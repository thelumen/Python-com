#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
from ctypes import *
import re
import sys

from cpython import Proccessor
from gait_analysis import Analysis

proccess = None

def process_result(delta):
    size = POINTER(c_int)()
    space = proccess.get_diagnose_space(byref(size))
    n = size[0]
    time = proccess.get_diagnose_time(byref(size), delta)
    m = size[0]
    return space, n, time, m

def plot_steps(left_space, left_n, right_space, right_n, title, xlabel, ylabel, ylim, start, out):
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.ylim(ylim)
    p = np.array([left_space[i] for i in range(start, left_n * 5, 5)])
    plt.plot(p, 'r-', label='左脚', marker='o')
    p = np.array([right_space[i] for i in range(start, right_n * 5, 5)])
    plt.plot(p, 'b-', label='右脚', marker='o')
    plt.legend(loc='lower right', frameon=False)
    plt.savefig(out)
    plt.cla()

def plot_space(left_space, left_n, right_space, right_n):
    # stride
    plot_steps(left_space, left_n, right_space, right_n, '步幅', '步数', '距离(米)', (0, 2), 0, 'img/stride.png')
    # angle
    plot_steps(left_space, left_n, right_space, right_n, '着地后脚与前进方向的夹角', '步数', '足偏角(度)', (0, 45), 1, 'img/angle.png')
    # depression
    plot_steps(left_space, left_n, right_space, right_n, '离地时脚与地面的夹角', '步数', '离地角度(度)', (-90, 0), 2, 'img/depression.png')
    # elevation
    plot_steps(left_space, left_n, right_space, right_n, '着地时脚与地面的夹角', '步数', '着地角度(度)', (-10, 45), 3, 'img/elevation.png')
    # height
    plot_steps(left_space, left_n, right_space, right_n, '抬脚高度', '步数', '离地高度(米)', (0, 0.5), 4, 'img/height.png')

def plot_time(left_time, left_m, right_time, right_m):
    # time
    p = [left_time[i] * 0.02 for i in range(1, left_m * 4, 4)]
    q = [left_time[i] * 0.02 for i in range(2, left_m * 4, 4)]
    plt.title('每一步的站立和摆动时间')
    plt.xlabel('步数')
    plt.ylabel('时间(秒)')
    d = []
    for i in range(0, len(p) - 1):
        d.append(p[i + 1] - q[i])
    plt.ylim(0, 3)
    plt.plot(np.array(d), 'r-', label='站立时间', marker='o')
    for i in range(0, len(q)):
        q[i] -= p[i]
    plt.ylim(0, 3)
    plt.plot(np.array(q), 'b-', label='摆动时间', marker='o')
    plt.legend(loc='upper right', frameon=False)
    plt.savefig('img/off.png')
    plt.cla()

