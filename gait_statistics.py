#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from ctypes import *
import math
import csv
import re

from cpython import Processor
from gait_analysis import Analysis

def by_age(row, i):
    age = int(row[i])
    return 0 if age < 20 else 4 if age >= 80 else age // 20

def by_gender(row, i):
    gender = row[i]
    return 0 if gender == '男' else 1 if gender == '女' else -1

def by_status(row, i):
    status = row[i]
    return 0 if status == '病人' else 1 if status == '正常人' else -1

def by_name(row):
    return row[0]

def by_archive(row):
    return row[0] + '+' + row[1]

class Classifier_Age_Gender:
    def __init__(self):
        self.age = ['<20', '20~39', '40~59', '60~79', '>80', 'unknown']
        self.gender = ['男', '女', 'unknown']

    def classify(self, row):
        age = by_age(row, -7)
        gender = by_gender(row, -5)
        return self.gender[gender] + self.age[age]

    def classes(self):
        for age in range(1, 5):
            for gender in range(0, 2):
                yield self.gender[gender] + self.age[age]

class Classifier_Age_Gender_Status:
    def __init__(self):
        self.age = ['<20', '20~39', '40~59', '60~79', '>80', 'unknown']
        self.gender = ['男', '女', 'unknown']
        self.status = [' 病人', ' 正常人', 'unknown']

    def classify(self, row):
        age = by_age(row, -7)
        gender = by_gender(row, -5)
        status = by_status(row, -6)
        return self.gender[gender] + self.age[age] + self.status[status]

    def classes(self):
        for age in range(1, 5):
            for gender in range(0, 2):
                for status in range(0, 2):
                    yield self.gender[gender] + self.age[age] + self.status[status]

class Classifier_Ill_Age_Gender:
    def __init__(self):
        self.ill = ['跟痛症', '跟腱炎', '前脚掌', '膝关节', '髌腱炎', '骨折不愈合', '腰椎', '臀部', '髋关节痛', 'unknown']
        self.age = ['<20', '20~39', '40~59', '60~79', '>80', 'unknown']
        self.gender = ['男', '女', 'unknown']

    def classify(self, row):
        age = by_age(row, -7)
        gender = by_gender(row, -5)
        return self.ill[ill] + self.gender[gender] + self.age[age]

    def classes(self):
        for ill in range(0, 3):
            for age in range(1, 5):
                for gender in range(0, 2):
                    yield self.ill[ill] + self.gender[gender] + self.age[age]

