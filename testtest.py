from message import Message
from enum_type import MSG_TYPE
import copy
import heapq
import time

import datetime
from utils import DatetimeToStr

'''t1 = datetime.datetime.now()
t3 = time.time()
print t1, DatetimeToStr(t1)
print t3
print t1.hour, t1.second, t1.microsecond
t2 = t1 + datetime.timedelta(microseconds=5 * 1000)
print t2, DatetimeToStr(t2)'''

t1 = time.time()
time.sleep(0.005)
t2 = time.time()
print int(round(t1 * 1000))
print int(round(t2 * 1000))

def testloop():
	x = 1
	cnt = 0
	while True:
		print datetime.datetime.now(), DatetimeToStr(datetime.datetime.now())
		if cnt > 3:
			break
		if x > 1:
			x = 0
		elif x <= 1 and x >= 0:
			x = -1
		else:
			x = 1
		cnt += 1

testloop()