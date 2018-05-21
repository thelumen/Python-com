#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import sqlite3
import json
import csv

from os.path import dirname
from gait_statistics import *

class Report:
    def __init__(self, handler):
        self.handler = handler
        self.walk = Walk(handler)

    def process_hospital(self, di):
        dbs = glob.glob(di + '/zkhc.db')
        for db in dbs:
            d = dirname(db)
            print(d)
            conn = sqlite3.connect('file:' + db + '?mode=ro', uri=True)
            c = conn.cursor()
            cursor = c.execute('select p.name,a.name,a.delta,a.left_calibrate,a.right_calibrate,p.age,p.status,p.gender,p.height,p.weight,p.remark,g.comment\
                from patient as p left join series as g on p._id=g.pid left join archive as a on g._id=a.pid where a.type="正常行走" and p.status="正常人"')# where a.type="正常行走" and p.status="病人"
            for row in cursor:
                self.walk.process_file(d, row)
            conn.close()
            # break
        print('********************************************************')
        info = ['男<20', '女<20', '男20~39', '女20~39', '男40~59', '女40~59', '男60~79', '女60~79', '男>80', '女>80']
        keys = ['stride', 'swing', 'stance', 'swing', 'both', 'cadence', 'velocity', 'angle', 'depression', 'elevation', 'min', 'max']
        csvf = open('report/report.csv', 'w', newline='')
        writer = csv.writer(csvf, dialect='excel', delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['', '步幅', '摆动时间', '支撑时间', '单足时间', '双足时间', '步频', '步速', '足偏角', '离地角度', '着地角度', '摆动最小角度', '摆动最大角度', '人数'])
        for i in range(2, 10):
            print(info[i])
            line = [info[i]]
            if i in self.handler.sum:
                sub = self.handler.sum[i]
                print(len(sub))
                result = {'stride': [], 'angle': [], 'depression': [], 'elevation': [],\
                    'swing': [], 'stance': [], 'both': [], 'min': [], 'max': [], 'cadence': [], 'velocity': []}
                for n in sub:
                    patient = sub[n]
                    for k in keys:
                        if len(patient[k][0]) > 0 or len(patient[k][1]) > 0:
                            result[k].append(np.mean(np.concatenate((patient[k][0], patient[k][1]))))
                for k in keys:
                    norm = (np.mean(result[k]), np.std(result[k]))
                    line.append('%.2f±%.2f' % norm)
                    print(k, norm)
                line.append(len(sub))
            writer.writerow(line)
            print('-----------------------')
        writer.writerow([])
        writer.writerow(['每个人的信息'])
        for i in range(2, 10):
            print(info[i])
            writer.writerow([info[i]])
            if i in self.handler.sum:
                sub = self.handler.sum[i]
                for n in sorted(sub):
                    patient = sub[n]
                    line = [n]
                    for k in keys:
                        if len(patient[k][0]) > 0 or len(patient[k][1]) > 0:
                            a = np.concatenate((patient[k][0], patient[k][1]))
                            norm = (np.mean(a), np.std(a))
                            line.append('%.2f±%.2f' % norm)
                        else:
                            line.append('')
                    line.append(patient['height'])
                    line.append(patient['weight'])
                    writer.writerow(line)
            print('-----------------------')
        csvf.close()

    '''reliability'''
    def process_kongyoki(self):
        js = open('/home/zhoulong/Data/kongyoki/kongyoki.json', 'r')
        people = json.load(js)
        js.close()
        for name in people:
            archives = people[name]
            for d in archives:
                print(d, name)
                conn = sqlite3.connect('file:' + d + '/zkhc.db?mode=ro', uri=True)
                c = conn.cursor()
                for archive in archives[d]:
                    cursor = c.execute('select p.name,a.name,a.delta,a.left_calibrate,a.right_calibrate,p.age,p.status,p.gender,p.height,p.weight,p.remark,g.comment\
                        from patient as p left join series as g on p._id=g.pid left join archive as a on g._id=a.pid where a.name="%s"' % archive)
                    for row in cursor:
                        self.walk.process_file(d, row)
                conn.close()
        print('********************************************************')
        info = ['男<20', '女<20', '男20~39', '女20~39', '男40~59', '女40~59', '男60~79', '女60~79', '男>80', '女>80']
        keys = ['stride', 'swing', 'stance', 'swing', 'both', 'cadence', 'velocity', 'angle', 'depression', 'elevation', 'min', 'max']
        csvf = open('report/report.csv', 'w', newline='')
        writer = csv.writer(csvf, dialect='excel', delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['', '步幅', '摆动时间', '支撑时间', '单足时间', '双足时间', '步频', '步速', '足偏角', '离地角度', '着地角度', '摆动最小角度', '摆动最大角度', '年龄'])
        for i in range(2, 10):
            writer.writerow([info[i]])
            if i in self.handler.sum:
                sub = self.handler.sum[i]
                for n in sorted(sub):
                    patient = sub[n]
                    if patient['status'] == '病人':
                        line = [n[0 : n.find('+')]]
                        for k in keys:
                            a = patient[k][0]
                            if len(a) > 0:
                                norm = (np.mean(a), np.std(a))
                                line.append('%.2f±%.2f' % norm)
                            else:
                                line.append('')
                        line.append(patient['age'])
                        line.append(patient['height'])
                        line.append(patient['weight'])
                        line.append(patient['status'])
                        line.append(patient['comment'])
                        writer.writerow(line)
                        line = ['']
                        for k in keys:
                            a = patient[k][1]
                            if len(a) > 0:
                                norm = (np.mean(a), np.std(a))
                                line.append('%.2f±%.2f' % norm)
                            else:
                                line.append('')
                        writer.writerow(line)
                for n in sorted(sub):
                    patient = sub[n]
                    if patient['status'] == '正常人':
                        line = [n[0 : n.find('+')]]
                        for k in keys:
                            if len(patient[k][0]) > 0 or len(patient[k][1]) > 0:
                                a = np.concatenate((patient[k][0], patient[k][1]))
                                norm = (np.mean(a), np.std(a))
                                line.append('%.2f±%.2f' % norm)
                            else:
                                line.append('')
                        line.append(patient['age'])
                        line.append(patient['height'])
                        line.append(patient['weight'])
                        line.append(patient['status'])
                        line.append(patient['comment'])
                        writer.writerow(line)
        csvf.close()

    def process_knee(self):
        js = open('/home/zhoulong/Data/jishuitan/knee.json', 'r')
        people = json.load(js)
        js.close()
        suffix = {'before': '', 'after': '1'}
        for name in people:
            archives = people[name]
            for suf in suffix:
                d = archives[suf]
                print(d, name)
                conn = sqlite3.connect('file:' + d + '/zkhc.db?mode=ro', uri=True)
                c = conn.cursor()
                cursor = c.execute('select p.name,a.name,a.delta,a.left_calibrate,a.right_calibrate,p.age,p.status,p.gender,p.height,p.weight,p.remark,g.comment\
                    from patient as p left join series as g on p._id=g.pid left join archive as a on g._id=a.pid where p.name="%s"' % (name + suffix[suf]))
                for row in cursor:
                    self.walk.process_file(d, row)
                conn.close()
        print('********************************************************')
        info = ['男<20', '女<20', '男20~39', '女20~39', '男40~59', '女40~59', '男60~79', '女60~79', '男>80', '女>80']
        keys = ['stride', 'swing', 'stance', 'swing', 'both', 'cadence', 'velocity', 'angle', 'depression', 'elevation', 'min', 'max']
        csvf = open('report/report.csv', 'w', newline='')
        writer = csv.writer(csvf, dialect='excel', delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['', '步幅', '摆动时间', '支撑时间', '单足时间', '双足时间', '步频', '步速', '足偏角', '离地角度', '着地角度', '摆动最小角度', '摆动最大角度', '年龄'])
        for i in range(2, 10):
            writer.writerow([info[i]])
            if i in self.handler.sum:
                sub = self.handler.sum[i]
                for n in sorted(sub):
                    patient = sub[n]
                    if patient['status'] == '病人':
                        line = [n[0 : n.find('+')]]
                        for k in keys:
                            a = patient[k][0]
                            if len(a) > 0:
                                norm = (np.mean(a), np.std(a))
                                line.append('%.2f±%.2f' % norm)
                            else:
                                line.append('')
                        line.append(patient['age'])
                        line.append(patient['height'])
                        line.append(patient['weight'])
                        line.append(patient['status'])
                        line.append(patient['comment'])
                        writer.writerow(line)
                        line = ['']
                        for k in keys:
                            a = patient[k][1]
                            if len(a) > 0:
                                norm = (np.mean(a), np.std(a))
                                line.append('%.2f±%.2f' % norm)
                            else:
                                line.append('')
                        writer.writerow(line)
                for n in sorted(sub):
                    patient = sub[n]
                    if patient['status'] == '正常人':
                        line = [n[0 : n.find('+')]]
                        for k in keys:
                            if len(patient[k][0]) > 0 or len(patient[k][1]) > 0:
                                a = np.concatenate((patient[k][0], patient[k][1]))
                                norm = (np.mean(a), np.std(a))
                                line.append('%.2f±%.2f' % norm)
                            else:
                                line.append('')
                        line.append(patient['age'])
                        line.append(patient['height'])
                        line.append(patient['weight'])
                        line.append(patient['status'])
                        line.append(patient['comment'])
                        writer.writerow(line)
        csvf.close()

    def patient_information(self, di):
        total_age_gender = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        csvf = open('report/people.csv', 'w', newline='')
        writer = csv.writer(csvf, dialect='excel', delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        dbs = glob.glob(di + '/zkhc.db')
        for db in dbs:
            print(db)
            conn = sqlite3.connect('file:' + db + '?mode=ro', uri=True)
            c = conn.cursor()
            cursor = c.execute('select p.name,p.age,p.gender,p.height,p.weight,p.contact,p.remark from patient as p where p.status="病人"')
            for row in cursor:
                writer.writerow(row)
                print(row)
                total_age_gender[by_age_gender(row, 1, 2)] += 1
            conn.close()
        age = ['<20', '20~39', '40~59', '60~79', '80+']
        total_man = 0
        total_woman = 0
        for i in range(0, 5):
            print('年龄段 %s\t男:%3d 女%3d' % (age[i], total_age_gender[i << 1], total_age_gender[(i << 1) + 1]))
            total_man += total_age_gender[i << 1]
            total_woman += total_age_gender[(i << 1) + 1]
        print('总数\t%d\t男:%3d 女%3d' % (total_man + total_woman, total_man, total_woman))
        csvf.close()

if __name__ == '__main__':
    # handler = Statistics(by_name)
    # report = Report(handler)
    # # report.patient_information('/home/zhoulong/Data/jishuitan/*')
    # report.process_hospital('/home/zhoulong/Data/chaoyangxiyuan/*')

    handler = Statistics(by_archive)
    report = Report(handler)
    report.process_kongyoki()
    # report.process_knee()
