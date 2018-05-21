#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure, SubplotParams
from matplotlib.widgets import Button
# from Energy import Energy
import numpy as np

class Binaural(FigureCanvas):
	def __init__(self, parent=None, width=500, height=400, dpi=100):
		subplotpars = SubplotParams(left=0.0, right=1.0, bottom=0.15, top=0.85, hspace=0.18)
		self.fig = Figure(figsize=(width, height), dpi=dpi, subplotpars=subplotpars)

		FigureCanvas.__init__(self, self.fig)
		self.setParent(parent)

		self.left_channel = self.fig.add_subplot(211)
		self.right_channel = self.fig.add_subplot(212)

		self.button_spectrum = Button(self.fig.add_axes([0.85, 0.03, 0.1, 0.07]), 'spectrum')
		self.button_shift_1 = Button(self.fig.add_axes([0.03, 0.03, 0.1, 0.07]), '<<<<')
		self.button_shift_2 = Button(self.fig.add_axes([0.13, 0.03, 0.1, 0.07]), '<<<')
		self.button_shift_3 = Button(self.fig.add_axes([0.23, 0.03, 0.1, 0.07]), '<<')
		self.button_shift_4 = Button(self.fig.add_axes([0.33, 0.03, 0.1, 0.07]), '<')
		self.button_shift_5 = Button(self.fig.add_axes([0.43, 0.03, 0.1, 0.07]), '>')
		self.button_shift_6 = Button(self.fig.add_axes([0.53, 0.03, 0.1, 0.07]), '>>')
		self.button_shift_7 = Button(self.fig.add_axes([0.63, 0.03, 0.1, 0.07]), '>>>')
		self.button_shift_8 = Button(self.fig.add_axes([0.73, 0.03, 0.1, 0.07]), '>>>>')

		# self.energy = Energy()
		self.left_channel_length = 0
		self.right_channel_length = 0
		self.shift = 0

		self.modify = False
		self.paint()

	def paint(self):
		pass

	def done(self):
		self.xlim_left = 0
		self.xlim_right = min(self.left_channel_length, self.right_channel_length)
		self.left_channel.set_xlim(0, self.xlim_right)
		self.right_channel.set_xlim(0, self.xlim_right)
		self.iswave = True

		self.wave_scroll = self.mpl_connect('scroll_event', self.scroll)
		self.button_shift_1.on_clicked(self.shift1)
		self.button_shift_2.on_clicked(self.shift2)
		self.button_shift_3.on_clicked(self.shift3)
		self.button_shift_4.on_clicked(self.shift4)
		self.button_shift_5.on_clicked(self.shift5)
		self.button_shift_6.on_clicked(self.shift6)
		self.button_shift_7.on_clicked(self.shift7)
		self.button_shift_8.on_clicked(self.shift8)
		self.button_spectrum.on_clicked(self.spectrum)

	def save(self):
		self.mpl_disconnect(self.wave_scroll)

	def setModify(self, modify):
		if modify != self.modify:
			self.modify = modify

	def isModified(self):
		return self.modify

	def mark(self, channel, marks):
		for step in marks:
			channel.axvline(marks[step]['heel-on'], color='firebrick')
			channel.axvline(marks[step]['toe-on'], color='magenta')

	def mark2(self, left_channel, right_channel, marks):
		for step in marks:
			mark = marks[step]
			if mark['foot'] == 'left':
				self.left_mark.axvline(mark['heel-on'], linewidth=2, color='black')
				self.left_mark.axvline(mark['toe-on'], color='black')
			elif mark['foot'] == 'right':
				self.right_mark.axvline(mark['heel-on'], linewidth=2, color='black')
				self.right_mark.axvline(mark['toe-on'], color='black')

	def spectrum(self, event):
		self.left_channel.cla()
		self.right_channel.cla()
		if self.iswave:
			self.left_channel.pcolormesh(self.left_frame, self.left_frequency, np.log(self.left_spectrum))
			self.right_channel.pcolormesh(self.right_frame, self.right_frequency, np.log(self.right_spectrum))
			self.iswave = False
		else:
			self.left_channel.plot(self.left_pcm, color='blue')
			self.right_channel.plot(self.right_pcm, color='blue')
			self.iswave = True
		self.left_channel.set_xlim(self.xlim_left, self.xlim_right)
		self.right_channel.set_xlim(self.xlim_left + self.shift, self.xlim_right + self.shift)
		self.draw()

	def scroll(self, event):
		if event.xdata and event.ydata:
			scale = 1.5 ** -event.step
			temp = event.xdata * (1 - scale)
			self.xlim_left = temp + scale * self.xlim_left
			self.xlim_right = temp + scale * self.xlim_right
			self.left_channel.set_xlim(self.xlim_left, self.xlim_right)
			self.right_channel.set_xlim(self.xlim_left + self.shift, self.xlim_right + self.shift)
			self.draw()

	def shift1(self, event):
		self.shift += 1000
		self.right_channel.set_xlim(self.xlim_left + self.shift, self.xlim_right + self.shift)
		self.draw()

	def shift2(self, event):
		self.shift += 100
		self.right_channel.set_xlim(self.xlim_left + self.shift, self.xlim_right + self.shift)
		self.draw()

	def shift3(self, event):
		self.shift += 10
		self.right_channel.set_xlim(self.xlim_left + self.shift, self.xlim_right + self.shift)
		self.draw()

	def shift4(self, event):
		self.shift += 1
		self.right_channel.set_xlim(self.xlim_left + self.shift, self.xlim_right + self.shift)
		self.draw()

	def shift5(self, event):
		self.shift -= 1
		self.right_channel.set_xlim(self.xlim_left + self.shift, self.xlim_right + self.shift)
		self.draw()

	def shift6(self, event):
		self.shift -= 10
		self.right_channel.set_xlim(self.xlim_left + self.shift, self.xlim_right + self.shift)
		self.draw()

	def shift7(self, event):
		self.shift -= 100
		self.right_channel.set_xlim(self.xlim_left + self.shift, self.xlim_right + self.shift)
		self.draw()

	def shift8(self, event):
		self.shift -= 1000
		self.right_channel.set_xlim(self.xlim_left + self.shift, self.xlim_right + self.shift)
		self.draw()