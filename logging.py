#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Hao Luo

from datetime import datetime
import sys

from message import Message
import utils


def log_receive_message(msg):
	sys.stdout.write('{time} {thread_id} {src} {msg_type}\n'.format(
		time=utils.datetime_to_str(datetime.now()),
		thread_id=msg.dest, 
		src=msg.src,
		msg_type=msg.msg_type.to_str(),
		))

def log_enter_cs(ts, node_id, node_list):
	sys.stdout.write('{time} {thread_id} {node_list}\n'.format(
		time=utils.datetime_to_str(ts),
        thread_id=node_id,
        node_list=node_list,
        ))

def log_receive_message_debug(msg, ts):
	sys.stdout.write("{time} {dest} {src} {msg_type} {msg_ts} {self_ts}\n".format(
		time=utils.datetime_to_str(datetime.now()),
		dest=msg.dest,
        src=msg.src,
        msg_type=msg.msg_type.to_str(),
        msg_ts=msg.ts,
        self_ts=ts,
        ))
