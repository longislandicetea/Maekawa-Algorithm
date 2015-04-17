import datetime
import json
from json import JSONEncoder
from json import JSONDecoder
import yaml

from enum_type import MSG_TYPE

class MessageEncoder(JSONEncoder):
	def default(self, obj):
		return obj.__json__()

class Message(object):
	def __init__(self, msg_type, src, dest, data):
		self.msg_type = msg_type
		self.src = src
		self.dest = dest
		self.data = data

	def __json__(self):
		return dict(msg_type=self.msg_type, src=self.src, dest=self.dest, data=self.data)

	def ToJSON(self):
		return json.dumps(self, cls=MessageEncoder)