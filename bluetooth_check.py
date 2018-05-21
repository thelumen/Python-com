#!/usr/bin/env python

from serial_cp2102 import recv_data

if __name__ == '__main__':
    f = open('out.txt', 'wb')
    def handle(data):
        f.write(data)
    recv_data(handle)
    f.close()
