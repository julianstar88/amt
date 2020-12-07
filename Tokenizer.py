"""
Created on Thu Apr 30 18:11:28 2020

@author: Julian

The Tokenizer-Module is considerd to be a helper module for the AMT-Module

USAGE:

    1. to categorize a file just instanciate a TokenCategorizer

        >>> categoizerObj = TokenCategorizer(file)

        either directly with a file as input for TokenCategorizer
        or...

    2. ...call the method tokenizeScript(file) wiht the file to be categorized as
       input.

       >>> categorizer.tokenizeScript(file)

    the untokenize-function restores the line of file, which is represented by
    a token. call it with a token as input

    line = untokenize(token)

    token is a tokenType-named-Tuple out of the standard-library-module tokeniz

"""
import copy
import keyword
import pathlib
import re
import tokenize


class TokenCategorizer():
    """
    the TokenCategorizerClass is the main class of the Tokenizer-Module. It´s
    purpose is to categorize the the tokens of a tokenized file into the

    following categories:
        - assignments: all tokens with include the Tokentype: EQUAL
        - classdef: all tokens which include the Keyword: class
        - funcdefs: all tokens which include the keyword: def
        - other: all tokens which do not fit into the above categories (include
          for example used constants)

    the properties of this class are:
        - file: the file which will be tokenized and categorized
        - fileEncoding: encoding of the tokenized and categorized file
        - tokenCategories: instance of the TokenCategories-class containing the
          above mentioned categories

    public methods:
        - tokenizeScript(file)

    private method:
        - __categorize_helper(element): helps categorizing the tokens of a
          tokenized file

    """
    assignmentKeyword = "="
    classdefKeyword = "class"
    funcdefKeyword = "def"
    importKeywords = ("import", "from")

    def __init__(self, file = None):
        self._file = None
        self._fileEncoding = None
        self._tokenCategories = None

        if file:
            self.file = file

        if self.file:
            self.tokenizeScript(self.file)

    def __categorize_helper(self, element):
        """
        helper method for the token-categorization
        """
        assignments = list()
        classdefs = list()
        fromImports = list()
        funcdefs = list()
        normalImports = list()
        other = list()
        relativeImports = list()

        if [True for tok in element if type(self).assignmentKeyword in tok]:
            assignments.append(element)
        elif [True for tok in element if type(self).classdefKeyword in tok]:
            classdefs.append(element)
        elif [True for tok in element if type(self).funcdefKeyword in tok]:
            funcdefs.append(element)
        elif [True for tok in element if type(self).importKeywords[0] in tok]:  # import keywort in element
            if [True for tok in element if type(self).importKeywords[1] in tok]: # from keywort in element

                # identify relative imports
                collect = False
                testName = str()
                pattern = "(^\.+)(\w*)"
                for tok in element:
                    if tok[1] == type(self).importKeywords[1]:
                        collect = True
                        continue
                    elif tok[1] == type(self).importKeywords[0]:
                        break
                    if collect:
                        testName += tok[1]

                # decide wether or not element belongs to an relative import
                if re.search(pattern, testName):
                    relativeImports.append(element)
                else:
                    fromImports.append(element)
            else:
                normalImports.append(element)
        else:
            other.append(element)

        categorized = (
                assignments,
                classdefs,
                fromImports,
                funcdefs,
                normalImports,
                other,
                relativeImports
            )
        return categorized

    def file(self):
        return self._file

    def fileEncoding(self):
        return self._fileEncoding

    def process_tokenized_script_helper(self, tokenized_script):
        stack = list()
        braces = {
                "(": ")",
                "[": "]",
                "{": "}"
            }
        out = TokenCategories()
        aux = list()
        tokenValues = copy.deepcopy(tokenized_script)
        while tokenValues:
            tok = tokenValues.pop(0)
            if tok[0] != "NEWLINE" and tok[0] != "NL":

                # handle multi-line import statements with braces
                if tok[1] in braces:
                    stack.append(tok)
                elif tok[1] in braces.values():
                    stack.pop()

                aux.append(tok)
            else:

                # if stack is true, then we have to wait until a
                # closing brace occures
                if stack:
                    continue

                if aux:
                    categorized = self.__categorize_helper(aux)
                    if categorized[0]:
                        out.assignments.extend(categorized[0])
                    if categorized[1]:
                        out.classdefs.extend(categorized[1])
                    if categorized[2]:
                        out.fromImports.extend(categorized[2])
                    if categorized[3]:
                        out.funcdefs.extend(categorized[3])
                    if categorized[4]:
                        out.normalImports.extend(categorized[4])
                    if categorized[5]:
                        out.other.extend(categorized[5])
                    if categorized[6]:
                        out.relativeImports.extend(categorized[6])
                aux = []
        return out

    def setFile(self, file):
        if not isinstance(file, pathlib.Path):
            raise TypeError(
                    "input for 'file' does not match {type_name}".format(
                            type_name = pathlib.Path
                        )
                )
        self._file = file

    def setFileEncoding(self, encoding):
        if not isinstance(encoding, str):
            raise TypeError(
                    "input for 'encoding' does not match {type_name}".format(
                            type_name = str
                        )
                )
        self._fileEncoding = encoding

    def setTokenCategories(self, categories):
        if not isinstance(categories, TokenCategories):
            raise TypeError(
                    "input for 'categories' does not match {type_name}".format(
                            type_name = TokenCategories
                        )
                )
        self._tokenCategories = categories

    def tokenCategories(self):
        return self._tokenCategories

    def tokenizeScript(self, file):
        result = list()
        try:
            with open(file, "br") as f:
                for tok in tokenize.tokenize(f.readline):
                    tokType = tokenize.tok_name[tok.exact_type]
                    if tokType == "NAME":
                        if keyword.iskeyword(tok.string):
                            tokType = "KEYWORD"
                    if tokType == "ENCODING":
                        self.fileEncoding = tok.string
                    aux = [
                            tokType,
                            tok.string,
                            tok.start,
                            tok.end,
                        ]
                    result.append(aux)
                self.tokenCategories = self.process_tokenized_script_helper(result)
        except SyntaxError:
            raise TypeError(
                    "cant open the file <{name}>".format(
                            name = file
                        )
                )

    file = property(file, setFile)
    fileEncoding = property(fileEncoding, setFileEncoding)
    tokenCategories = property(tokenCategories, setTokenCategories)

