# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 22:15:13 2020

@author: Surface

AMT - Abstract Module Tree v1.0.0
(for python >= 3)

create a object oriented hirachy of the used modules in a script

usage:
    NOTE: if you want to scan a single file, or a file located in a project, make
    sure that this file or respectivly the project is on the PYTHONPATH.

    1. create a amt-object by calling the parse() function with the file which
    should be scanned as input.

    2a. once the amt-object has been created, there are several methods to
    inspect the tree-hirachy:

        - printTree
        - inspectTree

    2b. to obtain certain objects of the three-hirachy, use

        - findObjects()

        whith a single module name or a list of names as input

    2c. to obtain the root-object or change the the tree, call:
        - root() --> obtain root-object
        - setRoot(amt-object) --> change tree

        specifically setRoot() should only be called with another amt-object
        as input

    all classes, namly:
        - amt
        - BaseResult
        - Function
        - Class
        - Module
        - Usage

    and all helper-functions, namly:
        - determine_usage
        - find_all_indices
        - imported_modules
        - lokal_callables
        - split_list

    are not for public usage, they are internally called to create and representate
    the amt

    BUT: certain helper-functions can be useful:

        - imported_modules()
        - lokal_callables()

        they can be called with a Tokenizer.tokenCategorizer() object as input
        the first retunrs a list of imported modules und Callabels:
            [moduls, callables]
        the latter returns a list of locally defined functions and classes:
            [funcdefs, classdefs]

        - determine_usage(obj, stdLib)

        returns a list of usages (usage-object) of Module-object <obj>. the
        stdLib is a list of all avaliable standard-library-moduls shipped whith
        pyhton in extended wiht pypi or anaconda. stdLib can be obtained with
        the StandardModuleFile-function of the standard_library_finder module


NOTE: the Tokenizer-Module has to be in the same directory like AMT itself,
as some helper functions rely on the functionality of Tokenizer!

CHANGELOG:

