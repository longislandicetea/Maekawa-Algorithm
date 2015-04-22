import socket

#0 for millionseconds, 1 for seconds
def TimeElapsed(start_time, end_time, unit=0):
	diff = end_time - start_time
	if unit == 0:
		return int(round(diff * 1000))
	elif unit == 1:
		return int(round(diff))

def CreateServerSocket(port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(('0.0.0.0', port))
	s.listen(10)
	return s

def CreateClientSocket():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)
	return s
