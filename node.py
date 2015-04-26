#!/usr/bin/python
# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import datetime, timedelta
import heapq
from math import ceil, sqrt
import re
import select
import sys
from threading import Event, Thread, Timer

import config
from enum_type import MSG_TYPE, STATE
from message import Message
import utils


class ServerThread(Thread):

    def __init__(self, node):
        Thread.__init__(self)
        self._node = node

    def run(self):
        self._update()

    def _update(self):
        self._connection_list = []
        self._server_socket = utils.create_server_socket(
            config.NODE_PORT[self._node.node_id])
        self._connection_list.append(self._server_socket)
        while True:
            (read_sockets, write_sockets, error_sockets) = select.select(
                self._connection_list, [], [])
            for read_socket in read_sockets:
                if read_socket == self._server_socket:
                    (conn, addr) = read_socket.accept()
                    self._connection_list.append(conn)
                else:
                    try:
                        msg_stream = read_socket.recv(config.RECV_BUFFER)
                        msgs = re.findall(r'\{(.*?)\}', msg_stream)
                        for msg in msgs:
                            self._process_message(
                                Message.to_message('{{{msg_body}}}'.format(msg_body=msg)))
                    except:
                        read_socket.close()
                        self._connection_list.remove(read_socket)
                        continue
        self._server_socket.close()

    def _process_message(self, msg):
        if self._node.OPTION == 1:
            sys.stdout.write('{time} {thread_id} {src} {msg_type}\n'.format(
                time=utils.datetime_to_str(datetime.now()),
                thread_id=self._node.node_id, src=msg.src,
                msg_type=msg.msg_type.to_str()))

        self._node.lamport_ts = max(self._node.lamport_ts + 1, msg.ts)

        if msg.msg_type == MSG_TYPE.REQUEST:
            self._on_request(msg)
        elif msg.msg_type == MSG_TYPE.GRANT:
            self._on_grant(msg)
        elif msg.msg_type == MSG_TYPE.RELEASE:
            self._on_release(msg)
        elif msg.msg_type == MSG_TYPE.FAIL:
            self._on_fail(msg)
        elif msg.msg_type == MSG_TYPE.INQUIRE:
            self._onInquire(msg)
        elif msg.msg_type == MSG_TYPE.YIELD:
            self._on_yield(msg)

    def _on_request(self, request_msg):
        if self._node.state == STATE.HELD:
            heapq.heappush(self._node.request_queue, request_msg)
        else:
            if self._node.has_voted:
                heapq.heappush(self._node.request_queue, request_msg)
                response_msg = Message(src=self._node.node_id)
                if (request_msg < self._node.voted_request and 
                        not self._node.has_inquired):
                    response_msg.set_type(MSG_TYPE.INQUIRE)
                    response_msg.set_dest(self._node.voted_request.src)
                else:
                    response_msg.set_type(MSG_TYPE.FAIL)
                    response_msg.set_dest(request_msg.src)
                self._node.client.send_message(response_msg,
                        response_msg.dest)
            else:
                self._grant_request(request_msg)

    def _on_release(self, release_msg=None):
        self._node.has_inquired = False
        if self._node.request_queue:
            next_request = heapq.heappop(self._node.request_queue)
            self._grant_request(next_request)
        else:
            self._node.has_voted = False
            self._node.voted_request = None

    def _grant_request(self, request_msg):
        grant_msg = Message(msg_type=MSG_TYPE.GRANT,
            src=self._node.node_id,
            dest=request_msg.src)
        self._node.client.send_message(grant_msg, grant_msg.dest)
        self._node.has_voted = True
        self._node.voted_request = request_msg

    def _on_grant(self, grant_msg):
        # self._node.voting_set[grant_msg.src] = grant_msg
        self._node.num_votes_received += 1

    def _on_fail(self, fail_msg):
        # self._node.voting_set[fail_msg.src] = fail_msg
        pass

    def _on_inquire(self, inquire_msg):
        if self._node.state != STATE.HELD:
            # self._node.voting_set[inquire_msg.src] = None
            self._node.num_votes_received -= 1
            yield_msg = Message(msg_type=MSG_TYPE.YIELD,
                                src=self._node.node_id,
                                dest=inquire_msg.src)
            self._node.client.send_message(yield_msg, yield_msg.dest)

    def _on_yield(self, yield_msg):
        heapq.heappush(self._node.request_queue,
                       self._node.voted_request)
        self._on_release()


