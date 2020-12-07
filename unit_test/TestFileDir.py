# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 13:42:05 2020

@author: Surface
"""
import pathlib

def getDir():
    directory = pathlib.Path(__file__).parents[0]
    return directory / "test_files"