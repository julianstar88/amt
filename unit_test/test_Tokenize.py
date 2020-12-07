# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 22:42:58 2020

@author: Surface
"""
import unittest

# project related modules
import TestFileDir
import Tokenizer

class TestTokenCategorizer(unittest.TestCase):
    """
    by testing the TokenCategory-object (all getter and setter methods),
    almost all properties and methods of the TokenCategorizer-class
    have been tested implicitly

    tested by testing the catagorizer-obj:
      - file / setFile
      - tokenCategories/ setTokenCategories
      - tokenizeScript
      - process_tokenized_script_helper
      - setFileEncoding

    the methods which are not tested by testing the categorizer-obj
    have to be tested explitcity:
      - fileEncoding

    functions which are not tested by testing the categorizer-obj also have to
    be tested explicitly
        - untokenize
    """
    def setUp(self):
        file = TestFileDir.getDir() / "test_file.py"
        self.categoryKeys = [
                "_assignments",
                "_classdefs",
                "_fromImports",
                "_funcdefs",
                "_normalImports",
                "_other",
                "_relativeImports"
            ]
        self.categorizerObj = Tokenizer.TokenCategorizer(file)
        self.assignmentLength = 12
        self.classdefsLength = 1
        self.fromImportsLength = 6
        self.funcdefsLength = 5
        self.normalImportsLength = 6
        self.otherLength = 31
        self.relativeImportsLength = 0
        self.expectedFileEncoding = "utf-8"
        self.expectedUntokenizedStr = "def dummyFunc():"

    # test the categorizer-object
    def testCategoryKeys(self):
        for key in self.categorizerObj.tokenCategories.__dict__.keys():
            with self.subTest(key = key):
                self.assertIn(key, self.categoryKeys)

    def testAssignments(self):
        assignments = self.categorizerObj.tokenCategories.assignments
        self.assertIsInstance(assignments, list)
        self.assertEqual(len(assignments), self.assignmentLength)

    def testClassdefs(self):
        classdefs = self.categorizerObj.tokenCategories.classdefs
        self.assertIsInstance(classdefs, list)
        self.assertEqual(len(classdefs), self.classdefsLength)

    def testFromImports(self):
        fromImports = self.categorizerObj.tokenCategories.fromImports
        self.assertIsInstance(fromImports, list)
        self.assertEqual(len(fromImports), self.fromImportsLength)

    def testFuncdefs(self):
        funcdefs = self.categorizerObj.tokenCategories.funcdefs
        self.assertIsInstance(funcdefs, list)
        self.assertEqual(len(funcdefs), self.funcdefsLength)

    def testNormalImports(self):
        normalImports = self.categorizerObj.tokenCategories.normalImports
        self.assertIsInstance(normalImports, list)
        self.assertEqual(len(normalImports), self.normalImportsLength)

    def testOther(self):
        other = self.categorizerObj.tokenCategories.other
        self.assertIsInstance(other, list)
        self.assertEqual(len(other), self.otherLength)

    def testRelativeImports(self):
        relativeImports = self.categorizerObj.tokenCategories.relativeImports
        self.assertIsInstance(relativeImports, list)
        self.assertEqual(len(relativeImports), self.relativeImportsLength)

    # test the remaining method of the TokenCategorizer-class
    def testFileEncodingGetter(self):
        self.assertEqual(
                self.categorizerObj.fileEncoding,
                self.expectedFileEncoding
            )

    # test the untokenize-function of the Tokenizer-module
    def testUntokenize(self):
        tokenStatement = self.categorizerObj.tokenCategories.funcdefs[0]
        self.assertEqual(
                Tokenizer.untokenize(tokenStatement),
                self.expectedUntokenizedStr
            )

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()