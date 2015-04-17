from enum import Enum

class STATE(Enum):
	INIT = 0
	REQUEST = 1
	HELD = 2
	RELEASE = 3