def plot_phase(phase, aspect):
    s = sum(phase)
    t = s + phase[0]
    w = s * 250 / t
    f = ['左', '右']
    plt.figure(figsize=(12, 4))
    plt.axis([0, 300, 0, 120])
    plt.text(22, 40, f[aspect] + '脚', ha='right', va='center')
    plt.text(22, 80, f[1 - aspect] + '脚', ha='right', va='center')
    plt.plot((25, 285), (30, 30), 'k-')
    plt.plot((25, 285), (50, 50), 'k-')
    plt.plot((25, 285), (70, 70), 'k-')
    plt.plot((25, 285), (90, 90), 'k-')
    # 
    a1 = 30
    plt.gca().add_patch(patches.Rectangle((a1, a1), w, 20, linewidth=0, facecolor="#c6d2eb"))
    plt.plot((a1, a1), (21, 69), 'k', linewidth=3)
    plt.text(a1, 18, '右脚跟着地', ha='center', va='top')
    a2 = (phase[0] + phase[1] + phase[2]) * 250 / t + a1
    plt.plot((a2, a2), (21, 70), 'k', linewidth=2)
    plt.text(a2, 18, '右脚尖离地', ha='center', va='top')
    a3 = w + a1
    plt.plot((a3, a3), (21, 69), 'k', linewidth=3)
    plt.text(a3, 18, '右脚跟着地', ha='center', va='top')
    plt.text((a1 + a2) / 2, 40, '右站立相', ha='center', va='center')
    plt.text((a2 + a3) / 2, 40, '右摆动相', ha='center', va='center')
    # 
    b1 = phase[0] * 250 / t + a1
    plt.gca().add_patch(patches.Rectangle((b1, 70), w, 20, linewidth=0, facecolor="#7d9fd1"))
    plt.plot((b1, b1), (50, 99), 'k', linewidth=2)
    plt.text(b1, 102, '左脚尖离地', ha='center', va='bottom')
    b2 = (phase[1]) * 250 / t + b1
    plt.plot((b2, b2), (51, 99), 'k', linewidth=3)
    plt.text(b2, 102, '左脚跟着地', ha='center', va='bottom')
    b3 = 250 + a1
    plt.plot((b3, b3), (50, 99), 'k', linewidth=2)
    plt.text(b3, 102, '左脚尖离地', ha='center', va='bottom')
    plt.text((b1 + b2) / 2, 80, '左摆动相', ha='center', va='center')
    plt.text((b2 + b3) / 2, 80, '左站立相', ha='center', va='center')
    # 
    plt.text((a1 + b1) / 2, 60, '双支撑', ha='center', va='center')
    plt.text((b1 + b2) / 2, 60, '右单支撑', ha='center', va='center')
    plt.text((a2 + b2) / 2, 60, '双支撑', ha='center', va='center')
    plt.text((a2 + a3) / 2, 60, '左单支撑', ha='center', va='center')
    plt.text((a3 + b3) / 2, 60, '双支撑', ha='center', va='center')
    plt.savefig('img/phase.png')
    plt.cla()

