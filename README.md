Maekawa Distributed Mutual Exclusion
====================================
A distributed mutual exclusion program implemented with Maekawa Algorithm

Author: Hao Luo (yvetterowe1116@gmail.com)

Usage
-----
```bash
$> python mutex.py -cs_int 5 -next_req 7 -tot_exec_time 15 -option 1
```

Arguments:
* `cs_int` (required): time (milliseconds) a node spends in the critical section
* `next_req` (required): time (milliseconds) a node waits after exiting the critical section before it requests another critical section entrance
* `tot_exec_time` (required): total execution time (seconds) for a node
* `option` (optional): 1 means display message log on screen

Outputs:
* Each node prints to the screen the following log whenever it enters the critical section (regardless of the `option` value):
	
	```bash
	$> Time Node_ID Node_List
	```
	* `Time`: system time at which the node enters the critical section
	* `Node_ID`: identifier of the node entering the critical section
	* `Node_List`: set of node identifiers from whom this node has obtained permission to enter the critical section

* Additionally, when `option` is specified as 1, each node should also print to the screen a log whenever it receives a message from another node:
	
	```bash
	$> Time Node_ID Sender_ID Message_Type
	```
	* `Time`: systime time at which the log is printed
	* `Node_ID`: identifier of the node printing the log
	* `Sender_ID`: identifier of the node that sent the message
	* `Message_Type`: type of the received message

Files
-----
* mutex.py: main program entrance
* maekawa.py: implements system setup
* node.py: implements node functionality
* enum_type.py: defines some enum types
* message.py: defines message format 
* config.py: program configuration (number of nodes, buffer size, port number)
* utils.py: implements utility functions
* logging.py: implements logging functions
* README.md: this file

Setup
-----
* Python version >= 2.7

Issues
-----
* Currently only works when the number of nodes is a perfect square (4, 9, 16,...)
