#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure, SubplotParams
from matplotlib.widgets import Button
import numpy as np

from fft import FFT


class Monophonic(FigureCanvas):
    def __init__(self, parent=None, width=500, height=400, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi,
                          subplotpars=SubplotParams(left=0.04, right=0.96, bottom=0.1, top=0.98, hspace=0.1))

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        self.channel = self.fig.add_subplot(111)
        self.audio = None

        self.button_spectrum = Button(self.fig.add_axes([0.85, 0.01, 0.1, 0.05]), 'spectrum')

        self.modify = False
        self.paint()

    def __del__(self):
        self.mpl_disconnect(self.wave_scroll)

    def paint(self):
        pass

    def isModified(self):
        return self.modify

    def extract_pressure(self, file_name):
        index_r_d_r = [6, 7, 0, 1, 3, 4, 5, 2]
        index_l_d_r = [1, 0, 6, 7, 5, 2, 3, 4]
        data = np.fromfile(file_name, dtype='u1')
        num = len(data) // 508
        audio = np.empty((num, 40), dtype='u1')
        end = 444
        i = 0
        while i < num:
            np.copyto(audio[i], data[end - 40: end])
            end += 508
            i += 1
        audio = audio.reshape(-1)
        type_foot = index_r_d_r
        file_name = file_name[:-4]
        if file_name[-4:] == 'left':
            type_foot = index_l_d_r
        data_t = []
        for i in range(8):
            data_t.append(audio[type_foot[i]::8])
        return data_t

    def open(self, file_name):
        index_c = ['k', 'r', 'tan', 'orange', 'm', 'b', 'g', 'yellow']
        # self.fft = FFT()
        self.audio = self.extract_pressure(file_name)
        self.channel.cla()
        self.channel.set_ylim(0,180)
        for i in range(len(self.audio)):
            self.channel.plot(self.audio[i], color=index_c[i])
        # self.frequency, self.frame, self.spectrum = self.fft.spectrogram_energy(self.audio)
        # self.spectrumT = np.sqrt(self.spectrum.T)
        # self.spectrumT = np.sqrt(self.spectrum)

        self.xlim_left = 0
        self.xlim_right = len(self.audio)/8
        self.channel.set_xlim(0, self.xlim_right)
        self.iswave = True

        self.wave_scroll = self.mpl_connect('scroll_event', self.scroll)
        self.button_spectrum.on_clicked(self.periodogram)

    def save(self):
        pass

    def periodogram(self, event):
        self.channel.cla()
        if self.iswave:
            self.channel.pcolormesh(self.frame, self.frequency, self.spectrumT)
            self.iswave = False
        else:
            self.channel.plot(self.audio, color='blue')
            self.iswave = True
        self.channel.set_xlim(self.xlim_left, self.xlim_right)
        self.draw()

    def scroll(self, event):
        if event.xdata and event.ydata:
            scale = 1.5 ** -event.step
            temp = event.xdata * (1 - scale)
            self.xlim_left = temp + scale * self.xlim_left
            self.xlim_right = temp + scale * self.xlim_right
            self.channel.set_xlim(self.xlim_left, self.xlim_right)
            self.draw()

    def mark(self, channel, marks):
        for step in marks:
            channel.axvline(marks[step]['heel-on'], color='firebrick')
            channel.axvline(marks[step]['toe-on'], color='magenta')
