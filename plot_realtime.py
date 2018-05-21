#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import rfcomm_client_device
import thread

max_data = 3000

press = np.zeros([max_data,], dtype=np.uint8)
lock = thread.allocate()

fig, ax = plt.subplots()
line, = ax.plot(press)
line.set_xdata(range(max_data))
ax.set_xlim(0, max_data)
ax.set_ylim(0, 255)

def update(data):
    line.set_ydata(data)
    return line,

def data_gen():
    if lock.acquire():
        cur_data = np.copy(press)
        lock.release()
        yield cur_data

def handle(data):
    global press
    cur_data = np.fromstring(data, dtype=np.uint8)
    cur_len = len(cur_data)
    if lock.acquire():
        if cur_len > max_data:
            press = cur_data[-max_data:]
        else:
            press = np.append(press[cur_len - max_data:], cur_data)
        lock.release()

def connect():
    rfcomm_client_device.recv_data(handle)

thread.start_new(connect, ())

ani = animation.FuncAnimation(fig, update, data_gen, interval=100)
plt.show()
