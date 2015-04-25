#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
from threading import Thread
import time

from node import Node
import config

TOT_EXEC_TIME = 100


def create_arg_parse():
    parser = \
        argparse.ArgumentParser(decription='A distributed mutual exclusion program implemented with Maekawa algorithm'
                                )
    parser.add_argument(
        '-cs_int',
        action='store',
        dest='cs_int',
        help='time a node spends in the critical section',
        default=5,
        required=False,
        )
    parser.add_argument(
        '-next_req',
        action='store',
        dest='next_req',
        help='time a node waits after exiting the critical section before it requests another critical section entrance'
            ,
        default=7,
        required=False,
        )
    parser.add_argument(
        '-tot_exec_time',
        action='store',
        dest='tot_exec_time',
        help='total execution time for a node',
        default=7,
        required=False,
        )


def main():
    nodes = []
    n = config.NUM_NODE

    # create nodes

    for i in xrange(n):
        nodes.append(Node(i))

    # print "{num_node} nodes created!".format(num_node=config.NUM_NODE)

    # build communcation channels

    for i in xrange(n):
        nodes[i].BuildConnection(config.NUM_NODE)
    print '{num_node} nodes set up complete.'.format(num_node=config.NUM_NODE)

    # run nodes

    for i in xrange(n):
        nodes[i].Run()


if __name__ == '__main__':
    timer_thread = Thread(target=main)
    timer_thread.daemon = True
    timer_thread.start()
    time.sleep(TOT_EXEC_TIME + 1)

    # main()