def plot_aspect(phase, aspect):
    # phase = [10, 40, 80, 100, 120, 190]
    s = sum(phase)
    a = [10]
    t = 0
    for p in phase[: -1]:
        t += p
        a.append(t * 180 // s + 10)
    a.append(190)
    f = ['左', '右']
    img = ['pkl/right_initial_contact.png', 'pkl/left_toe_off.png', 'pkl/right_heel_off.png',
        'pkl/left_initial_contact.png', 'pkl/right_toe_off.png', 'pkl/right_initial_contact.png']
    p = [f[aspect] + '脚跟\n着地', f[1 - aspect] + '脚尖\n离地', f[aspect] + '脚跟\n离地', f[1 - aspect] + '脚跟\n着地',\
        f[aspect] + '脚尖\n离地', f[aspect] + '脚跟\n着地']
    q = ['承重反应期', '站立相中期', '站立相末期', '摆动前期', '']
    r = ['站立相', '摆动相']
    # plt.gcf()
    plt.figure(figsize=(16, 8))
    plt.axis([0, 200, 0, 90])
    plt.plot(a, [50 for i in range(0, 6)], 'r-', marker='o')
    i, j, k = 0, 0, 0
    last = None
    for x in a:
        plt.imshow(mpimg.imread(img[i]), extent=(x - 8, x + 8, 55, 85))
        plt.plot((x, x), (42, 48), 'k--')
        plt.text(x, 40, p[i], ha='center', va='top')
        plt.plot((x, x), (17, 32), 'k--')
        if last:
            plt.annotate('', xy=(x, 27), xycoords='data', xytext=(last, 27), textcoords='data',
                arrowprops=dict(arrowstyle='<|-|>', facecolor='w', edgecolor='k', lw=1), horizontalalignment='right', verticalalignment='bottom')
            plt.text((x + last) / 2, 22, q[j], ha='center', va='top')
            j += 1
        i += 1
        last = x
    last = None
    for x in [a[0], a[4], a[5]]:
        plt.plot((x, x), (2, 16), 'k--')
        if last:
            plt.annotate('', xy=(x, 12), xycoords='data', xytext=(last, 12), textcoords='data',
                arrowprops=dict(arrowstyle='<|-|>', facecolor='w', edgecolor='k', lw=1), horizontalalignment='right', verticalalignment='bottom')
            plt.text((x + last) / 2, 9, r[k], ha='center', va='top')
            k += 1
        last = x
    plt.savefig('img/aspect.png')
    plt.cla()

def plot_pressure(prs):
    grid = np.empty(44 * 15, dtype='f4')
    proccess.interpolate_foot(prs, grid)
    plt.imshow(grid.reshape((44, 15)), interpolation='nearest', origin="lower")
    plt.savefig('img/pressure.png')
    plt.cla()

def plot_step(res, n, start, coeff, title, xlabel, ylabel, out):
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.plot(np.array([res[i] for i in range(start, n, 6)]) * coeff)
    plt.savefig(out)
    plt.cla()

def process_detail(detail, feet, k):
    size = POINTER(c_int)()
    count = 0
    while detail:
        if count == k:
            res = proccess.detail_trajectory(byref(size), detail)
            if res:
                n = size[0] * 6 - 6
                plot_step(res, n, 0, 180 / 3.1415926, '矢状面旋转', '时间', '角度(度)', 'img/detail/' + feet + '_rx' + '.png')
                plot_step(res, n, 1, 180 / 3.1415926, '冠状面旋转', '时间', '角度(度)', 'img/detail/' + feet + '_ry' + '.png')
                plot_step(res, n, 2, 180 / 3.1415926, '水平面旋转', '时间', '角度(度)', 'img/detail/' + feet + '_rz' + '.png')
                plot_step(res, n, 3, 1, '侧向位移', '时间', '距离(米)', 'img/detail/' + feet + '_cx' + '.png')
                plot_step(res, n, 4, 1, '前向位移', '时间', '距离(米)', 'img/detail/' + feet + '_cy' + '.png')
                plot_step(res, n, 5, 1, '垂直位移', '时间', '距离(米)', 'img/detail/' + feet + '_cz' + '.png')
            break
        detail = proccess.next_detail(detail)
        count += 1

def process_data(di, dat, delta, left_calib, right_calib):
    # left
    left_calib = re.split(r',|\.', left_calib)
    print(left_calib)
    proccess.reset_delivery_parameter(0, np.ascontiguousarray([int(i) for i in left_calib], dtype='i2'))
    da = np.fromfile(di + '/' + dat + '_left.dat', dtype='i1')
    for i in range(504, len(da), 508):
        proccess.get_data_result(da[i - 500 : i])
    (left_space, left_n, left_time, left_m) = process_result(c_longlong(int(delta)))
    left_detail = proccess.get_detail()
    # right
    right_calib = re.split(r',|\.', right_calib)
    print(right_calib)
    proccess.reset_delivery_parameter(1, np.ascontiguousarray([int(i) for i in right_calib], dtype='i2'))
    da = np.fromfile(di + '/' + dat + '_right.dat', dtype='i1')
    for i in range(504, len(da), 508):
        proccess.get_data_result(da[i - 500 : i])
    (right_space, right_n, right_time, right_m) = process_result(c_longlong(0))
    right_detail = proccess.get_detail()
    plot_space(left_space, left_n, right_space, right_n)
    plot_time(left_time, left_m, right_time, right_m)
    # phase
    # phase = proccess.get_diagnose_phase(left, right)
    # if phase:
    #     proccess.free_result(phase)
    # detail
    analysis = Analysis(right_time, right_space, right_n, left_time, left_space, left_n)
    analysis.analysis()
    process_detail(left_detail, 'left', (analysis.other_index + analysis.other_start) >> 1)
    process_detail(right_detail, 'right', (analysis.one_index + analysis.one_start) >> 1)
    plot_phase(analysis.phase(), 1)
    plot_aspect(analysis.aspect(), 1)
    plot_pressure(np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.1, 0.5], dtype='f4'))

def process_file(di, dat):
    db = di + '/zkhc.db'
    conn = sqlite3.connect('file:' + db + '?mode=ro', uri=True)
    c = conn.cursor()
    cursor = c.execute('select delta,left_calibrate,right_calibrate from archive where name="' + dat + '"')
    for row in cursor:
        print(row)
        process_data(di, dat, row[0], row[1], row[2])
        break
    conn.close()

if __name__ == '__main__':
    proccess = Proccessor()
    if len(sys.argv) == 5:
        process_data('img', sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        process_file('/home/zhoulong/Data/chaoyangdongyuan/2017-12-29_1', '1514254964')
        # process_file('/home/zhoulong/Data/chaoyangdongyuan/2017-11-03', '1509693530')
