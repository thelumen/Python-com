#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import math

class Analysis:
    def __init__(self, one_time, one_space, one_n, other_time, other_space, other_n):
        self.one_heel_off = [one_time[i] for i in range(0, one_n * 4, 4)]
        self.one_off = [one_time[i] for i in range(1, one_n * 4, 4)]
        self.one_on = [one_time[i] for i in range(2, one_n * 4, 4)]
        self.one_stride = [one_space[i] for i in range(0, one_n * 5, 5)]
        self.other_heel_off = [other_time[i] for i in range(0, other_n * 4, 4)]
        self.other_off = [other_time[i] for i in range(1, other_n * 4, 4)]
        self.other_on = [other_time[i] for i in range(2, other_n * 4, 4)]
        self.other_stride = [other_space[i] for i in range(0, other_n * 5, 5)]
        self.one_n = one_n
        self.other_n = other_n
        self.one_start = 0
        self.other_start = 0
        self.one_index = 0
        self.other_index = 0
        self.reset()

    def reset(self):
        self.one_swing = []
        self.one_stance = []
        self.one_both = []
        self.one_heel = []
        self.other_swing = []
        self.other_stance = []
        self.other_both = []

    def analysis(self):
        # while self.one_index < self.one_n and self.other_index < self.other_n:
        if self.one_n > 0 and self.other_n > 0:
            # print(self.one_stride, self.other_stride)
            print('range', self.one_n, self.other_n)
            while True:
                status = self.synchronize()
                if status >= 0:
                    print('start', self.one_start, self.other_start)
                    self.continuous(status)
                    print('end', self.one_index, self.other_index)
                    if self.one_index < self.one_n // 2 and self.other_index < self.other_n // 2:
                        self.reset()
                        self.one_start = self.one_index + 1
                        self.other_start = self.other_index + 1
                        continue
                else:
                    print('bad data')
                break
        else:
            print('data incomplete')
            print(self.one_stride, self.other_stride)
            status = self.single()
        return status

    def synchronize(self):
        status = -1
        while self.one_start < self.one_n and self.other_start < self.other_n:
            one_cur_off = self.one_off[self.one_start]
            other_cur_off = self.other_off[self.other_start]
            if one_cur_off < other_cur_off:
                one_cur_on = self.one_on[self.one_start]
                cur_stride = self.one_stride[self.one_start]
                if one_cur_off == 0 or one_cur_on < one_cur_off\
                    or math.isnan(cur_stride) or cur_stride < 0.1 or cur_stride > 2.0:
                    status = -1
                elif one_cur_on > other_cur_off:
                    self.other_start += 1
                    status = -1
                elif status == 1:
                    self.other_start -= 1
                    break
                else:
                    status = 0
                self.one_start += 1
            else:
                other_cur_on = self.other_on[self.other_start]
                cur_stride = self.other_stride[self.other_start]
                if other_cur_off == 0 or other_cur_on < other_cur_off\
                    or math.isnan(cur_stride) or cur_stride < 0.1 or cur_stride > 2.0:
                    status = -1
                elif other_cur_on > one_cur_off:
                    self.one_start += 1
                    status = -1
                elif status == 0:
                    self.one_start -= 1
                    break
                else:
                    status = 1
                self.other_start += 1
        return status

    def continuous(self, status):
        one_last_heel = self.one_heel_off[self.one_start]
        one_last_off = self.one_off[self.one_start]
        one_last_on = self.one_on[self.one_start]
        other_last_off = self.other_off[self.other_start]
        other_last_on = self.other_on[self.other_start]
        one_next = self.one_start + 1
        other_next = self.other_start + 1
        while one_next < self.one_n if status == 0 else other_next < self.other_n:
            if status == 0:
                one_cur_heel = self.one_heel_off[one_next]
                one_cur_off = self.one_off[one_next]
                one_cur_on = self.one_on[one_next]
                if other_last_off == 0 or other_last_on < other_last_off or one_cur_off < other_last_off:
                    print('corrupted one')
                    return
                if other_last_on > one_cur_off:
                    print('interrupted one')
                    return
                cur_stride = self.one_stride[one_next]
                if math.isnan(cur_stride) or cur_stride < 0.1 or cur_stride > 2.0:
                    print('bad one stride', cur_stride)
                    return
                self.handle_one(one_last_off, one_last_on, other_last_off, other_last_on, one_cur_off, one_last_heel)
                self.one_index = one_next
                one_last_heel = one_cur_heel
                one_last_off = one_cur_off
                one_last_on = one_cur_on
                one_next += 1
                status = 1
            else:
                other_cur_off = self.other_off[other_next]
                other_cur_on = self.other_on[other_next]
                if one_last_off == 0 or one_last_on < one_last_off or other_cur_off < one_last_off:
                    print('corrupted other')
                    return
                if one_last_on > other_cur_off:
                    print('interrupted other')
                    return
                cur_stride = self.other_stride[other_next]
                if math.isnan(cur_stride) or cur_stride < 0.1 or cur_stride > 2.0:
                    print('bad other stride', cur_stride)
                    return
                self.handle_other(other_last_off, other_last_on, one_last_off, one_last_on, other_cur_off)
                self.other_index = other_next
                other_last_off = other_cur_off
                other_last_on = other_cur_on
                other_next += 1
                status = 0

    def single(self):
        if self.one_n > 0:
            while self.one_start < self.one_n:
                last_off = self.one_off[self.one_start]
                last_on = self.one_on[self.one_start]
                stride = self.one_stride[self.one_start]
                if last_off > 0 and last_on > last_off and stride > 0.3 and stride < 2.0:
                    break
                self.one_start += 1
            i = self.one_start + 1
            while i < self.one_n:
                off = self.one_off[i]
                on = self.one_on[i]
                if last_off > last_on or off < last_on:
                    print('corrupted single')
                    break
                stride = self.one_stride[i]
                if math.isnan(stride) or stride < 0.3 or stride > 2.0:
                    print('bad stride', stride)
                    break
                self.one_swing.append(last_on - last_off)
                self.one_stance.append(off - last_on)
                self.one_index = i
                last_off = off
                last_on = on
                i += 1
            print('range', self.one_start, self.one_index)
        elif self.other_n > 0:
            while self.other_start < self.other_n:
                last_off = self.other_off[self.other_start]
                last_on = self.other_on[self.other_start]
                stride = self.other_stride[self.other_start]
                if last_off > 0 and last_on > last_off and stride > 0.3 and stride < 2.0:
                    break
                self.other_start += 1
            i = self.other_start + 1
            while i < self.other_n:
                off = self.other_off[i]
                on = self.other_on[i]
                if last_off > last_on or off < last_on:
                    print('corrupted single')
                    break
                stride = self.other_stride[i]
                if math.isnan(stride) or stride < 0.3 or stride > 2.0:
                    print('bad stride', stride)
                    break
                self.other_swing.append(last_on - last_off)
                self.other_stance.append(off - last_on)
                self.other_index = i
                last_off = off
                last_on = on
                i += 1
            print('range', self.other_start, self.other_index)
        else:
            return -1
        return 2

    def handle_one(self, one_last_off, one_last_on, other_last_off, other_last_on, one_cur_off, one_last_heel):
        self.one_swing.append(one_last_on - one_last_off)
        self.one_stance.append(one_cur_off - one_last_on)
        self.one_both.append(other_last_off - one_last_on)
        self.one_heel.append(one_last_off - one_last_heel)

    def handle_other(self, other_last_off, other_last_on, one_last_off, one_last_on, other_cur_off):
        self.other_swing.append(other_last_on - other_last_off)
        self.other_stance.append(other_cur_off - other_last_on)
        self.other_both.append(one_last_off - other_last_on)

    def phase(self):
        if len(self.one_swing) == 0 or len(self.other_swing) == 0:
            return (1, 1, 1, 1)
        return (np.mean(self.one_both), np.mean(self.other_swing), np.mean(self.other_both), np.mean(self.one_swing))

    def aspect(self):
        if len(self.one_swing) == 0 or len(self.other_swing) == 0:
            return (1, 1, 1, 1, 1)
        other_both = np.mean(self.other_both)
        delta_heel = np.mean(self.one_heel) - other_both
        print(delta_heel)
        return (np.mean(self.one_both), np.mean(self.other_swing) - delta_heel, delta_heel, other_both, np.mean(self.one_swing))

    def cadence(self):
        self.one_cadence = []
        self.other_cadence = []
        self.one_velocity = []
        self.other_velocity = []
        self.one_stride = self.one_stride[self.one_start : self.one_index]
        i = 0
        while i < self.one_index - self.one_start:
            t = 50 / (self.one_swing[i] + self.one_stance[i])
            self.one_cadence.append(120 * t)
            self.one_velocity.append(self.one_stride[i] * t)
            i += 1
        self.other_stride = self.other_stride[self.other_start : self.other_index]
        i = 0
        while i < self.other_index - self.other_start:
            t = 50 / (self.other_swing[i] + self.other_stance[i])
            self.other_cadence.append(120 * t)
            self.other_velocity.append(self.other_stride[i] * t)
            i += 1
