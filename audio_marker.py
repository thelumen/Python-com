#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pyaudio
import json
import re
from PyQt5.QtWidgets import QApplication
from matplotlib.widgets import SpanSelector, Button

from window import Window
from monophonic import Monophonic

class Marker(Monophonic):
    def __init__(self, parent=None):
        Monophonic.__init__(self, parent)

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt8, channels=1, rate=8000, output=True)

        self.button_play = Button(self.fig.add_axes([0.05, 0.01, 0.1, 0.05]), 'play')
        self.button_friction = Button(self.fig.add_axes([0.25, 0.01, 0.1, 0.05]), 'friction')
        self.button_footstep = Button(self.fig.add_axes([0.45, 0.01, 0.1, 0.05]), 'footstep')
        self.button_negative = Button(self.fig.add_axes([0.65, 0.01, 0.1, 0.05]), 'negative')

    def __del__(self):
        Monophonic.__del__(self)
        self.stream.close()
        self.p.terminate()

    def open(self, file_name):
        # if re.match('.*?\d{10}\_(?:left|right)\.dat', file_name):
        super().open(file_name)
        self.mark = self.channel.twinx()
        self.marks = {'friction': [], 'footstep': [], 'negative': []}
        self.mark_file = file_name.replace('.dat', '.json')
        self.last_select = None
        self.span = SpanSelector(self.mark, self.select, 'horizontal', span_stays=True, useblit=False, rectprops=dict(alpha=0.5, facecolor='red'))
        self.button_play.on_clicked(self.playAudio)
        self.button_footstep.on_clicked(self.footstep)
        self.button_friction.on_clicked(self.friction)
        self.button_negative.on_clicked(self.negative)
        self.draw()

    def save(self):
        data = json.dumps(self.marks)
        outfile = open(self.mark_file, 'w')
        outfile.write(data)
        outfile.close()

    def select(self, xmin, xmax):
        xmin = int(xmin)
        xmax = int(xmax)
        self.len_select = xmax - xmin
        self.last_select = (xmin, xmax)
        self.audio_select = self.audio[xmin: xmax]


    def playAudio(self, event):
        if self.len_select:
            self.stream.write(self.audio_select, self.len_select)

    def friction(self, event):
        if self.last_select:
            self.marks['friction'].append(self.last_select)
            self.mark.axvline(self.last_select[0], color='firebrick')
            self.mark.axvline(self.last_select[1], color='tomato')
            self.last_select = None

    def footstep(self, event):
        if self.last_select:
            self.marks['footstep'].append(self.last_select)
            self.mark.axvline(self.last_select[0], color='chartreuse')
            self.mark.axvline(self.last_select[1], color='aqua')
            self.last_select = None

    def negative(self, event):
        if self.last_select:
            self.marks['negative'].append(self.last_select)
            self.mark.axvline(self.last_select[0], color='darkgoldenrod')
            self.mark.axvline(self.last_select[1], color='lightsalmon')
            self.last_select = None

class App(Window):
    def getCanvas(self):
        return Marker(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    win = App()
    sys.exit(app.exec_())
