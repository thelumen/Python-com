#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import subprocess
import time
import os
import re

host = ('localhost', 9631)

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

class MyServer(BaseHTTPRequestHandler):
    '''https://gist.github.com/UniIsland/3346170'''
    pattern = re.compile(r'[a-zA-Z_0-9]')

    def do_GET(self):
        name = self.path[1 :]
        if MyServer.pattern.match(name):
            path = os.path.join('img', name + '.png')
            if os.path.isfile(path):
                self.send_response(200)
                self.send_header('Content-Type', 'image/png')
                self.end_headers()
                with open(path, 'rb') as f:
                    self.wfile.write(f.read())
                return
        self.send_head(404, 'false')

    def do_HEAD(self):
        name = self.path[1 :]
        if MyServer.pattern.match(name) and os.path.isfile(os.path.join('img', name + '_left.dat')) and\
            os.path.isfile(os.path.join('img', name + '_right.dat')):
            self.send_head(404, 'true')
        else:
            self.send_head(404, 'false')

    def do_POST(self):
        name = self.headers['Name']
        delta = self.headers['Delta']
        left_calib = self.headers['Left-Calib']
        right_calib = self.headers['Right-Calib']
        boundary = self.headers['Content-Type'].split('=')[1]
        remainbytes = int(self.headers['Content-Length'])
        while True:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if not boundary in str(line, 'utf-8'):
                self.send_head(200, 'false')
                return
            if remainbytes <= 0:
                break
            line = self.rfile.readline()
            remainbytes -= len(line)
            fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', str(line, 'utf-8'))
            if not fn:
                self.send_head(200, 'false')
                return
            fn = os.path.join('img', fn[0])
            line = self.rfile.readline()
            remainbytes -= len(line)
            line = self.rfile.readline()
            remainbytes -= len(line)
            curbytes = int(str(line, 'utf-8').rstrip().split(': ')[1])
            remainbytes -= curbytes
            line = self.rfile.readline()
            remainbytes -= len(line)
            with open(fn, 'wb') as f:
                while curbytes > 0:
                    f.write(self.rfile.read(1024 if curbytes >= 1024 else curbytes))
                    curbytes -= 1024
            line = self.rfile.readline()
            remainbytes -= len(line)
        if name is not None:
            cmd = ['python3', '/home/zhoulong/Sublime/mathematical_plot.py', name, delta, left_calib, right_calib]
            subprocess.check_call(cmd)
        self.send_head(200, 'true')

    def send_head(self, code, result):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', 8)
        self.send_header('Result', result)
        self.end_headers()
        self.wfile.write(b"longzhou")

if __name__ == '__main__':
    myServer = ThreadingSimpleServer(host, MyServer)
    print(time.asctime(), 'Server Starts - %s:%s' % host)
    try:
        myServer.serve_forever()
    except KeyboardInterrupt:
        pass
    myServer.server_close()
    print(time.asctime(), 'Server Stops')
