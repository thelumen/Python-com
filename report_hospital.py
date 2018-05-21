#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import sqlite3
import json
import xlsxwriter
import csv
import sys

from os.path import dirname, basename
from gait_statistics import *

class Report:
    def __init__(self):
        self.walk = Walk(self.handler)
        self.diseases = ['跟痛症', '跟腱炎', '前脚掌', '膝关节', '髌腱炎', '骨折不愈合', '腰椎', '臀部', '髋关节痛', 'unknown']
        self.focuses = ['左', '中', '右', '双', '?']
        self.age = ['<20', '20~39', '40~59', '60~79', '>80', 'unknown']
        self.gender = ['男', '女', 'unknown']
        self.status = [' 病人', ' 正常人', ' unknown']

    def classify(self, row):
        age = by_age(row, -7)
        gender = by_gender(row, -5)
        return self.gender[gender] + self.age[age]

    def classes(self):
        for age in range(1, 5):
            for gender in range(0, 2):
                yield self.gender[gender] + self.age[age]

    def order_by_date(self, dbs):
        date = {}
        for db in dbs:
            conn = sqlite3.connect('file:' + db + '?mode=ro', uri=True)
            c = conn.cursor()
            cursor = c.execute('select p.name,p.age,p.gender,p.height,p.weight,p.contact,p.remark,g.time from patient as p,series as g where p.status="病人" and p._id=g.pid group by p._id')
            for row in cursor:
                d = row[-1][: 5]
                if d in date:
                    today = date[d]
                else:
                    today = []
                    date[d] = today
                today.append((row[0], dirname(db)))
            conn.close()
        return date

