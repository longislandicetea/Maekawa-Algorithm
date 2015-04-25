#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket


# 0 for millionseconds, 1 for seconds

def TimeElapsed(start_time, end_time, unit=0):
    delta = end_time - start_time
    if unit == 0:
        return int(round(delta.microseconds / 1000.0))
    elif unit == 1:
        return int(delta.seconds)


def DatetimeToStr(time):
    return '{hour}:{min}:{second}:{millisecond}'.format(hour=time.hour,
            min=time.minute, second=time.second,
            millisecond=str(int(round(time.microsecond / 1000.0))))


def CreateServerSocket(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', port))
    s.listen(5)
    return s


def CreateClientSocket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    return s
