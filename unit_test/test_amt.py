# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 22:43:13 2020

@author: Surface
"""
import amt
import filecmp
import pathlib
import tempfile
import TestFileDir
import unittest

class TestAmt(unittest.TestCase):
    """
    the test of the amt-module is limited to the test of the amt-class. all
    other classes (BaseResult and its descendants) as well as all functions
    contained in the amt-module are uesed and therefore tested by the test of
    the parse-function

    methods of the amt-class to be tested:
        - findObjects
        - inspectTree
        - parentObject
        - printTree

    methods of amt-class which are tested implicitly by the parsing process:
        - __find_parent_object
        - __find_single_parent
        - root/ setRoot

    all of these methods are usually not invoked by the user. they are used
    internally to populate an instance of the amt-class. the methods of the
    amt-class which should be tested (see above) are likely to be called by a
    user and thus we have to make sure they are producing expected results.
    """

    def setUp(self):
        file = TestFileDir.getDir() / "test_file.py"
        self.tree = amt.parse(file, toStdOut = False)

    def testFindModuleObjects(self):
        rootObj = self.tree.root
        objects = self.tree.findModuleObjects("package", rootObj, list())
        objectsLength = 12
        objectNames = [val.name for val in objects]
        expectedNames = [
                "package.sub_package_2.module_2_1",
                "package.sub_package_3.module_3_1",
                "package.sub_package_2.module_2_2",
                "package.sub_package_2.module_2_3",
                "package.sub_package_3.module_3_2",
                "package.sub_package_3.module_3_3",
                "package.sub_package_1.module_1_2",
                "package.sub_package_1.module_1_1",
                "package.sub_package_1.module_1_2",
                "package.sub_package_1.module_1_3",
                "package.sub_package_2.module_2_2",
                "package.sub_package_2"
            ]
        self.assertEqual(
                len(objects),
                objectsLength
            )

        for i, name in enumerate(expectedNames):
            with self.subTest(name = name):
                self.assertEqual(
                        objectNames[i],
                        name
                    )

    def testFindModuleCallable(self):
        rootObj = self.tree.root
        callables = self.tree.findModuleCallables("module_1_2", rootObj, list())
        callableNames = [val.name for val in callables]
        expectedCallablesLength = 2
        expectedNames = [
                "dummy_1_2_1",
                "func_1_2_3"
            ]

        self.assertEqual(
                len(callables),
                expectedCallablesLength
            )

        for i,name in enumerate(expectedNames):
            with self.subTest(name = name):
                self.assertEqual(
                        callableNames[i],
                        name
                    )

    def testInspectTree(self):
        inspectedTree = self.tree.inspectTree(self.tree)
        expectedHirachyLevels = 3
        expectedParentsLevel1 = ["test_file.py"]
        expectedParentsLevel2 = [
                "package.sub_package_2.module_2_1",
                "package.sub_package_3.module_3_1",
                "package.sub_package_1.module_1_2",
                "package.sub_package_1.module_1_1"
            ]
        expectedParentsLevel3 = [
                "package.sub_package_2.module_2_2",
                "package.sub_package_2.module_2_3",
                "package.sub_package_3.module_3_2",
                "package.sub_package_3.module_3_3",
                "package.sub_package_1.module_1_2",
                "package.sub_package_1.module_1_3",
                "package.sub_package_2.module_2_2",
                "package.sub_package_2"
            ]
        expectedParents = [
                expectedParentsLevel1,
                expectedParentsLevel2,
                expectedParentsLevel3
            ]

        self.assertEqual(len(inspectedTree), expectedHirachyLevels)

        for key in inspectedTree.keys():
            with self.subTest(key = key):
                parents = [val["parent"] for val in inspectedTree[key]]
                for i, par in enumerate(parents):
                    with self.subTest(par = par):
                        self.assertEqual(
                                par,
                                expectedParents[key - 1][i]
                            )

    def testParentObject(self):
        child = self.tree.root.children["modules"][0]
        expectedParentName = "test_file.py"

        self.assertEqual(
                self.tree.parentObject(child).name,
                expectedParentName
            )

    def testPrintTree(self):
        with tempfile.TemporaryDirectory() as tdir:
            testFile = pathlib.Path(tdir) / "test_tree.txt"
            expectedFile = TestFileDir.getDir() / "expected_result_tree.txt"
            self.tree.printTree(self.tree.root, file = testFile)

            self.assertTrue(
                    filecmp.cmp(testFile, expectedFile, shallow = False)
                )

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()