class TokenCategories():

    def __init__(self):
        self._assignments = list()
        self._classdefs = list()
        self._fromImports = list()
        self._funcdefs = list()
        self._normalImports = list()
        self._other = list()
        self._relativeImports = list()

    def assignments(self):
        return self._assignments

    def classdefs(self):
        return self._classdefs

    def fromImports(self):
        return self._fromImports

    def funcdefs(self):
        return self._funcdefs

    def normalImports(self):
        return self._normalImports

    def other(self):
        return self._other

    def relativeImports(self):
        return self._relativeImports

    def setAssignments(self, assignments):
        if not isinstance(assignments, list):
            raise TypeError(
                    "input <{err_name}> for 'assignments' does not match {type_name}".format(
                            err_name = str(assignments),
                            type_name = list
                        )
                )
        self._assignments = assignments

    def setClassdefs(self, classdefs):
        if not isinstance(classdefs, list):
            raise TypeError(
                    "input <{err_name}> for 'classdefs' does not match {type_name}".format(
                            err_name = str(classdefs),
                            type_name = list
                        )
                )
        self._classdefs = classdefs

    def setFromImports(self, fromImports):
        if not isinstance(fromImports, list):
            raise TypeError(
                    "input <{err_name}> for 'fromImports' does not match {type_name}".format(
                            err_name = str(fromImports),
                            type_name = list
                        )
                )
        self._fromImports = fromImports

    def setFuncdefs(self, funcdefs):
        if not isinstance(funcdefs, list):
            raise TypeError(
                    "input <{err_name}> for 'funcdefs' does not match {type_name}".format(
                            err_name = str(funcdefs),
                            type_name = list
                        )
                )
        self._funcdefs = funcdefs

    def setNormalImports(self, normalImports):
        if not isinstance(normalImports, list):
            raise TypeError(
                    "input <{err_name}> for 'normalImports' does not match {type_name}".format(
                            err_name = str(normalImports),
                            type_name = list
                        )
                )
        self._normalImports = normalImports

    def setOther(self, other):
        if not isinstance(other, list):
            raise TypeError(
                    "input <{err_name}> for 'other' does not match {type_name}".format(
                            err_name = str(other),
                            type_name = list
                        )
                )
        self._other = other

    def setRelativeImports(self, relativeImports):
        if not isinstance(relativeImports, list):
            raise TypeError(
                    "input <{err_name}> for 'relativeImports' does not match {type_name}".format(
                            err_name = str(relativeImports),
                            type_name = list
                        )
                )
        self._relativeImports = relativeImports

    assignments = property(assignments, setAssignments)
    classdefs = property(classdefs, setClassdefs)
    fromImports = property(fromImports, setFromImports)
    funcdefs = property(funcdefs, setFuncdefs)
    normalImports = property(normalImports, setNormalImports)
    other = property(other, setOther)
    relativeImports = property(relativeImports, setRelativeImports)

def untokenize(tokenStatement):
    commandStatement = str()
    for tok in tokenStatement:
        if tok[0] == "EQUAL" or tok[0] == "OP":
            partition = " {} ".format(tok[1])
        elif tok[1] == "class" or tok[1] == "def":
            partition = "{} ".format(tok[1])
        elif tok[0] == "KEYWORD" and tok[0] != "class" and tok[0] != "def":
            partition = " {} ".format(tok[1])
        else:
            partition = tok[1]
        commandStatement += partition
    return commandStatement


if __name__ == "__main__":
    pass
