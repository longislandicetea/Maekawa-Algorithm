from enum import Enum
import socket
import select
import time
from threading import Thread

import config

RECV_BUFFER = 4096

class STATE(Enum):
	INIT = 0
	REQUEST = 1
	HELD = 2
	RELEASE = 3

class Node(object):
	def __init__(self, node_id):
		self.NodeID = node_id
		self.State = STATE.INIT

		#create server socket
		self._connectionList = []
		self._serverSocket = Node._createServerSocket(config.NODE_PORT[self.NodeID])
		self._connectionList.append(self._serverSocket)
		self._serverThread = Thread(target=self._run_server)
		self._serverThread.start()

		#create client socket
		self._clientSockets = [Node._createClientSocket() for i in xrange(config.NUM_NODE)]

		#init voting set
		self._votingSet = dict()
		print "Init node {node_id}!".format(node_id=self.NodeID)

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

	def Run(self):
		self._clientThread = Thread(target=self._run_client)
		self._clientThread.start()

	def _run_server(self):
		while True:
			read_sockets,write_sockets,error_sockets = select.select(self._connectionList,[],[])
			for read_socket in read_sockets:
				if read_socket == self._serverSocket:
					conn, addr = read_socket.accept()
					self._connectionList.append(conn)
				else:
					try:
						msg = read_socket.recv(RECV_BUFFER)
						print "I am {node}. I receive {msg} !".format(node=self.NodeID, msg=msg)
					except:
						self._connectionList.remove(read_socket)
						read_socket.close()
			time.sleep(0.1)

	def _run_client(self):
		for i in xrange(config.NUM_NODE):
			if i != self.NodeID:
				msg = "Hi {dest}! I am {src}.".format(dest=i, src=self.NodeID)
				print msg
				self._clientSockets[i].send(msg)			

	def _run_check(self):
		pass
