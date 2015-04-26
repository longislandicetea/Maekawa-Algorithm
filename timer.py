from threading import Thread
import time

class Timer(thread):
	def __init__(self, event, start_time, elapse_time):
		self._start_time = start_time
		self._elapse_time = elapse_time
		self._event = event

	def run(self):
		while True:
			curr_time = time.time()
			if curr_time - self._start_time >= self._elapse_time:
				self._event.set()
				break