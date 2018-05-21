#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import serial
from progress import progress
from time import sleep
import sys

def recv_data(handle):
    ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=100)
    ser.write(b"\xfa\x31\x30\x30\xfb")
    while True:
        data = ser.read(16)
        # print(len(data))
        if len(data) == 0: break
        handle(data)
    ser.close()

def send_data():
    ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=10)
    string = '\x40' * 95
    i = 0
    k = 0
    while True:
        i += 1
        s = string + format(i, '05d')
        k += len(s)
        progress(k)
        ser.write(s.encode())
        # if i == 100:
        #     sleep(100)
        sleep(0.1)
    ser.close()

def send_file():
    ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=10)
    file = open('/home/longzhou/Data/chaoyangxiyuan/2017-09-08/1504850902_left.dat', 'rb')
    size = 0
    while True:
        data = file.read(100)
        if len(data) == 0:
            break
        ser.write(data)
        size += len(data)
        progress(size)
        sleep(0.1)
    ser.close()
    print("done")


start = False
expect = 0
prog = 0

if __name__ == '__main__':
    send_data()

if __name__ == "__main__1":
    send_file()

if __name__ == '__main__1':
    np.set_printoptions(formatter={'int': hex})
    dt = np.dtype(np.uint8)
    f = open('data/out.dat', 'wb')
    def handle(data):
        global start, expect, prog
        array = np.fromstring(data, dtype=np.uint8)
        length = array.size
        if start:
            f.write(data)
            prog += length
            progress(prog)
            # if expect >= length:
            #     expect -= length
            # else:
            #     if expect < 0:
            #         i = -expect
            #         expect = 0
            #     else:
            #         i = 0
            #     while expect < length:
            #         while i < 8 and expect < length:
            #             if (i < 4 and array[expect] == 0xfb) or (i >= 4 and array[expect] == 0xff):
            #                 expect += 1
            #                 i += 1
            #             else:
            #                 print('*********error*********')
            #                 f.close()
            #                 sys.exit(1)
            #         if i < 8:
            #             expect = -i
            #             return
            #         else:
            #             expect += 940
            #     expect -= length
        else:
            i = 0
            while i < length:
                if array[i] == 0xfb:
                    expect += 1
                    if expect == 4:
                        start = True
                        if i < 3:
                            head = '\xfb' * (3 - i)
                            data = head + data
                        else:
                            data = data[i - 3 :]
                        expect = 0
                        handle(data)
                        return
                else:
                    expect = 0
                i += 1
    def handle1(data):
        # data = np.fromstring(data, dt)
        # print(data)
        global prog
        prog += len(data)
        progress(prog)
        f.write(data)
    recv_data(handle1)
    f.close()