"""
import os
import re
import inspect
import importlib
import copy
import pathlib
import standard_library_finder as stf
import Tokenizer as tokenizer

# third party functions
import progress_2  as progress
import standard_library_finder

class amt():

    def __init__(self):
        self._root = None

    def __find_parent_objects(self, searchObj, rootObj, res = list()):
        """
        find all objects in <rootObjects> which are named <searchObj.parent.stem>
        """

        # find all obj with the name: obj.parent.stem
        # if the obj doesn´t have ap parent, it is the root object and therefor
        # it is not further considered
        if searchObj.parent:
            val = searchObj.parent.stem
        else:
            val = None

        if val:
            if re.search(val, rootObj.name):
                res.append(rootObj)

        if rootObj.children:
            for rootObj in rootObj.children["modules"]:
                res = self.__find_parent_objects(searchObj, rootObj, res)

        return res

    def __find_single_parent(self, searchObj, modules):
        """
        find particulally this object in <modules> (list of all objects
        related to searchObj.parent), which has <searchObj> in his
        ~.children["moudles"]-list. this object is considered to be the direct
        parent of <searchObj>.
        """
        parent = None

        # find the tangible parent of obj in modules
        for mod in modules:
            if mod.children:
                for child in mod.children["modules"]:
                    if searchObj.name == child.name:
                        parent = mod

        return parent

    def findModuleCallables(self, objSearchPattern, rootObj, result):
        result = list()
        modules = self.findModuleObjects(objSearchPattern, rootObj, list())

        for mod in modules:
            parentObj = self.parentObject(mod)

            if parentObj:
                queryObj = parentObj
            else:
                queryObj = mod

            if queryObj.children:
                for call in queryObj.children["callables"]:
                    if call.module == mod.name:
                        result.append(call)

        return result

    def findModuleObjects(self, objSearchPattern, rootObj, result):
        """
        find all objects called <objName> which are in the tree-hirachy

        Parameters
        ----------
        objName : str, list or tupe
            names to be found in tree-hirachy of <rootObj>.
        rootObj : amt.tree
            a tree object used as search starting-point.
        result : list
            the found objects will be appended to this list so normally one
            would provide an empty list.

        Raises
        ------
        TypeError
            riased if:
                - objName: not str, not list and not tuple
                - rootObj: not instance of BaseResult

        Returns
        -------
        res : list
            all found modules.

        """

        if not isinstance(objSearchPattern, str) and \
        not isinstance(objSearchPattern, list) and \
        not isinstance(objSearchPattern, tuple):
            raise TypeError(
                    "input <{input_name}> does not match {type_name_1}, {type_name_2} or {type_name_3}".format(
                            input_name = str(objSearchPattern),
                            type_name_1 = str,
                            type_name_2 = list,
                            type_name_3 = tuple
                        )
                )

        if not isinstance(rootObj, BaseResult):
            raise TypeError(
                    "input <{input_name}> for 'rootObj' does not match {type_name}".format(
                            input_name = str(rootObj),
                            type_name = BaseResult
                        )
                )

        if not isinstance(result, list):
            raise TypeError(
                    "input <{input_name}> for 'list' does not match {type_name}".format(
                            input_name = str(result),
                            type_name = list
                        )
                )

        if isinstance(objSearchPattern, str):
            if re.search(objSearchPattern, rootObj.name) or re.search(rootObj.name, objSearchPattern):
                result.append(rootObj)
        elif isinstance(objSearchPattern, list) or isinstance(objSearchPattern, tuple):
            for name in objSearchPattern:
                if re.search(name, rootObj.name) or re.search(rootObj.name, name):
                    result.append(rootObj)

        # recursivley walk through module-tree
        if rootObj.children:
            for obj in rootObj.children["modules"]:
                result = self.findModuleObjects(objSearchPattern, obj, result)

        return result

    def inspectTree(self, tree):
        """
        inpsect the hirachy of amt.root. flattens the hirachy and returns a
        list of dicts representing the tree

        Parameters
        ----------
        tree : amt.tree

        Returns
        -------
        hirachy : dict
            tree-hirachy in form of a dict. the keys represent the levels of
            hirachy-depth. contents of this dict are:
                {
                    level1:

                    {parent: paretnobj, modules: list of childmodules},
                    {...},
                    {...}
                    .
                    .
                    .

                    level2:

                    {parent: paretnobj, modules: list of childmodules},
                    {...},
                    {...}
                    .
                    .
                    .

                    levelN:
                        .
                        .
                        .
                }
        """
        obj = tree.root
        level = 1
        moduleNames = [val.name for val in obj.children["modules"]]
        hirachy = {
                level: [
                        {"parent": obj.name, "modules": moduleNames}
                    ]
            }
        modules = obj.children["modules"]
        while True:
            level += 1
            aux_modules = list()
            aux_hirachy = list()
            for child in modules:
                if child.children:
                    moduleNames = [val.name for val in child.children["modules"]]
                    aux_hirachy.append(
                            {"parent": child.name, "modules": moduleNames}
                        )
                    aux_modules.extend(child.children["modules"])
            if aux_hirachy:
                hirachy[level] = aux_hirachy
            modules = aux_modules

            if not modules:
                break

        return hirachy

    def parentObject(self, child):
        """
        returns the parent-obj of <child>

        Parameters
        ----------
        child : BaseResult
            object which parent has to be found.

        Returns
        -------
        parent : BaseResult
        """
        parent = None
        modules = self.__find_parent_objects(child, self.root)

        if modules:
            parent = self.__find_single_parent(child, modules)
        else:
            parent = None

        return parent

    def printTree(self, obj, file = None, showModuleUsage = True, limit = None, level = -1):
        """
        print a string-representation of the amt-object eihter to stdout, or to
        a file, if <file> has been set

        Parameters
        ----------
        obj : amt.root
            root object of amt.

        file : pathlib.Path or str, optional
            a file to write the result of printTree.

        showModuleUsage : bool
            if true, the module tree is going to be extended by the usage of
            the modules, if module has been used. the default is True

        limit : int or None
            if the limit has been set, the amt is only going to be printed to
            the depth of 'limit'. the default is None.

        level : int, for internal usage only

        Returns
        -------
        None.
        """
        # on fist func-call clear the file from previous content
        if level == -1:
            if file:
                f = open(file, "w")
                f.close()

        if limit is not None:
            if level > limit:
                return

        level += 1
        tab = "\t"
        vertSep = "" # vertSep = "|" --> use this as vertival separator to indicate tab guidlines
        parent = self.parentObject(obj)

        if level == 0:
            horzSep = str()
        else:
            horzSep = "+--"

        horzSepUsage = "o"

        separator = str()
        for i in range(level):
            if i == 0:
                aux = "\t"
            else:
                aux = "{vertSep}{tab}".format(
                        vertSep = vertSep,
                        tab = tab
                    )
            separator += aux

        # create the tree with imported modules
        if not file:
            print(
                "{separator}{horzSep}{node}".format(
                        separator = separator,
                        horzSep = horzSep,
                        node = obj.name
                    )
                )
        else:
            with open(file, "a") as f:
                string = "{separator}{horzSep}{node}\n".format(
                        separator = separator,
                        horzSep = horzSep,
                        node = obj.name
                    )
                f.write(string)

        if showModuleUsage:
            # extent module-tree with the usage of callabels of imported modules
            if parent:
                callUsageObj = parent
            else:
                callUsageObj = obj

            if callUsageObj.children: # callable usage
                for call in callUsageObj.children["callables"]:
                    if call.module == obj.name:
                        if call.usage:
                            for use in call.usage:
                                if not file:
                                    print(
                                        "{separator}{vertSep}\t{horzSepUsage}[usage][alias: {alias}][line: {line}]{name}".format(
                                                separator = separator,
                                                vertSep = vertSep,
                                                horzSepUsage = horzSepUsage,
                                                alias = call.name,
                                                line = use.lineNumber,
                                                name = use.usage.strip(" \t\n")
                                            )
                                        )
                                else:
                                    with open(file, "a") as f:
                                        string = "{separator}{vertSep}\t{horzSepUsage}[usage][alias: {alias}][line: {line}]{name}\n".format(
                                                separator = separator,
                                                vertSep = vertSep,
                                                horzSepUsage = horzSepUsage,
                                                alias = call.name,
                                                line = use.lineNumber,
                                                name = use.usage.strip(" \t\n")
                                            )
                                        f.write(string)

        if showModuleUsage:
            # extend module-tree with the usage of the imported modules
            if obj.usage: # module usage
                for use in obj.usage:
                    if not file:
                        print(
                            "{separator}{vertSep}\t{horzSepUsage}[usage][alias: {alias}][line: {line}]{name}".format(
                                    separator = separator,
                                    vertSep = vertSep,
                                    horzSepUsage = horzSepUsage,
                                    alias = obj.alias,
                                    line = use.lineNumber,
                                    name = use.usage.strip(" \t\n")
                                )
                            )
                    else:
                        with open(file, "a") as f:
                            string = "{separator}{vertSep}\t{horzSepUsage}[usage][alias: {alias}][line: {line}]{name}\n".format(
                                    separator = separator,
                                    vertSep = vertSep,
                                    horzSepUsage = horzSepUsage,
                                    alias = obj.alias,
                                    line = use.lineNumber,
                                    name = use.usage.strip(" \t\n")
                                )
                            f.write(string)

        # recursivley walk through the tree-hirachy
        if obj.children:
            for obj in obj.children["modules"]:
                self.printTree(
                        obj,
                        file = file,
                        showModuleUsage = showModuleUsage,
                        limit = limit,
                        level = level
                    )

    def root(self):
        """
        root of the amt

        Returns
        -------
        BaseResult

        """
        return self._root

    def setRoot(self, root):
        """
        set the root to <root>

        Parameters
        ----------
        root : BaseResult

        Raises
        ------
        TypeError
            will be raised if <root> is not instance of BaseResult.

        Returns
        -------
        None.
        """
        if not isinstance(root, BaseResult):
            raise TypeError(
                    "input for 'tree' does not match {type_name}".format(
                            type_name = BaseResult
                        )
                )
        self._root = root

    root = property(root, setRoot)

"""result classes for amt"""

class BaseResult():
    """
    base-class for all amt result-classes
    """

    def __init__(self):
        self._alias = None
        self._name = None
        self._parent = None
        self._children = None
        self._usage = None

    def alias(self):
        return self._alias

    def children(self):
        return self._children

    def name(self):
        return self._name

    def parent(self):
        return self._parent

    def usage(self):
        return self._usage

    def setAlias(self, alias):
        if not isinstance(alias, str) and alias is not None:
            raise TypeError(
                    "input for 'alias' does not match {type_name}".format(
                            type_name = str
                        )
                )
        self._alias = alias

    def setChildren(self, children):
        if not isinstance(children, dict) and children is not None:
            raise TypeError(
                    "input for 'children' does not match {type_name}".format(
                            type_name = dict
                        )
                )
        self._children = children

    def setName(self, name):
        if not isinstance(name, str):
            raise TypeError(
                    "input for 'name' does not match {type_name}".format(
                            type_name = str
                        )
                )
        self._name = name

    def setParent(self, parent):
        self._parent = parent

    def setUsage(self, usage):
        self._usage = usage

    alias = property(alias, setAlias)
    children = property(children, setChildren)
    name = property(name, setName)
    parent = property(parent, setParent)
    usage = property(usage, setUsage)

class Function(BaseResult):

    def __init__(self):
        super().__init__()

class Callable(BaseResult):

    def __init__(self):
        super().__init__()
        self._fullName = None
        self._module = None

    def fullName(self):
        return self._fullName

    def module(self):
        return self._module

    def setFullName(self, name):
        if not isinstance(name, str) and name is not None:
            raise TypeError(
                    "input for 'name' does not match {type_name}".format(
                            type_name = str
                        )
                )
        self._fullName = name

    def setModule(self, module):
        if not isinstance(module, str) and module is not None:
            raise TypeError(
                    "input for 'module' does not match {type_name}".format(
                            type_name = str
                        )
                )
        self._module = module

    fullName = property(fullName, setFullName)
    module = property(module, setModule)

class Class(BaseResult):

    def __init__(self):
        super().__init__()
        self._inheritsFrom = None
        self._inheritedBy = None

    def inheritedBy(self):
        return self._inheritedBy

    def inheritsFrom(self):
        return self._inheritsFrom

    def setInheritedBy(self, name):
        if not isinstance(name, str) and name is not None:
            raise TypeError(
                    "input for 'name' does not match {type_name}".format(
                            type_name = str
                        )
                )
        self._inheritedBy = name

    def setInheritsFrom(self, name):
        if not isinstance(name, str) and name is not None:
            raise TypeError(
                    "input for 'name' does not match {type_name}".format(
                            type_name = str
                        )
                )
        self._inheritsFrom = name

    inheritedBy = property(inheritedBy, setInheritedBy)
    inheritsFrom = property(inheritsFrom, setInheritsFrom)

class Module(BaseResult):

    def __init__(self):
        super().__init__()

class Usage(BaseResult):

    def __init__(self):
        super().__init__()
        self._lineNumber = None

    def lineNumber(self):
        return self._lineNumber

    def setLineNumber(self, number):
        if not isinstance(number, int) and number is not None:
            raise TypeError(
                    "input for 'name' does not match {type_name}".format(
                            type_name = int
                        )
                )
        self._lineNumber = number

    lineNumber = property(lineNumber, setLineNumber)

"""helper functions"""
def determine_usage(resultObj, categorizerObj):

    def deep_find(val, iterable):

        if (not isinstance(iterable, list)) and (not isinstance(iterable, tuple)):
            if val == iterable:
                return True
        else:
            for element in iterable:
                if deep_find(val, element):
                    return True
        return False


    assignments = categorizerObj.tokenCategories.assignments
    other = categorizerObj.tokenCategories.other
    usage = list()
    out =list()

    if resultObj.alias:
        searchPattern = resultObj.alias
    else:
        searchPattern = resultObj.name.split(".")[-1]

    for assignment in assignments:
        aux = list()
        tokValues = [val[1] for val in assignment]
        index = find_all_indices(searchPattern, tokValues)
        if index:
            aux.append(tokenizer.untokenize(assignment))
            aux.append(assignment[0][2][0])
            usage.append(aux)

    for element in other:
        aux = list()
        tokValues = [val[1] for val in element]
        index = find_all_indices(searchPattern, tokValues)
        if index:
            aux.append(tokenizer.untokenize(element))
            aux.append(element[0][2][0])
            usage.append(aux)

    # out = list()
    for case in usage:
        obj = Usage()
        obj.name = resultObj.name
        obj.usage = case[0]
        obj.lineNumber = case[1]
        obj.parent = categorizerObj.file
        out.append(obj)
    return out

def find_all_indices(val, iterable):
    return [i for i, element in enumerate(iterable) if element == val]

def get_public_members(moduleName):
    """
    get all public members (all public callable classes, functions
    and constants) of the module <moduleName>
    """
    members = inspect.getmembers(importlib.import_module(moduleName))
    return [val[0] for val in members if not re.search("^_\w+", val[0])]

def imported_modules(categorizerObj):

    def identifier_helper(categorizerObj, iterable, modName):

        helper_callables = list()
        helper_modules = list()

        rawIdentifier = split_list("COMMA", cleanup_tok_helper(iterable))
        for element in rawIdentifier:
            aux = split_list("KEYWORD", element)
            importName = aux[0][0][1]
            try:
                aliasName = aux[1][0][1]
            except IndexError: # no alias for importName
                aliasName = None

            try:

                # test if importName is importalbe
                importlib.import_module(modName + "." + importName)

                # if importable: importName is a module and has to be casted
                # into the Module-class
                mod = Module()
                mod.name = modName + "." + importName
                mod.alias = aliasName
                mod.usage = determine_usage(mod, categorizerObj)
                mod.parent = categorizerObj.file
                helper_modules.append(mod)
            except ModuleNotFoundError:
                # importName is not a module --> callable
                # modName therefor must stand for a module, not a package
                mod = Module()
                mod.name = modName
                mod.alias = None
                mod.usage = determine_usage(mod, categorizerObj)
                mod.parent = categorizerObj.file
                if mod.name not in [val.name for val in helper_modules]:
                    helper_modules.append(mod)

                # process star imports
                if importName == "*":
                    stdLib = [val.stem for val in stf.StandardModuleFiles()]
                    publicMembers = [val for val in get_public_members(mod.name) if val not in stdLib]
                    for member in publicMembers:
                        call = Callable()
                        call.name = member
                        call.fullName = "{}.{}".format(mod.name, member)
                        call.module = mod.name
                        call.usage = determine_usage(call, categorizerObj)
                        call.parent = categorizerObj.file
                        callables.append(call)

                # from here on: process normal "from" imports
                else:
                    call = Callable()
                    call.name = importName
                    call.fullName = "{}.{}".format(mod.name, call.name)
                    call.alias = aliasName
                    call.module = mod.name
                    call.usage = determine_usage(call, categorizerObj)
                    call.parent = categorizerObj.file
                    helper_callables.append(call)

        return helper_modules, helper_callables

    def cleanup_tok_helper(iterable):
        """
        delete all unwated commas, resulting from multi-line import statements
        """
        copiedList = copy.deepcopy(iterable)

        # delete unwanted commas, resulting from multi-line import statements
        tokValues = [val[1] for val in copiedList]
        rindices = find_all_indices(")", tokValues)
        for i in range(len(rindices)):
            index = tokValues.index(")")
            commaIdx = index - 1
            if tokValues[commaIdx] == ",":
                del copiedList[commaIdx]

        tokValues = [val[1] for val in copiedList]
        lindices = find_all_indices("(", tokValues)
        for i in range(len(lindices)):
            index = tokValues.index("(")
            del copiedList[index]

        tokValues = [val[1] for val in copiedList]
        rindices = find_all_indices(")", tokValues)
        for i in range(len(rindices)):
            index = tokValues.index(")")
            del copiedList[index]

        return copiedList

    fromImports = copy.deepcopy(categorizerObj.tokenCategories.fromImports)
    normalImports = copy.deepcopy(categorizerObj.tokenCategories.normalImports)
    relativeImports = copy.deepcopy(categorizerObj.tokenCategories.relativeImports)

    modules = list()
    callables = list()

    # process "normal" imports
    for tok in normalImports:

        index = [val[1] for val in tok].index("import")
        del tok[0:index + 1]

        rawModules = split_list("COMMA", tok)
        for element in rawModules:
            mod = Module()
            name = str()
            aux = split_list("KEYWORD", element)
            for val in aux[0]:
                name += val[1]
            try:
                alias = aux[1][0][1]
            except IndexError:
                alias = None
            mod.name = name
            mod.alias = alias
            mod.usage = determine_usage(mod, categorizerObj)
            mod.parent = categorizerObj.file
            modules.append(mod)


    # process "from" imports
    for tok in fromImports:

        index = [val[1] for val in tok].index("from")
        del tok[0:index + 1]

        aux = split_list("import", tok, index = 1)
        fromIdentifier = aux[0]
        importIdentifier = aux[1]

        modName = tokenizer.untokenize(fromIdentifier)
        helper_modules, helper_callables = identifier_helper(categorizerObj, importIdentifier, modName)
        modules.extend(helper_modules)
        callables.extend(helper_callables)

    # process relative imports (which is similar to "from" Imports but not
    # completley the same)
    for tok in relativeImports:

        # compute a relative path form cwd to file-path we are now processing
        # relativePath = categorizerObj.file.relative_to(pathlib.Path().cwd())
        try:
            relativePath = categorizerObj.file.relative_to(pathlib.Path().cwd())
        except ValueError:
            # Value Error occurs if 'categorizerObj.file and pathlib.Path().cwd()
            # does not have a common base-path. the solution is to go up the
            # path hirachy of pathlib.Path().cwd() until a common base has been
            # found
            parentPath = pathlib.Path().cwd().parent
            while True:
                try:
                    relativePath = categorizerObj.file.relative_to(parentPath)
                    break
                except:
                    parentPath = parentPath.parent

        # delete unwanted preceeding tokens
        index = [val[1] for val in tok].index("from")
        del tok[0:index + 1]

        # process the relative part of the import
        aux = split_list("import", tok, index = 1)
        fromIdentifier = aux[0]
        importIdentifier = aux[1]

        pattern = "(^\.+)(\w*)"
        fromIdentifierStr = tokenizer.untokenize(fromIdentifier)
        match = re.search(pattern, fromIdentifierStr)
        parentIdx = len(match.group(1)) - 1
        name = match.group(2)
        modName = str(relativePath.parents[parentIdx]).replace(os.sep, ".")
        if name:
            modName = "{}.{}".format(modName, name)

        # now process the modules/callables after the import command
        helper_modules, helper_callables = identifier_helper(categorizerObj, importIdentifier, modName)
        modules.extend(helper_modules)
        callables.extend(helper_callables)

    return modules, callables

def lokal_callables(categorizerObj):
    classes = list()
    functions = list()
    classdefs = copy.deepcopy(categorizerObj.tokenCategories.classdefs)
    funcdefs = copy.deepcopy(categorizerObj.tokenCategories.funcdefs)

    # process classdefs
    for element in classdefs:
        cl = Class()
        inheritance = str()
        tokValues = [val[1] for val in element]
        clIdx = find_all_indices("class", tokValues)[0]
        clName = tokValues[clIdx + 1]

        try:
            lparIdx = find_all_indices("(", tokValues)[0]
            rparIdx = find_all_indices(")", tokValues)[0]
            par = tokValues[lparIdx + 1:rparIdx]
            for val in par:
                inheritance += val
            cl.inheritsFrom = inheritance
        except IndexError:
            cl.inheritsFrom = None

        cl.name = clName
        cl.usage = determine_usage(cl, categorizerObj)
        cl.parent = categorizerObj.file
        classes.append(cl)

    for element in funcdefs:
        func = Function()
        tokValues = [val[1] for val in element]
        funcIdx = find_all_indices("def", tokValues)[0]
        funcName = tokValues[funcIdx + 1]
        func.name = funcName
        func.usage = determine_usage(func, categorizerObj)
        func.parent = categorizerObj.file
        functions.append(func)

    return classes, functions

def scan_file(file, stdLib):

    # make sure to use pathlib.Path objects otherwise throw an arror
    try:
        file = pathlib.Path(file)
    except TypeError:
        raise TypeError(
                "input <{error_cause}> for 'file' does not match {type_name}".format(
                        type_name = pathlib.Path,
                        error_cause = str(file)
                    )
            )

    if file in stdLib:
        return False

    tok = tokenizer.TokenCategorizer(file)
    modules, callables = imported_modules(tok)
    lokalClasses, lokalFunctions = lokal_callables(tok)

    out = {
            "modules": modules,
            "callables": callables,
            "lokalClasses": lokalClasses,
            "lokalFunctions": lokalFunctions
        }

    return out

def split_list(seperator, iterable, index = 0):
    aux = dict()
    idx = find_all_indices(seperator, [val[index] for val in iterable])
    iterable = copy.deepcopy(iterable)
    out = list()

    for i in range(len(idx) + 1):
        aux[i] = list()

    i = 0
    while iterable:
        line = iterable.pop(0)
        if line[index] != seperator:
            aux[i].append(line)
        else:
            i += 1

    for key in aux.keys():
        out.append(aux[key])

    return out

"""functions exposed to the user"""
def parse(rootFile, modules = None, toStdOut = True):
    """
    the parse function create the abstract module tree (amt) by scanning the
    'file'. the result will be an object-oriented module-tree casted into a
    object-hirachy depicted by a instance of the amt-class

    Parameters
    ----------
    rootFile : pathlib.Path or str
        path to a file to be scanned. this file will be the root of the amt.

    modules : list or tuple, optional
        a list of modules to limit the modules to be searched for.
        if this argument is None, all modules except the standard-library-modules
        are searched for. The default is None.

    toStdOut : bool, optional
        if true, the scanning progress is going to be printed to stdOut.
        The default is True.

    Raises
    ------
    TypeError
        reasos for this error:
        - Tokenizer.tokenCategorizer can´t open <file> (invoked in scan_file)
        - scan_file returns False (<file> is part of pythons standard-library)

    Returns
    -------
    amt-object
    """

    if not isinstance(modules, list) and not isinstance(modules, tuple) and modules is not None:
        raise TypeError(
                "input for 'modules does not match {type_name_1} or {type_name_2}".format(
                        type_name_1 = list,
                        type_name_2 = tuple
                    )
            )

    # make sure to use pathlib.Path for rootFile
    file = pathlib.Path(rootFile)

    def delete_helper(names, scanned):

        if not isinstance(names, list) and not isinstance(names, tuple) and names is not None:
            raise TypeError(
                    "input for 'names' should be {type_name_1} or {type_name_2}, not {error_name}".format(
                            type_name_1 = list,
                            type_name_2 = tuple,
                            error_name = type(names)
                        )
                )

        if not isinstance(scanned, dict):
            raise TypeError(
                    "input <{error_name}> for 'scanned' does not match {type_name}".format(
                            type_name = dict,
                            error_name = str(scanned)
                        )
                )

        if names:
            modules = copy.deepcopy(scanned["modules"])
            callables = copy.deepcopy(scanned["callables"])

            # identify and delete unwanted modules
            for module in modules:
                if not find_occurence_helper(names, [module.name]):
                    index = [val.name for val in scanned["modules"]].index(module.name)
                    del scanned["modules"][index]

            # identify and delete unwanted callables
            for call in callables:
                if not find_occurence_helper(names, [call.fullName]):
                    index = [val.name for val in scanned["callables"]].index(call.name)
                    del scanned["callables"][index]

        return scanned

    def find_occurence_helper(iterable1, iterable2):
        occurence = list()
        for val in iterable1:
            for testVal in iterable2:
                if re.search(val, testVal):
                    occurence.append(True)
                else:
                    occurence.append(False)

        return any(occurence)

    def path_helper(module):
        if not isinstance(module, BaseResult):
            raise TypeError(
                    "input for 'module' does not match {type_name}".format(
                            type_name = BaseResult
                        )
                )
        if isinstance(module, Module):
            try:
                path = pathlib.Path(inspect.getfile(importlib.import_module(module.name)))
            except TypeError:
                path = False
            except ModuleNotFoundError:
                path = False

        elif isinstance(module, Callable):
            try:
                path = pathlib.Path(inspect.getfile(importlib.import_module(module.module)))
            except TypeError:
                path = False
        else:
            path = False

        return path

    stdLib = standard_library_finder.StandardModuleFiles()
    tree = amt()
    root = Module()
    root.name = file.name
    foundIdentifiers = delete_helper(modules, scan_file(file, stdLib))
    root.children = foundIdentifiers
    continueScan = True

    foundModules = root.children["modules"]
    level = 1

    if toStdOut:
        print("Scanning Tree Levels:")
        progress.progressBar(
                0, len(foundModules),
                title = "Level {}".format(level),
                note = "{} elements".format(len(foundModules))
            )

    while continueScan:
        aux = list()
        for index, module in enumerate(foundModules):

            if toStdOut:
                prog = index + 1
                progress.progressBar(
                        prog, len(foundModules),
                        title = "Level {}".format(level),
                        note = "{} elements".format(len(foundModules))
                    )

            try:
                foundIdentifiers = delete_helper(modules, scan_file(path_helper(module), stdLib))
            except TypeError:
                # various reasons for TypeError:
                #     - Tokenizer.tokenCategorizer can´t open <file> (invoked in scan_file)
                #     - scan_file returns False (<file> is part of pythons standard-library)
                continue
            module.children = foundIdentifiers
            aux.extend(foundIdentifiers["modules"])
        level += 1
        foundModules = aux
        continueScan = any(aux)
    tree.root = root

    if toStdOut:
        print("\n\n")

    return tree

if __name__ == "__main__":
    pass