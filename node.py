from copy import deepcopy
import datetime
#from datetime import datetime
import heapq
from math import sqrt
from math import ceil
import re
import select
import sys
import time
import threading
from threading import Thread

import config
from enum_type import STATE
from enum_type import MSG_TYPE
from message import Message
import utils

global CS_INT, NEXT_REQ, TOT_EXEC_TIME, OPTION

RECV_BUFFER = 4096
CS_INT = 2
NEXT_REQ = 5
TOT_EXEC_TIME = 20
OPTION = 1

class ServerThread(Thread):
	def __init__(self, node):
		Thread.__init__(self)
		self._node = node

	def run(self):
		self._update()

	def _update(self):
		self._connectionList = []
		self._serverSocket = utils.CreateServerSocket(config.NODE_PORT[self._node.NodeID])
		self._connectionList.append(self._serverSocket)
		while True:
			read_sockets,write_sockets,error_sockets = select.select(self._connectionList,[],[])
			for read_socket in read_sockets:
				if read_socket == self._serverSocket:
					conn, addr = read_socket.accept()
					self._connectionList.append(conn)
				else:
					try:
						msg_stream = read_socket.recv(RECV_BUFFER)
						msgs = re.findall(r'\{(.*?)\}', msg_stream)
						for msg in msgs:
							'''sys.stdout.write("{i}: receiving {msg} at {time}\n".format(
								i=self._node.NodeID, 
								msg=msg, 
								time=utils.DatetimeToStr(datetime.datetime.now()),
								))'''
							self._processMessage(Message.ToMessage("{{{msg_body}}}".format(msg_body=msg)))
					except:
						read_socket.close()
						self._connectionList.remove(read_socket)
						continue
		self._serverSocket.close()

	def _processMessage(self, msg):
		self._node.LamportTS = max(self._node.LamportTS + 1, msg.ts)
		if msg.msg_type == MSG_TYPE.REQUEST:
			self._onRequest(msg)
		elif msg.msg_type == MSG_TYPE.GRANT:
			self._onGrant(msg)
		elif msg.msg_type == MSG_TYPE.RELEASE:
			self._onRelease(msg)
		elif msg.msg_type == MSG_TYPE.FAIL:
			self._onFail(msg)
		elif msg.msg_type == MSG_TYPE.INQUIRE:
			self._onInquire(msg)
		elif msg.msg_type == MSG_TYPE.YIELD:
			self._onYield(msg)

	def _onRequest(self, request_msg):
		'''sys.stdout.write("{i}: receive request from {sender}. my state: {state}. has voted {voted}\n".format(
			i=self._node.NodeID,
			sender=request_msg.src,
			state=self._node.State,
			voted=self._node.HasVoted))'''
		if self._node.State == STATE.HELD:
			heapq.heappush(self._node.RequestQueue, request_msg)
		else:
			if self._node.HasVoted:
				heapq.heappush(self._node.RequestQueue, request_msg)
				response_msg = Message(src=self._node.NodeID)
				if request_msg < self._node.VotedRequest and not self._node.HasInquired:
					response_msg.SetType(MSG_TYPE.INQUIRE)
					response_msg.SetDest(self._node.VotedRequest.src)
				else:
					response_msg.SetType(MSG_TYPE.FAIL)
					response_msg.SetDest(request_msg.src)
				self._node.Client.SendMessage(response_msg, response_msg.dest)
			else:
				self._grantRequest(request_msg)

	def _onRelease(self, release_msg=None):
		#sys.stdout.write("{i} receives release from {r}\n".format(i=self._node.NodeID, r=release_msg.src))
		self._node.HasInquired = False
		if self._node.RequestQueue:
			next_request = heapq.heappop(self._node.RequestQueue)
			self._grantRequest(next_request)
		else:
			self._node.HasVoted = False
			self._node.VotedRequest = None

	def _grantRequest(self, request_msg):
		grant_msg = Message(
			msg_type=MSG_TYPE.GRANT,
			src=self._node.NodeID,
			dest=request_msg.src,
			)
		self._node.Client.SendMessage(grant_msg, grant_msg.dest)
		self._node.HasVoted = True
		self._node.VotedRequest = request_msg

	def _onGrant(self, grant_msg):
		#self._node.VotingSet[grant_msg.src] = grant_msg
		self._node.NumVotesReceived += 1

	def _onFail(self, fail_msg):
		#self._node.VotingSet[fail_msg.src] = fail_msg
		pass

	def _onInquire(self, inquire_msg):
		if self._node.State != STATE.HELD:
			#self._node.VotingSet[inquire_msg.src] = None
			self._node.NumVotesReceived -= 1 #!!!!!
			yield_msg = Message(
				msg_type=MSG_TYPE.YIELD,
				src=self._node.NodeID,
				dest=inquire_msg.src,
				)
			self._node.Client.SendMessage(yield_msg, yield_msg.dest)

	def _onYield(self, yield_msg):
		heapq.heappush(self._node.RequestQueue, 
			self._node.VotedRequest)
		self._onRelease()


