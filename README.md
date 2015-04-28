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
	*-cs_int (required): time a node spends in the critical section
	*-next_req (required): time a node waits after exiting the critical section before it requests another critical section entrance
	*-tot_exec_time (required): total execution time for a node
	*-option (optional): 1 means display message log on screen

Files
-----
*mutex.py: main program entrance
*maekawa.py: implements system setup
*node.py: implements node functionality
*enum_type.py: defines some enum types
*message.py: defines message format 
*config.py: program configuration (number of nodes, buffer size, port number)
*utils.py: implements utility functions
*logging.py: implements logging functions
*README.md: this file

Setup
-----
* Python version >= 2.7

Issues
-----
*Currently only works when the number of nodes is a perfect square (4, 9, 16,...)
