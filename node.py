from math import sqrt
from math import ceil
import socket
import select
import time
from threading import Thread

import config
from enum_type import STATE
from enum_type import MSG_TYPE
from message import Message

RECV_BUFFER = 4096
CS_INT = 5 
NEXT_REQ = 7
TOT_EXEC_TIME = 20
OPTION = 1

class ServerThread(Thread):
	def __init__(self, node):
		Thread.__init__(self)
		self._node = node
		self._connectionList = []
		self._serverSocket = ServerThread._createServerSocket(config.NODE_PORT[self._node.NodeID])
		self._connectionList.append(self._serverSocket)

	def run(self):
		self._update()

	def _update(self):
		while True:
			read_sockets,write_sockets,error_sockets = select.select(self._connectionList,[],[])
			for read_socket in read_sockets:
				if read_socket == self._serverSocket:
					conn, addr = read_socket.accept()
					self._connectionList.append(conn)
				else:
					try:
						msg = read_socket.recv(RECV_BUFFER)
						++self._node.LamportTS
						self._processMessage(msg)
					except:
						self._connectionList.remove(read_socket)
						read_socket.close()
			time.sleep(0.1)

	def _processMessage(self, msg):
		decoded_msg = Message.ToMessage(msg)
		print "I am {dest}. I receive {data} from {src}!".format(dest=decoded_msg.dest,data=decoded_msg.data,src=decoded_msg.src)
		msg_type = decoded_msg.msg_type
		if msg_type == MSG_TYPE.REQUEST:
			self._onRequest(decoded_msg)
		elif msg_type == MSG_TYPE.GRANT:
			self._onGrant(decoded_msg)
		elif msg_type == MSG_TYPE.RELEASE:
			self._onRelease(decoded_msg)
		elif msg_type == MSG_TYPE.FAIL:
			self._onFail(decoded_msg)
		elif msg_type == MSG_TYPE.INQUIRE:
			self._onInquire(decoded_msg)
		elif msg_type == MSG_TYPE.YIELD:
			self._onYield(decoded_msg)
		else:
			pass

	def _onRequest(self, request_msg):
		pass

	def _onRelease(self, release_msg):
		pass

	def _onGrant(self, grant_msg):
		pass

	def _onFail(self, fail_msg):
		pass

	def _onInquire(self, inquire_msg):
		pass

	def _onYield(self, yield_msg):
		pass

	@staticmethod
	def _createServerSocket(port):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(('0.0.0.0', port))
		s.listen(10)
		return s


class ClientThread(Thread):
	def __init__(self, node):
		Thread.__init__(self)
		self._node = node
		self._clientSockets = [ClientThread._createClientSocket() for i in xrange(config.NUM_NODE)]

	def run(self):
		self._update()

	def _update(self):
		for i in xrange(config.NUM_NODE):
			if i != self._node.NodeID:
				msg = Message(msg_type=MSG_TYPE.REQUEST, src=self._node.NodeID, dest=i, data="lalala").ToJSON()
				print "sent msg!"
				self._clientSockets[i].send(msg)

	def BuildConnection(self, num_node):
		for i in xrange(num_node):
			self._clientSockets[i].connect(('localhost', config.NODE_PORT[i]))
			print "{src} connects with {dest}!".format(src=self._node.NodeID, dest=i)

	@staticmethod
	def _createClientSocket():
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(2)
		return s


class Node(object):
	def __init__(self, node_id):
		self.NodeID = node_id
		self.State = STATE.INIT
		#init voting set
		self._timer = 0
		self.LamportTS = 0
		self._votingSet = self._createVotingSet()
		self._votedRequest = None
		self._hasVoted = False
		self._hasInquired = False
		self._receiveFail = False
		#self._requestQueue = None //should be a priority queue (key = lamportTS, value = request)

		self._serverThread = ServerThread(self)
		self._serverThread.start()
		self._clientThread = ClientThread(self)
		print "Init node {node_id} completed!".format(node_id=self.NodeID)

	def _createVotingSet(self):
		voting_set = dict()
		mat_k = int(ceil(sqrt(config.NUM_NODE)))
		row_id, col_id = int(self.NodeID / mat_k), int(self.NodeID % mat_k)
		for i in xrange(mat_k):
			voting_set[mat_k * row_id + i] = None
			voting_set[col_id + mat_k * i] = None
		return voting_set

	def _resetVotingSet(self):
		pass

	def Run(self):
		self._clientThread.BuildConnection(config.NUM_NODE)
		self._clientThread.start()
			