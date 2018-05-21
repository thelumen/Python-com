#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def progress(num):
    print('\r% 10d' % (num,), end='\r')

def progress2(num):
    sys.stdout.write('\r')
    sys.stdout.write('% 10d' % (num,))
    sys.stdout.flush()

if __name__ == '__main__':
    from time import sleep
    for i in range(20):
        progress(i)
        sleep(0.5)
