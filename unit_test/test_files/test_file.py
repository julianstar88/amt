# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 23:09:55 2020

@author: Surface
"""

# normal imports
import ast
import numpy as np, sqlite3 as lite
import sys
import pathlib
import package.sub_package_2.module_2_1 as m21

# module contains absolute imports
import package.sub_package_3.module_3_1


# star imports
from tempfile import *

# from imports
from PyQt5 import QtWidgets, QtGui, QtCore
from package.sub_package_1.module_1_2 import dummy_1_2_1 as d121, func_1_2_3
from os import (chdir, getppid, getcwd,
                fsdecode, fspath, getenv)
from math import ceil as c, copysign, fsum as s

# module contains relative imports
from package.sub_package_1 import module_1_1



def dummyFunc():
    pass

def dummyFunc2(arg1, arg2, arg3):
    print(arg1)
    print(arg2)
    print(arg3)

def dummyFunc3(*args):
    for arg in args:
        print(arg)

class dummyClass(QtWidgets.QMainWindow):

    def __init__(self, *args):
        super().__init__(*args)

        text = """
        This Window has been created by test_file.py. It´s purpose is to test
        the amt-module with various import-commands, object- and function
        calls. one of the object calls creates this window
        """
        self.timer = QtCore.QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(5*1e3)
        self.timer.timeout.connect(self.closeWindow)

        self.main = QtWidgets.QWidget()
        self.sub1 = QtWidgets.QLabel(text)
        self.layout = QtWidgets.QGridLayout(self.main)

        self.layout.addWidget(self.sub1, 0, 0, QtCore.Qt.AlignCenter)

        self.setCentralWidget(self.main)
        self.setWindowTitle("unittest: amt-module")
        self.setGeometry(400, 300, 600, 200)
        self.show()

        self.timer.start()

    def closeWindow(self, *args):
        self.deleteLater()

dummyFuncCall = dummyFunc()

qapp = QtWidgets.QApplication(sys.argv)
dummyClassTest = dummyClass()
qapp.exec()
# sys.exit(qapp.exec())

# test of package and subpackages
modObj1 = m21.dummy_2_1_1()
modObj2 = module_1_1.dummy_1_1_2()

modFunc1 = m21.func_2_1_3()
modFunc2 = module_1_1.func_1_1_2()

with TemporaryDirectory() as tmpdir:
    pass

if __name__ == "__main__":
    print(dummyFuncCall)