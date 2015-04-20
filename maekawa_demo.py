from node import Node

import config

def main():
	nodes = []
	n = config.NUM_NODE
	
	#create nodes
	for i in xrange(n):
		nodes.append(Node(i))
	print "{num_node} nodes created!".format(num_node=config.NUM_NODE)

	for i in xrange(n):
		nodes[i].Run()

if __name__ == '__main__':
	main()