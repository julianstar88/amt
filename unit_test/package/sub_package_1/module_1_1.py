# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 22:38:56 2020

@author: Surface
"""
# relative import form current sub_package
from . import module_1_2 as m12
from .module_1_3 import dummy_1_3_1, func_1_3_1

# relative import from parent package
from ..sub_package_2 import module_2_2 as m22
from ..sub_package_2.module_2_3 import func_2_3_1, dummy_2_3_2


class dummy_1_1_1():

    def __init__(self):
        pass

class dummy_1_1_2():

    def __init__(self):
        pass

class dummy_1_1_3():

    def __init__(self):
        pass

def func_1_1_1():
    pass

def func_1_1_2():
    pass

def func_1_1_3():
    pass

if __name__ == "__main__":
    dummyObj1 = m22.dummy_2_2_1()