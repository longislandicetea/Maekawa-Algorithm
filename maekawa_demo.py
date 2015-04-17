from node import Node

import config

def main():
	nodes = []
	n = config.NUM_NODE
	
	#create nodes
	for i in xrange(n):
		nodes.append(Node(i))

	#enable communication between nodes
	for i in xrange(n):
		nodes[i].BuildConnection(n)

	for i in xrange(n):
		nodes[i].Run()

if __name__ == '__main__':
	main()