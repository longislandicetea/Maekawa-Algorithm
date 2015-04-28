"""program configuration

NUM_NODE: number of nodes
INIT_PORT: port number of the first node
		   (I assuem node ports are consecutive, you could 
		   	certainly choose whatever ports you like)
RECV_BUFFER: socket buffer size when receiving messages

"""


NUM_NODE = 9
INIT_PORT = 3000
NODE_PORT = [(INIT_PORT + i) for i in xrange(NUM_NODE)]
RECV_BUFFER = 4096