#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
import numpy as np

data = np.fromfile('data/out.prs', np.uint8)

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

data1 = data[0::8]
data2 = data[1::8]
data3 = data[2::8]
data4 = data[3::8]
data5 = data[4::8]
data6 = data[5::8]
data7 = data[6::8]
data8 = data[7::8]

# # intial parameters
# n_iter = data1.size
# sz = (n_iter,) # size of array
# x = -0.37727 # truth value (typo in example at top of p. 13 calls this z)
# # z = np.random.normal(x,0.1,size=sz) # observations (normal about x, sigma=0.1)

# Q = 1e-5 # process variance

# # allocate space for arrays
# xhat=np.zeros(sz)      # a posteri estimate of x
# P=np.zeros(sz)         # a posteri error estimate
# xhatminus=np.zeros(sz) # a priori estimate of x
# Pminus=np.zeros(sz)    # a priori error estimate
# K=np.zeros(sz)         # gain or blending factor

# R = 0.1**2 # estimate of measurement variance, change to see effect

# # intial guesses
# xhat[0] = 0.0
# P[0] = 1.0

# for k in range(1,n_iter):
#     # time update
#     xhatminus[k] = xhat[k-1]
#     Pminus[k] = P[k-1]+Q

#     # measurement update
#     K[k] = Pminus[k]/( Pminus[k]+R )
#     xhat[k] = xhatminus[k]+K[k]*(data1[k]-xhatminus[k])
#     P[k] = (1-K[k])*Pminus[k]

# order = 6
# fs = 30.0       # sample rate, Hz
# cutoff = 3.667
# b, a = butter_lowpass(cutoff, fs, order)
# data11 = butter_lowpass_filter(data1, cutoff, fs, order)
# data22 = butter_lowpass_filter(data2, cutoff, fs, order)
# data33 = butter_lowpass_filter(data3, cutoff, fs, order)
# data44 = butter_lowpass_filter(data4, cutoff, fs, order)
# data55 = butter_lowpass_filter(data5, cutoff, fs, order)
# data66 = butter_lowpass_filter(data6, cutoff, fs, order)
# data77 = butter_lowpass_filter(data7, cutoff, fs, order)
# data88 = butter_lowpass_filter(data8, cutoff, fs, order)

p1 = plt.subplot(421)
p2 = plt.subplot(422)
p3 = plt.subplot(423)
p4 = plt.subplot(424)
p5 = plt.subplot(425)
p6 = plt.subplot(426)
p7 = plt.subplot(427)
p8 = plt.subplot(428)

# x1 = np.arange(data1.size)
# plt.plot(x1, data1, 'r')
# x2 = np.arange(data2.size)
# plt.plot(x2, data2, 'g')
# # p3.plot(data33[100:])
# x4 = np.arange(data4.size)
# plt.plot(x4, data4, 'b')
# x5 = np.arange(data5.size)
# plt.plot(x5, data5, 'y')
# p6.plot(data66[100:])
# p7.plot(data77[100:])
# p8.plot(data88[100:])

p1.plot(data1)
p2.plot(data2)
p3.plot(data3)
p4.plot(data4)
p5.plot(data5)
p6.plot(data6)
p7.plot(data7)
p8.plot(data8)

np.save('out.pcm', data1)

plt.show()