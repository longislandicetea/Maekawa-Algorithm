from threading import Thread
import time

from node import Node
import config

import stacktracer

TOT_EXEC_TIME = 100

def main():
	nodes = []
	n = config.NUM_NODE
	
	#create nodes
	for i in xrange(n):
		nodes.append(Node(i))
	print "{num_node} nodes created!".format(num_node=config.NUM_NODE)

	#build communcation channels
	for i in xrange(n):
		nodes[i].BuildConnection(config.NUM_NODE)
	
	#run nodes
	for i in xrange(n):
		nodes[i].Run()

if __name__ == '__main__':
	'''stacktracer.trace_start("trace.html",interval=5,auto=True)
	timer_thread = Thread(target=main)
	timer_thread.daemon = True
	timer_thread.start()
	time.sleep(TOT_EXEC_TIME + 1)
	stacktracer.trace_stop()'''
	main()