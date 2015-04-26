#!/usr/bin/python
# -*- coding: utf-8 -*-

import config
from node import Node


class MaekawaMutex(object):

    def __init__(
        self,
        cs_int,
        next_req,
        option,
        ):

        Node.CS_INT = cs_int
        Node.NEXT_REQ = next_req
        Node.OPTION = option
        self._nodes = [Node(i) for i in xrange(config.NUM_NODE)]

    def _build_connection(self):
        for node in self._nodes:
            node.build_connection(config.NUM_NODE)

            # print node.NodeID, node.CS_INT, node.NEXT_REQ

    def run(self):

        # print "hello world!"

        self._build_connection()

        # cnt = 0

        for node in self._nodes:

            # sys.stdout.write("{id} {tid}\n".format(id=cnt, tid=))

            node.run()
