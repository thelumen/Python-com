#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from time import sleep

file = open('data/out.imu', 'rb')
last = None

def recv_data(handle):
    global last
    while True:
        data = file.read(1024 * 4)
        length = len(data)
        if length == 0:
            break
        if last is not None:
            data = last + data
            length = len(data)
            last = None
        i = 0
        while i + 12 <= length:
            handle(data[i : i + 12])
            i += 12
            sleep(0.02)
        if i < length:
            last = data[i :]

if __name__ == '__main__':
    import numpy as np
    def handle(data):
        data = np.fromstring(data, dtype=np.uint8)
        data = np.array(np.frombuffer(data, dtype=np.int16), dtype=np.float32)
        print(data)
    recv_data(handle)