class Comma:
    def __init__(self):
        self.csvf = None
        self.writer = None

    def open(self, row):
        self.csvf = open('report/separate/' + row[0] + '_' + row[1] + '.csv', 'w', newline='')
        self.writer = csv.writer(self.csvf, dialect='excel', delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        self.writer.writerow(row[-6 : -1])
        self.cur = {'space': [], 'time': [], 'time_n': [], 'min': [[], []], 'max': [[], []]}

    def space(self, res, n):
        self.cur['space'].append(res)

    def time(self, res, n):
        self.cur['time'].append(res)
        self.cur['time_n'].append(n)

    def phase(self):
        analysis = Analysis(self.cur['time'][0], self.cur['space'][0], self.cur['time_n'][0],\
            self.cur['time'][1], self.cur['space'][1], self.cur['time_n'][1])
        if analysis.analysis() >= 0:
            self.left_start = analysis.one_start
            self.left_end = analysis.one_index
            self.right_start = analysis.other_start
            self.right_end = analysis.other_index
            analysis.cadence()
            self.writer.writerow(['左脚'])
            if self.left_end - self.left_start >= 2:
                self.writer.writerow(['步幅'] + analysis.one_stride[1 :])
                self.writer.writerow(['摆动时间'] + [x * 0.02 for x in analysis.one_swing[1 :]])
                self.writer.writerow(['站立时间'] + [x * 0.02 for x in analysis.one_stance])
                self.writer.writerow(['双支撑时间'] + [x * 0.02 for x in analysis.one_both])
                self.writer.writerow(['步频'] + analysis.one_cadence[1 :])
                self.writer.writerow(['步速'] + analysis.one_velocity[1 :])
                space = self.cur['space'][0]
                start = self.left_start * 5 + 5
                end = self.left_end * 5
                self.writer.writerow(['偏角'] + [space[i] for i in range(start + 1, end, 5)])
                self.writer.writerow(['离地角度'] + [space[i] for i in range(start + 2, end, 5)])
                self.writer.writerow(['着地角度'] + [space[i] for i in range(start + 3, end, 5)])
            self.writer.writerow([])
            self.writer.writerow(['右脚'])
            if self.right_end - self.right_start >= 2:
                self.writer.writerow(['步幅'] + analysis.other_stride[1 :])
                self.writer.writerow(['摆动时间'] + [x * 0.02 for x in analysis.other_swing[1 :]])
                self.writer.writerow(['站立时间'] + [x * 0.02 for x in analysis.other_stance])
                self.writer.writerow(['双支撑时间'] + [x * 0.02 for x in analysis.other_both])
                self.writer.writerow(['步频'] + analysis.other_cadence[1 :])
                self.writer.writerow(['步速'] + analysis.other_velocity[1 :])
                space = self.cur['space'][1]
                start = self.right_start * 5 + 5
                end = self.right_end * 5
                self.writer.writerow(['偏角'] + [space[i] for i in range(start + 1, end, 5)])
                self.writer.writerow(['离地角度'] + [space[i] for i in range(start + 2, end, 5)])
                self.writer.writerow(['着地角度'] + [space[i] for i in range(start + 3, end, 5)])
        else:
            self.left_start = 0
            self.left_end = 0
            self.right_start = 0
            self.right_end = 0
        self.writer.writerow([])

    def trajectory(self, res, n, i, foot):
        if i > self.left_start and i < self.left_end if foot == 0 else i > self.right_start and i < self.right_end:
            self.writer.writerow(['角度_x' + str(i)] + [str(res[i]) for i in range(0, n, 6)])
            self.writer.writerow(['角度_y' + str(i)] + [str(res[i]) for i in range(1, n, 6)])
            self.writer.writerow(['角度_z' + str(i)] + [str(res[i]) for i in range(2, n, 6)])
            self.writer.writerow(['坐标_x' + str(i)] + [str(res[i]) for i in range(3, n, 6)])
            self.writer.writerow(['坐标_y' + str(i)] + [str(res[i]) for i in range(4, n, 6)])
            self.writer.writerow(['坐标_z' + str(i)] + [str(res[i]) for i in range(5, n, 6)])

    def center(self, res, n, i, foot):
        self.writer.writerow(['压力大小_' + str(i)] + [str(res[i]) for i in range(0, n, 1)])
        self.writer.writerow(['压力位置_' + str(i)] + [str(res[i]) for i in range(n, n * 2, 1)])

    def close(self):
        self.csvf.close()

    def done(self):
        pass

class Statistics:
    def __init__(self, classify, identifier):
        self.sum = {}
        self.classify = classify
        self.identifier = identifier
        self.keys = ['stride', 'swing', 'stance', 'swing', 'both', 'cadence', 'velocity', 'angle', 'depression', 'elevation', 'min', 'max']
        self.names = ['', '步幅', '摆动时间', '支撑时间', '单足时间', '双足时间', '步频', '步速', '足偏角', '离地角度', '着地角度', '摆动最小角度', '摆动最大角度', '年龄']

    def open(self, row):
        i = self.classify(row)
        if i in self.sum:
            self.sub = self.sum[i]
        else:
            self.sub = {}
            self.sum[i] = self.sub
        n = self.identifier(row)
        if n in self.sub:
            self.patient = self.sub[n]
        else:
            self.patient = {'age': row[-7], 'height': row[-4], 'weight': row[-3], 'status': row[-6],\
                'comment': str(row[-2]) + str(row[-1]), 'stride': [[], []], 'angle': [[], []], 'depression': [[], []], 'elevation': [[], []],\
                'swing': [[], []], 'stance': [[], []], 'both': [[], []], 'min': [[], []], 'max': [[], []], 'cadence': [[], []], 'velocity': [[], []]}
            self.sub[n] = self.patient
        h = float(row[-4])
        if h > 185 or h < 150:
            print('warning height', h)
        self.cur = {'space': [], 'time': [], 'time_n': [], 'min': [[], []], 'max': [[], []]}

    def space(self, res, n):
        self.cur['space'].append(res)

    def time(self, res, n):
        self.cur['time'].append(res)
        self.cur['time_n'].append(n)

    def zero(self, res, n):
        pass

    def phase(self):
        analysis = Analysis(self.cur['time'][0], self.cur['space'][0], self.cur['time_n'][0],\
            self.cur['time'][1], self.cur['space'][1], self.cur['time_n'][1])
        if analysis.analysis() >= 0:
            self.left_start = analysis.one_start
            self.left_end = analysis.one_index
            self.right_start = analysis.other_start
            self.right_end = analysis.other_index
            analysis.cadence()
            if self.left_end - self.left_start >= 2:
                self.patient['stride'][0].extend(analysis.one_stride[1 :])
                self.patient['swing'][0].extend([x * 0.02 for x in analysis.one_swing[1 :]])
                self.patient['stance'][0].extend([x * 0.02 for x in analysis.one_stance])
                self.patient['both'][0].extend([x * 0.02 for x in analysis.one_both])
                self.patient['cadence'][0].extend(analysis.one_cadence[1 :])
                self.patient['velocity'][0].extend(analysis.one_velocity[1 :])
                space = self.cur['space'][0]
                start = self.left_start * 5 + 5
                end = self.left_end * 5
                self.patient['angle'][0].extend([space[i] for i in range(start + 1, end, 5)])
                self.patient['depression'][0].extend([space[i] for i in range(start + 2, end, 5)])
                self.patient['elevation'][0].extend([space[i] for i in range(start + 3, end, 5)])
            if self.right_end - self.right_start >= 2:
                self.patient['stride'][1].extend(analysis.other_stride[1 :])
                self.patient['swing'][1].extend([x * 0.02 for x in analysis.other_swing[1 :]])
                self.patient['stance'][1].extend([x * 0.02 for x in analysis.other_stance])
                self.patient['both'][1].extend([x * 0.02 for x in analysis.other_both])
                self.patient['cadence'][1].extend(analysis.other_cadence[1 :])
                self.patient['velocity'][1].extend(analysis.other_velocity[1 :])
                space = self.cur['space'][1]
                start = self.right_start * 5 + 5
                end = self.right_end * 5
                self.patient['angle'][1].extend([space[i] for i in range(start + 1, end, 5)])
                self.patient['depression'][1].extend([space[i] for i in range(start + 2, end, 5)])
                self.patient['elevation'][1].extend([space[i] for i in range(start + 3, end, 5)])
        else:
            self.left_start = 0
            self.left_end = 0
            self.right_start = 0
            self.right_end = 0

    def trajectory(self, res, n, i, foot):
        if foot == 0:
            if i > self.left_start and i < self.left_end:
                a = [res[i] for i in range(0, n, 6)]
                self.cur['min'][0].append(min(a))
                self.cur['max'][0].append(max(a))
        else:
            if i > self.right_start and i < self.right_end:
                a = [res[i] for i in range(0, n, 6)]
                self.cur['min'][1].append(-max(a))
                self.cur['max'][1].append(-min(a))

    def center(self, res, n, i, foot):
        pass

    def close(self):
        if self.left_end - self.left_start >= 2:
            self.patient['min'][0].extend([x * 180 / math.pi for x in self.cur['min'][0]])
            self.patient['max'][0].extend([x * 180 / math.pi for x in self.cur['max'][0]])
        if self.right_end - self.right_start >= 2:
            self.patient['min'][1].extend([x * 180 / math.pi for x in self.cur['min'][1]])
            self.patient['max'][1].extend([x * 180 / math.pi for x in self.cur['max'][1]])

class Plotter:
    def __init__(self):
        pass

    def open(self, row):
        self.cur = {'time': [], 'time_n': [], 'zero': [], 'zero_n': []}

    def space(self, res, n):
        pass

    def time(self, res, n):
        self.cur['time'].append(res)
        self.cur['time_n'].append(n)

    def zero(self, res, n):
        self.cur['zero'].append(res)
        self.cur['zero_n'].append(n)

    def phase(self):
        pass

    def trajectory(self, res, n, i, foot):
        pass

    def center(self, res, n, i, foot):
        pass

    def close(self):
        self.dic = {}
        n = self.cur['time_n'][0]
        self.dic['left_time'] = [self.cur['time'][0][i] for i in range(0, n * 4)]
        n = self.cur['time_n'][1]
        self.dic['right_time'] = [self.cur['time'][1][i] for i in range(0, n * 4)]
        n = self.cur['zero_n'][0]
        self.dic['left_zero'] = [self.cur['zero'][0][i] for i in range(0, n * 2)]
        n = self.cur['zero_n'][1]
        self.dic['right_zero'] = [self.cur['zero'][1][i] for i in range(0, n * 2)]

class Walk:
    def __init__(self, handler):
        self.process = Processor()
        self.handler = handler

    def process_result(self, delta):
        space_size = POINTER(c_int)()
        res = self.process.get_diagnose_space(byref(space_size))
        self.handler.space(res, space_size[0])
        time_size = POINTER(c_int)()
        res = self.process.get_diagnose_time(byref(time_size), delta)
        self.handler.time(res, time_size[0])
        zero_size = POINTER(c_int)()
        res = self.process.get_diagnose_zero(byref(zero_size))
        self.handler.zero(res, zero_size[0])
        return zero_size

    def process_detail(self, detail, foot):
        size = POINTER(c_int)()
        count = 0
        while detail:
            res = self.process.detail_trajectory(byref(size), detail)
            if res:
                n = size[0] * 6 - 6
                self.handler.trajectory(res, n, count, foot)
            # res = self.process.detail_center(byref(size), detail)
            # if res:
            #     n = size[0]
            #     self.handler.center(res, n, count, foot)
            detail = self.process.next_detail(detail)
            count += 1

    def process_file(self, d, row):
        print(row)
        self.handler.open(row)
        # left
        calib = re.split(r',|\.', row[3])
        # print(calib)
        self.process.reset_delivery_parameter(0, np.ascontiguousarray([int(i) for i in calib], dtype='i2'))
        da = np.fromfile(d + '/' + row[1] + '_left.dat', dtype='i1')
        for i in range(504, len(da), 508):
            self.process.get_data_result(da[i - 500 : i])
        self.process.get_fake_data_result()
        left_zero = self.process_result(c_longlong(row[2]))
        left_detail = self.process.get_detail()
        # right
        calib = re.split(r',|\.', row[4])
        # print(calib)
        self.process.reset_delivery_parameter(1, np.ascontiguousarray([int(i) for i in calib], dtype='i2'))
        da = np.fromfile(d + '/' + row[1] + '_right.dat', dtype='i1')
        for i in range(504, len(da), 508):
            self.process.get_data_result(da[i - 500 : i])
        self.process.get_fake_data_result()
        right_zero = self.process_result(c_longlong(0))
        right_detail = self.process.get_detail()
        self.handler.phase()
        # detail
        self.process_detail(left_detail, 0)
        self.process_detail(right_detail, 1)
        self.handler.close()
        self.process.free_result(left_zero)
        self.process.free_result(right_zero)

if __name__ == '__main__':
    handler = Statistics(by_name)
    walk = Walk(handler)
    walk.process_file('/home/longzhou/Data/chaoyangxiyuan/2018-03-20_2',\
        ['苗树长', '1521523578', 20535153, '40,0,59,4088,4090,4073.-15,32,4', '-65,-66,20,4095,4093,4067.23,31,11',\
        '66', '正常人', '男', '173', '75', '', '18211171079'])
