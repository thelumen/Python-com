#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
from PyQt5.QtWidgets import QApplication

from window import Window
from monophonic import Monophonic
from audio_feature import *


class Predictor(Monophonic):
    def __init__(self, parent=None):
        Monophonic.__init__(self, parent)

    def open(self, file_name):
        if re.match('.*?\d{10}\_(?:left|right)\.dat', file_name):
            super().open(file_name)
            self.X, self.y = data_scale(self.spectrum)
            self.model = load_model()
            proba = predict_proba(self.model, self.X)
            start = self.fft.window >> 1
            frame = np.arange(start, start + len(proba) * self.fft.shift, self.fft.shift)
            self.mark = self.channel.twinx()
            self.mark.set_ylim(-1, 2)
            self.mark.plot(frame, proba[:, 0], 'red')
            self.draw()


class App(Window):
    def getCanvas(self):
        return Predictor(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    win = App()
    sys.exit(app.exec_())