class Report_Hospital(Report):
    def __init__(self, di):
        self.di = di
        # self.handler = Comma()
        self.handler = Statistics(self.classify, by_name)
        super().__init__()

    def process(self):
        dbs = glob.glob(self.di + '/zkhc.db')
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
        csvf = open('report/report.csv', 'w', newline='')
        writer = csv.writer(csvf, dialect='excel', delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(self.handler.names)
        for i in self.classes():
            print(i)
            line = [i]
            if i in self.handler.sum:
                sub = self.handler.sum[i]
                print(len(sub))
                result = {'stride': [], 'angle': [], 'depression': [], 'elevation': [],\
                    'swing': [], 'stance': [], 'both': [], 'min': [], 'max': [], 'cadence': [], 'velocity': []}
                for n in sub:
                    patient = sub[n]
                    for k in self.handler.keys:
                        if len(patient[k][0]) > 0 or len(patient[k][1]) > 0:
                            result[k].append(np.mean(np.concatenate((patient[k][0], patient[k][1]))))
                for k in self.handler.keys:
                    norm = (np.mean(result[k]), np.std(result[k]))
                    line.append('%.2f±%.2f' % norm)
                    print(k, norm)
                line.append(len(sub))
            writer.writerow(line)
            print('-----------------------')
        writer.writerow([])
        writer.writerow(['每个人的信息'])
        for i in self.classes():
            print(i)
            writer.writerow([i])
            if i in self.handler.sum:
                sub = self.handler.sum[i]
                for n in sorted(sub):
                    patient = sub[n]
                    line = [n]
                    for k in self.handler.keys:
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

class Report_Plot(Report):
    def __init__(self):
        self.handler = Plotter()
        super().__init__()

    def process(self):
        js = open('/home/longzhou/Data/chaoyangxiyuan/kongyoki.json', 'r')
        people = json.load(js)
        js.close()
        time_stamp = {}
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
                        time_stamp[d + '/' + archive] = self.handler.dic
                conn.close()
        data = json.dumps(time_stamp)
        outfile = open('time_stamp.json', 'w')
        outfile.write(data)
        outfile.close()
        print('********************************************************')

class Report_Jishuitan(Report):
    def __init__(self):
        js = open('/home/longzhou/Data/jishuitan/all.json', 'r')
        diseases = json.load(js)
        js.close()
        self.people = {}
        for disease in diseases:
            focuses = diseases[disease]
            for focus in focuses:
                patients = focuses[focus]
                for patient in patients:
                    self.people[patient] = (disease, focus)
        self.handler = Statistics(self.classify, by_name)
        super().__init__()

    def classify(self, row):
        return self.disease[0] + self.disease[1] + super().classify(row)

    def process(self):
        dbs = glob.glob('/home/longzhou/Data/jishuitan/*/zkhc.db')
        date = self.order_by_date(dbs)
        for d in date:
            today = date[d]
            today.sort(key=lambda x: x[0])
            print(d, today)
            idx, num = 0, len(today) - 1
            while idx < num:
                p0 = today[idx]
                p1 = today[idx + 1]
                if p0[0][: -1] == p1[0][: -1]:
                    for p in (p0, p1):
                        conn = sqlite3.connect('file:' + p[1] + '/zkhc.db?mode=ro', uri=True)
                        c = conn.cursor()
                        cursor = c.execute('select p.name,a.name,a.delta,a.left_calibrate,a.right_calibrate,p.age,p.status,p.gender,p.height,p.weight,p.remark,g.comment\
                            from patient as p left join series as g on p._id=g.pid left join archive as a on g._id=a.pid where p.name="%s"' % p[0])
                        print(p[0])
                        for row in cursor:
                            self.disease = self.people[row[0][: -1]]
                            self.walk.process_file(p[1], row)
                        conn.close()
                    idx += 2
                else:
                    idx += 1
        print('********************************************************')
        xlsx = xlsxwriter.Workbook('report/report_jishuitan.xlsx')
        for disease in self.diseases:
            sheet = xlsx.add_worksheet(disease)
            for i, name in enumerate(self.handler.names, start=0):
                sheet.write(0, i, name)
            row = 1
            for i in self.classes():
                sheet.write(row, 0, i)
                row += 1
                for focus in self.focuses:
                    c = disease + focus + i
                    if c in self.handler.sum:
                        sheet.write(row, 0, focus)
                        row += 1
                        sub = self.handler.sum[c]
                        for n in sorted(sub):
                            patient = sub[n]
                            sheet.write(row, 0, n)
                            col = 1
                            for k in self.handler.keys:
                                a = patient[k][0]
                                if len(a) > 0:
                                    norm = (np.mean(a), np.std(a))
                                    sheet.write(row, col, '%.2f±%.2f' % norm)
                                col += 1
                            sheet.write(row, col, patient['age'])
                            sheet.write(row, col + 1, patient['height'])
                            sheet.write(row, col + 2, patient['weight'])
                            sheet.write(row, col + 2, patient['weight'])
                            row += 1
                            col = 1
                            for k in self.handler.keys:
                                a = patient[k][1]
                                if len(a) > 0:
                                    norm = (np.mean(a), np.std(a))
                                    sheet.write(row, col, '%.2f±%.2f' % norm)
                                col += 1
                            row += 1
        xlsx.close()

class Report_Jishuitan1:
    def __init__(self):
        self.classifier = Classifier_Ill_Gender_Age()
        self.handler = Statistics(self.classifier.classify, by_archive)
        super().__init__()

    def process_knee(self):
        js = open('/home/longzhou/Data/jishuitan/knee.json', 'r')
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
        csvf = open('report/report.csv', 'w', newline='')
        writer = csv.writer(csvf, dialect='excel', delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(self.handler.names)
        for i in self.classifier.classes():
            writer.writerow([i])
            if i in self.handler.sum:
                sub = self.handler.sum[i]
                for n in sorted(sub):
                    patient = sub[n]
                    line = [n[0 : n.find('+')]]
                    for k in self.handler.keys:
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
                    for k in self.handler.keys:
                        a = patient[k][1]
                        if len(a) > 0:
                            norm = (np.mean(a), np.std(a))
                            line.append('%.2f±%.2f' % norm)
                        else:
                            line.append('')
                    writer.writerow(line)
        csvf.close()

class Report_Kongyoki(Report):
    def __init__(self):
        self.classifier = Classifier_Age_Gender()
        self.handler = Statistics(self.classifier.classify, by_archive)
        super().__init__()

    '''reliability'''
    def process(self):
        js = open('/home/longzhou/Data/chaoyangxiyuan/kongyoki.json', 'r')
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
        csvf = open('report/report.csv', 'w', newline='')
        writer = csv.writer(csvf, dialect='excel', delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(self.handler.names)
        for i in self.classifier.classes():
            if i in self.handler.sum:
                writer.writerow([i])
                sub = self.handler.sum[i]
                for n in sorted(sub):
                    patient = sub[n]
                    if patient['status'] == '病人':
                        line = [n[0 : n.find('+')]]
                        for k in self.handler.keys:
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
                        for k in self.handler.keys:
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
                        for k in self.handler.keys:
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

if __name__ == '__main__':
    # report = Report_Hospital('/home/longzhou/Data/chaoyangxiyuan/*')
    report = Report_Jishuitan()
    # report = Report_Kongyoki()
    # report = Report_Plot()
    report.process()