class ClientThread(Thread):

    def __init__(self, node):
        Thread.__init__(self)
        self._node = node
        self._client_sockets = [utils.create_client_socket() for i in
                                xrange(config.NUM_NODE)]

    def run(self):
        self._update()

    def _update(self):
        while True:
            self._node.signal_request_cs.wait()
            self._node.request_cs(datetime.now())
            self._node.signal_enter_cs.wait()
            self._node.enter_cs(datetime.now())
            self._node.signal_exit_cs.wait()
            self._node.exit_cs(datetime.now())

    def send_message(self, msg, dest, multicast=False):
        if not multicast:
            self._node.lamport_ts += 1
            msg.set_ts(self._node.lamport_ts)
        self._client_sockets[dest].sendall(msg.to_json())
        assert dest == msg.dest
        #self._node.MessageBuffer[dest].append([msg, datetime.now() + timedelta(0, config.DELAY[self._node.node_id][dest])])

    def multicast(self, msg, group):
        self._node.lamport_ts += 1
        msg.set_ts(self._node.lamport_ts)
        for dest in group:
            new_msg = deepcopy(msg)
            new_msg.set_dest(dest)
            assert new_msg.dest == dest
            assert new_msg.ts == msg.ts
            self.send_message(new_msg, dest, True)

    def build_connection(self, num_node):
        for i in xrange(num_node):
            self._client_sockets[i].connect(('localhost',
                    config.NODE_PORT[i]))


class DelayThread(Thread):

    def __init__(self, node):
        Thread.__init__(self)
        self._node = node

    def run(self):
        self._update()

    def _update(self):
        while True:
            curr_time = datetime.now()
            for i in xrange(config.NUM_NODE):
                while (self._node.MessageBuffer[i] and 
                        self._node.MessageBuffer[i][0][1] <= curr_time):
                    curr_msg = self._node.MessageBuffer[i][0][0]
                    assert curr_msg.src == self._node.node_id
                    assert curr_msg.dest == i
                    self._node.client._client_sockets[curr_msg.dest].sendall(
                        curr_msg.to_json())
                    self._node.MessageBuffer[i].pop(0)
            time.sleep(0.1)


class Node(object):

    CS_INT = None
    NEXT_REQ = None
    OPTION = None

    def __init__(self, node_id):
        self.node_id = node_id
        self.state = STATE.INIT

        self.lamport_ts = 0

        # for simulating delay channel debug use
        # self.Delay = DelayThread(self)
        # self.MessageBuffer = [[] for i in xrange(config.NUM_NODE)]
        
        # attributes as a voter (receive & process request)
        self.has_voted = False
        self.voted_request = None
        self.request_queue = []  # a priority queue (key = lamportTS, value = request)

        # attributess as a proposer (propose & send request)
        self.voting_set = self._create_voting_set()
        self.num_votes_received = 0
        self.has_inquired = False

        # threads
        self.server = ServerThread(self)
        self.server.daemon = True
        self.server.start()
        self.client = ClientThread(self)
        self.client.daemon = True

        # Event signals
        self.signal_request_cs = Event()
        self.signal_request_cs.set()
        self.signal_enter_cs = Event()
        self.signal_exit_cs = Event()

        # Timestamp for next expected request/exit
        self.time_request_cs = None
        self.time_exit_cs = None

    def _create_voting_set(self):
        voting_set = dict()
        mat_k = int(ceil(sqrt(config.NUM_NODE)))
        (row_id, col_id) = (int(self.node_id / mat_k), 
            int(self.node_id % mat_k))
        for i in xrange(mat_k):
            voting_set[mat_k * row_id + i] = None
            voting_set[col_id + mat_k * i] = None
        return voting_set

    def _reset_voting_set(self):
        for voter in self.voting_set:
            self.voting_set[voter] = None

    def request_cs(self, ts):
        self.state = STATE.REQUEST
        self.lamport_ts += 1
        request_msg = Message(msg_type=MSG_TYPE.REQUEST,
                              src=self.node_id)
        self.client.multicast(request_msg, self.voting_set.keys())
        self.signal_request_cs.clear()

    def enter_cs(self, ts):
        self.time_exit_cs = ts + timedelta(milliseconds=Node.CS_INT)
        self.state = STATE.HELD
        self.lamport_ts += 1
        sys.stdout.write('{time} {thread_id} {node_list}\n'.format(
            time=utils.datetime_to_str(ts),
            thread_id=self.node_id,
            node_list=self.voting_set.keys()))
        self.signal_enter_cs.clear()

    def exit_cs(self, ts):
        self.time_request_cs = ts + timedelta(milliseconds=Node.NEXT_REQ)
        self.state = STATE.RELEASE
        self.lamport_ts += 1
        self.num_votes_received = 0
        # self._reset_voting_set()

        release_msg = Message(msg_type=MSG_TYPE.RELEASE,
                              src=self.node_id)
        self.client.multicast(release_msg, self.voting_set.keys())
        self.signal_exit_cs.clear()

    def build_connection(self, num_node):
        self.client.build_connection(num_node)

    def _check(self):
        timer = Timer(0.001, self._check)
        timer.start()
        curr_time = datetime.now()
        if (self.state == STATE.RELEASE and 
                self.time_request_cs <= curr_time):
            if not self.signal_request_cs.is_set():
                self.signal_request_cs.set()
        elif (self.state == STATE.REQUEST and 
                self.num_votes_received == len(self.voting_set)):
            if not self.signal_enter_cs.is_set():
                self.signal_enter_cs.set()
        elif (self.state == STATE.HELD and 
                self.time_exit_cs <= curr_time):
            if not self.signal_exit_cs.is_set():
                self.signal_exit_cs.set()

    def run(self):
        self.client.start()
        self._check()
        # self.Delay.start()
