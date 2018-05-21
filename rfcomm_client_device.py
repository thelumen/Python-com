#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bluetooth import *
import bluetooth._bluetooth as bt   # low level bluetooth wrappers.
from progress import progress
import time

def recv_data(handle):
    timeout = 1000
    # bt_addr = '1E:03:E0:81:03:44'
    # bt_addr = '1E:03:E0:81:0A:F8'
    bt_addr = '1E:03:E0:81:39:CB'

    # Create the client socket
    sock = BluetoothSocket(RFCOMM)

    print("trying to connect to %s:1001" % bt_addr)
    port = 0x1001
    sock.connect((bt_addr, port))

    print("connected. Adjusting link parameters.")
    print("current flush timeout is %d ms" % read_flush_timeout(bt_addr))
    try:
        write_flush_timeout(bt_addr, timeout)
    except bt.error as e:
        print("error setting flush timeout.  are you sure you're superuser?")
        print(e)
        sys.exit(1)
    print("new flush timeout is %d ms" % read_flush_timeout(bt_addr))

    try:
        sock.send(b'\xfa\x31\x30\x30\xfb')
        try:
            while True:
                # sock.send(b'\xfa\x31\x30\x30\xf7')
                data = sock.recv(1024)
                if len(data) == 0: break
                handle(data)
                # time.sleep(1)
        except KeyboardInterrupt:
            sock.send(b'\xfa\x32\x30\x30\xfb')
            pass
    except IOError:
        pass
    print("disconnected")

    sock.close()
    print("all done")

start = False
expect = 0
i = 0
prog = 0

if __name__ == '__main__':
    # data = b'\xfc\xfd\xfe\xff\x00\x01\x02\x03'
    import numpy as np
    f = open('data/out.dat', 'wb')
    def handle(data):
        global start, expect, i, prog
        array = np.fromstring(data, dtype=np.uint8)
        length = array.size
        if start:
            f.write(data)
            prog += length
            progress(prog)
            while expect < length:
                while i < 8 and expect < length:
                    if array[expect] == 0xfb if i < 4 else array[expect] == 0xff:
                        expect += 1
                        i += 1
                    else:
                        print('*********error*********')
                        f.close()
                        sys.exit(1)
                if i < 8:
                    expect = 0
                    return
                else:
                    i = 0
                    expect += 500
            expect -= length
        else:
            i = 0
            while i < length:
                if array[i] == 0xfb:
                    expect += 1
                    if expect == 4:
                        start = True
                        expect = 0
                        i += 1
                        if i < length:
                            data = data[i :]
                            i = 4
                            handle(data)
                        i = 4
                        return
                else:
                    expect = 0
                i += 1
    def handle1(data):
        global prog
        prog += len(data)
        progress(prog)
        f.write(data)
    def handle2(data):
        print(len(data), data)
    recv_data(handle)
    f.close()
