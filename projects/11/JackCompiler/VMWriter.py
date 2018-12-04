#!/usr/bin/env python3

class VMWriter:

    CONST = 'constant'
    ARG = 'argument'
    LOCAL = 'local'
    STATIC = 'static'
    THIS = 'this'
    THAT = 'that'
    POINTER = 'pointer'
    TEMP = 'temp'

    ADD = 'add'
    SUB = 'sub'
    NEG = 'neg'
    EQ = 'eq'
    GT = 'gt'
    LT = 'lt'
    AND = 'and'
    OR = 'or'
    NOT = 'not'

    def __init__(self, outputPath):
        self._file = open(outputPath, 'w')

    def writePush(self, Segment, Index):
        self._file.write('push ' + Segment + ' ' + str(Index) + '\n')

    def writePop(self, Segment, Index):
        self._file.write('pop ' + Segment + ' ' + str(Index) + '\n')

    def WriteArithmetic(self, command):
        self._file.write(command + '\n')

    def WriteLabel(self, label):
        self._file.write('label ' + label + '\n')

    def WriteGoto(self, label):
        self._file.write('goto ' + label + '\n')

    def WriteIf(self, label):
        self._file.write('if-goto ' + label + '\n')

    def writeCall(self, name, nArgs):
        self._file.write('call ' + name + ' ' + str(nArgs) + '\n')

    def writeFunction(self, name, nLocals):
        self._file.write('function ' + name + ' ' + str(nLocals) + '\n')

    def writeReturn(self):
        self._file.write('return\n')

    def close(self):
        self._file.close()
