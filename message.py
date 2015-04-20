import json
from json import JSONEncoder
from json import JSONDecoder

from enum_type import MSG_TYPE

class MessageEncoder(JSONEncoder):
	def encode(self, obj):
		obj_dict = dict()
		obj_dict['msg_type'] = int(obj.msg_type)
		obj_dict['src'] = obj.src
		obj_dict['dest'] = obj.dest
		obj_dict['data'] = obj.data
		return super(MessageEncoder, self).encode(obj_dict)

class MessageDecoder(JSONDecoder):
	def decode(self, json_string):
		parsed_dict = super(MessageDecoder, self).decode(json_string)
		return Message(
			MSG_TYPE(parsed_dict['msg_type']),
			parsed_dict['src'],
			parsed_dict['dest'],
			parsed_dict['data'],
			)

class Message(object):
	def __init__(self, msg_type, src, dest, data):
		self.msg_type = msg_type
		self.src = src
		self.dest = dest
		self.data = data

	def __json__(self):
		return dict(
			msg_type=self.msg_type, 
			src=self.src, 
			dest=self.dest, 
			data=self.data,
			)

	def ToJSON(self):
		return json.dumps(self, cls=MessageEncoder)

	@staticmethod
	def ToMessage(json_str):
		return json.loads(json_str, cls=MessageDecoder)