class ClientThread(Thread):
	def __init__(self, node):
		Thread.__init__(self)
		self._node = node
		self._clientSockets = [utils.CreateClientSocket() for i in xrange(config.NUM_NODE)]

	def run(self):
		self._update()

	def _update(self):
		self._node.TrueTimeReuqestCS = datetime.datetime.now()
		while True:
			#curr_time = datetime.datetime.now()
			self._node.SignalRequestCS.wait()
			self._node.RequestCS(datetime.datetime.now())
			self._node.SignalEnterCS.wait()
			self._node.EnterCS(datetime.datetime.now())
			self._node.SignalExitCS.wait()
			#sys.stdout.write("{i}: client: {t}\n".format(i=self._node.NodeID, t=utils.DatetimeToStr(datetime.datetime.now())))
			self._node.ExitCS(datetime.datetime.now())

	def SendMessage(self, msg, dest, multicast=False):
		'''sys.stdout.write("{src}: sending {msg} to {dest}\n".format(
			src=self._node.NodeID,
			msg=msg.msg_type.ToStr(), 
			dest=dest,
			))'''
		#sys.stdout.write("{i}: sending {msg}\n".format(i=self._node.NodeID, msg=msg.ToJSON()))
		#assert msg.dest == dest
		if not multicast:
			self._node.LamportTS += 1
			msg.SetTS(self._node.LamportTS)
		self._clientSockets[dest].sendall(msg.ToJSON())
		'''sys.stdout.write("{i}: adding {msg} to queue {qid}!\n".format(
			i=self._node.NodeID,
			msg=msg.ToJSON(),
			qid=dest,
			))'''
		#assert dest == msg.dest
		#self._node.MessageBuffer[dest].append([msg, datetime.datetime.now() + datetime.timedelta(0, config.DELAY[self._node.NodeID][dest])])

	def Multicast(self, msg, group):
		#sys.stdout.write("multicast: {group}\n".format(group=group))
		self._node.LamportTS += 1
		msg.SetTS(self._node.LamportTS)
		for dest in group:
			new_msg = deepcopy(msg)
			new_msg.SetDest(dest)
			assert new_msg.dest == dest
			assert new_msg.ts == msg.ts
			self.SendMessage(new_msg, dest, True)

	def BuildConnection(self, num_node):
		for i in xrange(num_node):
			self._clientSockets[i].connect(('localhost', config.NODE_PORT[i]))


class CheckerThread(Thread):
	def __init__(self, node):
		Thread.__init__(self)
		self._node = node

	def run(self):
		self._update()
	
	def _update(self):
		while True:
			curr_time = datetime.datetime.now()
			if self._node.State == STATE.RELEASE and self._node.TimeRequestCS <= curr_time:
				if not self._node.SignalRequestCS.is_set():
					#self._node.TrueTimeReuqestCS = curr_time
					self._node.SignalRequestCS.set()
			elif self._node.State == STATE.REQUEST and self._node.NumVotesReceived == len(self._node.VotingSet):
				if not self._node.SignalEnterCS.is_set():
					#self._node.TrueTimeEnterCS = curr_time
					self._node.SignalEnterCS.set()
			elif self._node.State == STATE.HELD and self._node.TimeExitCS <= curr_time:
				if not self._node.SignalExitCS.is_set():
					#self._node.TrueTimeExitCS = curr_time
					self._node.SignalExitCS.set()
					#sys.stdout.write("{i}: checker: {t}\n".format(i=self._node.NodeID, t=utils.DatetimeToStr(curr_time)))
			time.sleep(0.001)


'''This thread simulates commnucation channel delay, 
 used for debug only'''
class DelayThread(Thread):
	def __init__(self, node):
		Thread.__init__(self)
		self._node = node

	def run(self):
		self._update()

	def _update(self):
		while True:
			curr_time = datetime.datetime.now()
			for i in xrange(config.NUM_NODE):
				while self._node.MessageBuffer[i] and self._node.MessageBuffer[i][0][1] <= curr_time:
				 	curr_msg = self._node.MessageBuffer[i][0][0]
				 	assert curr_msg.src == self._node.NodeID
				 	assert curr_msg.dest == i
					self._node.Client._clientSockets[curr_msg.dest].sendall(curr_msg.ToJSON())
					self._node.MessageBuffer[i].pop(0)
			time.sleep(0.1)


