import datetime
import json
from json import JSONEncoder
import yaml

from enum_type import MSG_TYPE

class Message(object):
	def __init__(self, msg_type, src, dest, data):
		self.type = msg_type
		self.src = src
		self.dest = dest
		self.data = data

	def __json__(self):
		return dict (\
			type=self.type, \
			src=self.src, \
			dest=self.dest, \
			data=self.data,\
			)