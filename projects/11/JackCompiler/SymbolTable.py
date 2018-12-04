#!/usr/bin/env python3

class SymbolTable:

    STATIC = 0
    FIELD = 1
    ARG = 2
    VAR = 3
    NONE = 4

    def __init__(self):
        self._classScope = {}
        self._subroutineScope = {}
        self._staticCount = self._fieldCount = self._argCount = self._varCount = 0

    def startSubroutine(self):
        self._subroutineScope = {}
        self._staticCount = self._fieldCount = self._argCount = self._varCount = 0

    def Define(self, name, type, kind):
        if kind == SymbolTable.STATIC:
            self._classScope[name] = (type, kind, self._staticCount)
            self._staticCount += 1
        elif kind == SymbolTable.FIELD:
            self._classScope[name] = (type, kind, self._fieldCount)
            self._fieldCount += 1
        elif kind == SymbolTable.ARG:
            self._subroutineScope[name] = (type, kind, self._argCount)
            self._argCount += 1
        elif kind == SymbolTable.VAR:
            self._subroutineScope[name] = (type, kind, self._varCount)
            self._varCount += 1

    def VarCount(self, kind):
        return sum(1 for (key, value) in self._classScope.items() if value[1] == kind)\
            + sum(1 for (key, value) in self._subroutineScope.items() if value[1] == kind)

    def KindOf(self, name):
        if name in self._subroutineScope:
            return self._subroutineScope[name][1]
        elif name in self._classScope:
            return self._classScope[name][1]
        else:
            return SymbolTable.NONE

    def TypeOf(self, name):
        if name in self._subroutineScope:
            return self._subroutineScope[name][0]
        elif name in self._classScope:
            return self._classScope[name][0]
        else:
            return ''

    def IndexOf(self, name):
        if name in self._subroutineScope:
            return self._subroutineScope[name][2]
        elif name in self._classScope:
            return self._classScope[name][2]
        else:
            return -1
