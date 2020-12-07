# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 23:26:53 2020

@author: Surface
"""
import amt
import TestFileDir

file = TestFileDir.getDir() / "test_file.py"
result = TestFileDir.getDir() / "expected_result_tree.txt"
tree = amt.parse(file)
tree.printTree(tree.root, file = result)
