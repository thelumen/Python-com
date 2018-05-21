#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

a = np.fromfile('/home/zhoulong/Downloads/out1.dat', dtype='<i2')
b = a[1 :: 6]
c = a[2 :: 6]
plt.plot(b)
plt.plot(c)
plt.show()