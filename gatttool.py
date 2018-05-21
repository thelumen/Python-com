#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
http://shaocheng.li/post/blog/2016-04-05
hcitool dev
sudo hcitool lescan
D1:72:EA:57:91:10
D8:B0:4C:DC:7A:84
gatttool -b  -t random -I
connect
mtu 512
primary
characteristics
char-write-req 0x0013 0100
char-write-cmd 0x0010 fa313030fb

primary 0003cdd0-0000-1000-8000-00805f9b0131
characteristics 0x000e 0xffff

handle: 0x000f, char properties: 0x08, char value handle: 0x0010, uuid: 0003cdd2-0000-1000-8000-00805f9b0131
handle: 0x0011, char properties: 0x12, char value handle: 0x0012, uuid: 0003cdd1-0000-1000-8000-00805f9b0131

gatttool -b D1:72:EA:57:91:10 --char-write-req --handle=0x0013 --value=0100 --listen
'''

import pexpect

class Ble:
    def __init__(self, bluetooth_address):
        self.callbacks = None
        self.conn = pexpect.spawn('gatttool -b ' + bluetooth_address + ' -t random --interactive')
        self.conn.expect('\[' + bluetooth_address + '\]\[LE\]>', timeout = 10)
        print("Preparing to connect.")
        self.conn.sendline('connect')
        self.conn.expect('Attempting to connect to ' + bluetooth_address, timeout = 5)
        self.conn.expect('Connection successful', timeout = 5)
        self.callbacks = {}
        print('connect successful.')

    def __del__(self):
        if self.callbacks:
            self.char_write_cmd(0x0010, 'fa323030fb')
            self.conn.sendline('disconncet')
        self.conn.sendline('exit')
        print("exiting..")

    def mtu(self, value):
        cmd = 'mtu %d' % value
        print(cmd)
        self.conn.sendline(cmd)
        self.conn.expect('MTU was exchanged successfully: %d' % value)

    def char_write_cmd(self, handle, value):
        cmd = 'char-write-cmd 0x%04x %s' % (handle, value)
        print(cmd)
        self.conn.sendline(cmd)

    def char_write_req(self, handle):
        cmd = 'char-write-req 0x%04x 0100' % handle
        print(cmd)
        self.conn.sendline(cmd)
        self.conn.expect('Characteristic value was written successfully', timeout = 5)

    def notification_loop(self):
        count = 0
        while True:
            try:
                pnum = self.conn.expect('Notification handle = .*? \r', timeout = 10)
            except pexpect.TIMEOUT:
                print("timeout exception!")
                break
            if pnum == 0:
                after = self.conn.after
                data = after.split()[3:]
                handle = int(data[0], 0)
                if self.callbacks[handle]:
                    data = data[2:]
                    self.callbacks[handle](data)
            if count >= 100000:
                print('times full')
                break
            count += 1

    def register_callback(self, handle, function):
        self.callbacks[handle] = function

def recv_data(handle):
    ble = Ble('D1:72:EA:57:91:10')
    ble.mtu(248)
    ble.char_write_req(0x0013)
    ble.char_write_cmd(0x0010, 'fa313030fb')
    ble.register_callback(0x0012, handle)
    ble.notification_loop()

if __name__ == '__main__':
    def handle(value):
        print(value)
    recv_data(handle)
