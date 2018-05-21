#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import glob
import subprocess
import numpy as np
from sklearn import svm
from sklearn.datasets import load_svmlight_file, dump_svmlight_file
from sklearn.externals import joblib

from fft import FFT


def load_model():
    return joblib.load('pkl/model.pkl')


def fit_proba(C, gamma, X, y):
    clf = svm.SVC(C=C, kernel='rbf', gamma=gamma, probability=True)
    clf.fit(X, y)
    joblib.dump(clf, 'pkl/model.pkl')
    return clf


def predict_proba(model, X):
    return model.predict_proba(X)


def data_scale(spectrum):
    label = np.zeros(len(spectrum))
    dump_svmlight_file(spectrum, label, 'data/single.dat', zero_based=False)
    cmd = ['/home/zhoulong/CodeBlocks/libsvm-3.22/svm-scale', '-r', 'data/scale', 'data/single.dat']
    with open('data/single.scale', 'w') as out:
        subprocess.check_call(cmd, stdout=out)
    return load_svmlight_file('data/single.scale')


def generate_svmlight_file(folder):
    fft = FFT()
    files = glob.glob(folder + '.json')
    for f in files:
        json_file = open(f, 'r')
        marks = json.load(json_file)
        json_file.close()
        audio = fft.extract_audio(f.replace('.json', '.dat'))
        features = fft.spectrogram_energy(audio)[2]
        labels = {'friction': [0], 'negative': [1], 'footstep': [1]}
        X = []
        y = []
        for key, value in marks.items():
            label = labels[key]
            for start, end in value:
                start = fft.frame_index(start)
                end = fft.frame_index(end) + 1
                X.extend(features[start: end])
                y.extend(label * (end - start))
        dump_svmlight_file(np.array(X), np.array(y), f.replace('.json', '.svm'), zero_based=False)


if __name__ == '__main__':
    # folder = '/home/zhoulong/Data/zkhc/2017-12-16/*'
    # generate_svmlight_file(folder)
    # cat *.svm >> out.svm

    X, y = load_svmlight_file('/home/zhoulong/CodeBlocks/libsvm-3.22/tools/out.scale')
    fit_proba(2.0, 0.125, X, y)
