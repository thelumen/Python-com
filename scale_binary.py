#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

if __name__ == '__main__':
    f = open('/home/zhoulong/CodeBlocks/libsvm-3.22/tools/scale', 'r')
    scale = []
    total = 0
    while True:
        line = f.readline().rstrip('\n')
        if not line:
            break
        num = line.split(' ')
        if len(num) == 3:
            scale.append([float(num[1]), float(num[2])])
            total += 1
    out = np.array(scale, dtype=np.float64).T
    out.tofile('data/scale.bin')
    print(total)
