from math import sqrt
from math import ceil
import socket
import select
import time
from threading import Thread
import yaml

import config
from enum_type import STATE
from enum_type import MSG_TYPE
from message import Message

RECV_BUFFER = 4096
CS_INT = 5 
NEXT_REQ = 7
TOT_EXEC_TIME = 20
OPTION = 1

class Node(object):
	def __init__(self, node_id):
		self.NodeID = node_id
		self.State = STATE.INIT

		#create server socket
		self._connectionList = []
		self._serverSocket = Node._createServerSocket(config.NODE_PORT[self.NodeID])
		self._connectionList.append(self._serverSocket)
		self._serverThread = Thread(target=self._runServer)
		self._serverThread.start()

		#create client socket
		self._clientSockets = [Node._createClientSocket() for i in xrange(config.NUM_NODE)]

		#init voting set
		self._votingSet = self._createVotingSet()
		print self._votingSet
		print "Init node {node_id}!".format(node_id=self.NodeID)

	"""socket related"""
	"""
		*****************************************************************************
	"""
	@staticmethod
	def _createServerSocket(port):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(('0.0.0.0', port))
		s.listen(10)
		return s

	@staticmethod
	def _createClientSocket():
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(2)
		return s

	def BuildConnection(self, num_node):
		for i in xrange(num_node):
			self._clientSockets[i].connect(('localhost', config.NODE_PORT[i]))
			print "{src} connects with {dest}!".format(src=self.NodeID, dest=i)
	"""
		*****************************************************************************
	"""

	def _createVotingSet(self):
		voting_set = dict()
		mat_k = int(ceil(sqrt(config.NUM_NODE)))
		row_id, col_id = int(self.NodeID / mat_k), int(self.NodeID % mat_k)
		for i in xrange(mat_k):
			voting_set[mat_k * row_id + i] = False
			voting_set[col_id + mat_k * i] = False
		return voting_set

	def Run(self):
		self._clientThread = Thread(target=self._runClient)
		self._clientThread.start()

	def _runServer(self):
		while True:
			read_sockets,write_sockets,error_sockets = select.select(self._connectionList,[],[])
			for read_socket in read_sockets:
				if read_socket == self._serverSocket:
					conn, addr = read_socket.accept()
					self._connectionList.append(conn)
				else:
					try:
						msg = read_socket.recv(RECV_BUFFER)
						self._processMessage(msg)
					except:
						self._connectionList.remove(read_socket)
						read_socket.close()
			time.sleep(0.1)

	def _processMessage(self, msg):
		decoded_msg = yaml.load(msg)
		print "I am {dest}. I receive {data} from {src}!".format(dest=decoded_msg['dest'],data=decoded_msg['data'],src=decoded_msg['src'])
		msg_type = decoded_msg['msg_type']
		if msg_type == "MSG_TYPE.REQUEST":
			pass
		elif msg_type == "MSG_TYPE.GRANT":
			pass
		elif msg_type == "MSG_TYPE.RELEASE":
			pass
		elif msg_type == "MSG_TYPE.FAIL":
			pass
		elif msg_type == "MSG_TYPE.INQUIRE":
			pass
		elif msg_type == "MSG_TYPE.YIELD":
			pass
		else:
			pass

	def _runClient(self):
		for i in xrange(config.NUM_NODE):
			if i != self.NodeID:
				msg = Message(msg_type=MSG_TYPE.REQUEST, src=self.NodeID, dest=i, data="lalala").ToJSON()
				self._clientSockets[i].send(msg)			

	def _run_check(self):
		pass
