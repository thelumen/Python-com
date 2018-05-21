#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QAction, QFileDialog
from PyQt5.QtGui import QIcon, QKeySequence

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('中科汇成')
        self.setWindowIcon(QIcon("images/logo.ico"))
        self.createActions()
        self.createToolBars()
        self.createStatusBar()

        self.canvas = self.getCanvas()
        self.canvas.setFocus()
        self.setCentralWidget(self.canvas)
 
        self.show()

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut=QKeySequence.Open,
            statusTip="Open an existing file", triggered=self.open)
        self.saveAct = QAction("&Save", self, shortcut=QKeySequence.Save,
            statusTip="Save the document to disk", triggered=self.save)
        self.aboutAct = QAction("&About", self,
            statusTip="Show the application's About box", triggered=self.about)

    def createToolBars(self):
        toolbar = self.addToolBar("File")
        toolbar.addAction(self.openAct)
        toolbar.addAction(self.saveAct)
        toolbar = self.addToolBar("About")
        toolbar.addAction(self.aboutAct)

    def createStatusBar(self):
        self.statusBar().showMessage("CopyRight 2017 All Right Reserved !", 2000)

    def getCanvas(self):
        pass

    def open(self):
        file_name, filtr = QFileDialog.getOpenFileName(self)
        if file_name:
            self.canvas.open(file_name)

    def save(self):
        self.canvas.save()

    def about(self):
        QMessageBox.about(self, "About", """Copyright 2017""")
