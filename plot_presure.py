#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

def plot_seprate(data):
    data1 = data[0::8]
    data2 = data[1::8]
    data3 = data[2::8]
    data4 = data[3::8]
    data5 = data[4::8]
    data6 = data[5::8]
    data7 = data[6::8]
    data8 = data[7::8]

    p1 = plt.subplot(421)
    p2 = plt.subplot(422)
    p3 = plt.subplot(423)
    p4 = plt.subplot(424)
    p5 = plt.subplot(425)
    p6 = plt.subplot(426)
    p7 = plt.subplot(427)
    p8 = plt.subplot(428)

    p1.plot(data1)
    p2.plot(data2)
    p3.plot(data3)
    p4.plot(data4)
    p5.plot(data5)
    p6.plot(data6)
    p7.plot(data7)
    p8.plot(data8)

def plot_all(data):
    data1 = data[0::8]
    data2 = data[1::8]
    data3 = data[2::8]
    data4 = data[3::8]
    data5 = data[4::8]
    data6 = data[5::8]
    data7 = data[6::8]
    data8 = data[7::8]

    plt.plot(data1, 'b')
    plt.plot(data2, 'g')
    plt.plot(data3, 'r')
    plt.plot(data4, 'c')
    # plt.plot(data5, 'm')
    # plt.plot(data6, 'y')
    plt.plot(data7, 'k')
    plt.plot(data8, 'm')

def plot_one(data):
    plt.plot(data[50:])

if __name__ == '__main__':
    data = np.fromfile('data/out.prs', dtype=np.uint8)

    plot_seprate(data)

    plt.show()
