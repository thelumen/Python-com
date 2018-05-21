#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scipy.signal import spectrogram
import numpy as np
from numpy.ctypeslib import ndpointer
import math

class FFT():
    def __init__(self):
        self.window = 128
        self.shift = 64
        self.lib = np.ctypeslib.load_library('attitude.so', 'c')
        self.lib.init_fft(4000)
        self.periodogram = self.lib.periodogram
        self.periodogram.argtypes = [ndpointer(dtype=np.float64, ndim=1, flags='C_CONTIGUOUS'), ndpointer(dtype=np.float64, ndim=1, flags='C_CONTIGUOUS')]
        self.periodogram.restype = None

    def __del__(self):
        pass

    def extract_audio(self, file_name):
        data = np.fromfile(file_name, dtype='i1')[508 * 4 :]
        num = len(data) // 508
        audio = np.empty((num, 400), dtype='i1')
        end = 404
        i = 0
        while i < num:
            np.copyto(audio[i], data[end - 400 : end])
            end += 508
            i += 1
        return audio.reshape(-1)

    def extract_audio_1(self, file_name):
        data = np.fromfile(file_name, dtype='i1')
        num = len(data) // 240
        audio = np.empty((num, 200), dtype='i1')
        end = 240
        i = 0
        while i < num:
            np.copyto(audio[i], data[end - 200 : end])
            end += 240
            i += 1
        return audio.reshape(-1)

    def extract_audio_2(self, file_name):
        return np.fromfile(file_name, dtype='<i2')[2000 :]

    def spectrogram_energy(self, audio):
        frequency_num = self.window // 2 + 1
        frequency = np.linspace(0.0, 0.5, frequency_num)
        length = len(audio)
        frame_num = (length - self.window) // self.shift + 1
        start = self.window >> 1
        frame = np.arange(start, start + frame_num * self.shift, self.shift)
        spectrum = np.empty((frame_num, frequency_num), dtype=np.float64)
        one = np.empty(self.window + 2, dtype=np.float64)
        end = self.window
        i = 0
        while end <= length:
            np.copyto(one[0 : self.window], audio[end - self.window : end])
            self.periodogram(one, spectrum[i])
            end += self.shift
            i += 1
        return frequency, frame, spectrum

    def spectrogram_paint(self, audio):
        return spectrogram(audio, 1, 'hann', self.window, self.window - self.shift, scaling='spectrum')

    def frame_index(self, index):
        return (index - (self.window >> 1)) // self.shift

if __name__ == '__main__':
    fft = FFT()
    a = np.empty(130, dtype=np.float64)
    for i in range(0, 128):
        a[i] = math.cos(i) - 0.1
    b = np.empty(65, dtype=np.float64)
    fft.periodogram(a, b)
    # print(10 * np.log10(b))
    print(b)
    a = np.empty(128, dtype=np.float64)
    for i in range(0, 128):
        a[i] = math.cos(i) - 0.1
    a -= np.mean(a)
    c = np.fft.rfft(a)
    # print(c)
    t = np.fromfile('/home/zhoulong/Sublime/data/out.pcm', dtype='<i1')[2000:]
    # c = np.fft.rfft(t[0 : 128])
    # print(c)
    # one = np.array(t[0 : 130], dtype=np.float64)
    # spectrum = np.empty(65, dtype=np.float64)
    # fft.periodogram(one, spectrum)
    # print(spectrum)

    x, y, z = fft.spectrogram_paint(t)
    print(z[:, 0])