class Node(object):
	def __init__(self, node_id):
		self.NodeID = node_id
		self.State = STATE.INIT
		
		self.LamportTS = 0
		
		#for simulating delay channel debug use
		#self.MessageBuffer = [[] for i in xrange(config.NUM_NODE)]

		#attributes as a voter (receive & process request)
		self.HasVoted = False
		self.VotedRequest = None
		self.RequestQueue = [] #a priority queue (key = lamportTS, value = request)

		#attributess as a proposer (propose & send request)
		self.VotingSet = self._createVotingSet()
		self.NumVotesReceived = 0	
		self.HasInquired = False

		self.Server = ServerThread(self)
		self.Server.start()
		self.Client = ClientThread(self)
		self.Checker = CheckerThread(self)
		self.Delay = DelayThread(self)

		#Event signals
		self.SignalRequestCS = threading.Event()
		self.SignalRequestCS.set()
		self.SignalEnterCS = threading.Event()
		self.SignalExitCS = threading.Event()

		#Timestamp for next expected request/exit
		self.TimeRequestCS = None
		self.TimeExitCS = None

		#self.TrueTimeRequestCS = None
		#self.TrueTimeEnterCS = None
		#self.TrueTimeExitCS = None

	def _createVotingSet(self):
		voting_set = dict()
		mat_k = int(ceil(sqrt(config.NUM_NODE)))
		row_id, col_id = int(self.NodeID / mat_k), int(self.NodeID % mat_k)
		for i in xrange(mat_k):
			voting_set[mat_k * row_id + i] = None
			voting_set[col_id + mat_k * i] = None
		return voting_set
		'''if self.NodeID == 0:
			return {0:None, 1:None, 2:None}
		elif self.NodeID == 1:
			return {0:None, 1:None, 2:None}
		elif self.NodeID == 2:
			return {0:None, 3:None, 2:None}
		elif self.NodeID == 3:
			return {1:None, 3:None, 2:None}'''

	def _resetVotingSet(self):
		for voter in self.VotingSet:
			self.VotingSet[voter] = None

	def RequestCS(self, ts):
		self.State = STATE.REQUEST
		self.LamportTS += 1
		'''sys.stdout.write("{src}: reque CS at {t}\n".format(
			src=self.NodeID, 
			t=utils.DatetimeToStr(ts),
			))'''
		request_msg = Message(
			msg_type=MSG_TYPE.REQUEST,
			src=self.NodeID,
			#ts=self.LamportTS,
			)
		self.Client.Multicast(request_msg, self.VotingSet.keys())
		self.SignalRequestCS.clear()

	def EnterCS(self, ts):
		self.TimeExitCS = ts + datetime.timedelta(seconds=CS_INT)
		self.State = STATE.HELD
		self.LamportTS += 1
		sys.stdout.write("{src}: enter CS at {t}\n".format(
			src=self.NodeID, 
			t=utils.DatetimeToStr(ts),
			))
		'''sys.stdout.write("{time} {node_id}, {node_list}\n".format(
			time=datetime.now().time(),
			node_id=self.NodeID,
			node_list=self.VotingSet.keys()))'''
		self.SignalEnterCS.clear()

	def ExitCS(self, ts):
		self.TimeRequestCS = ts + datetime.timedelta(seconds=NEXT_REQ)
		self.State = STATE.RELEASE
		self.LamportTS += 1
		self.NumVotesReceived = 0
		#self._resetVotingSet()
		sys.stdout.write("{src}: exite CS at {t}\n".format(
			src=self.NodeID,
			t=utils.DatetimeToStr(ts),
			))
		release_msg = Message(
			msg_type=MSG_TYPE.RELEASE,
			src=self.NodeID,
			#ts=self.LamportTS,
			)
		self.Client.Multicast(release_msg, self.VotingSet.keys())
		self.SignalExitCS.clear()

	def BuildConnection(self, num_node):
		self.Client.BuildConnection(num_node)

	def _check(self):
		threading.Timer(0.001, self._check).start()
		curr_time = datetime.datetime.now()
		if self.State == STATE.RELEASE and self.TimeRequestCS <= curr_time:
			if not self.SignalRequestCS.is_set():
				#self._node.TrueTimeReuqestCS = curr_time
				self.SignalRequestCS.set()
		elif self.State == STATE.REQUEST and self.NumVotesReceived == len(self.VotingSet):
			if not self.SignalEnterCS.is_set():
				#self._node.TrueTimeEnterCS = curr_time
				self.SignalEnterCS.set()
		elif self.State == STATE.HELD and self.TimeExitCS <= curr_time:
			if not self.SignalExitCS.is_set():
				#self._node.TrueTimeExitCS = curr_time
				self.SignalExitCS.set()
			#sys.stdout.write("")

	def Run(self):
		self.Client.start()
		self._check()
		#self.Checker.start()
		#self.Delay.start()
			