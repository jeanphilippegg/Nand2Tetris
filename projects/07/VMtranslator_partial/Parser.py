#!/usb/bin/env python3

import re

class Parser:

    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_FUNCTION = 6
    C_RETURN = 7
    C_CALL = 8

    def __init__(self, path):
        self._file = open(path, 'r')
        self._nextCommand = self._getNextCommand()
        self._currentCommand = ''

    def hasMoreCommands(self):
        return self._nextCommand

    def advance(self):
        self._currentCommand = self._nextCommand
        self._nextCommand = self._getNextCommand()

    def commandType(self):
        if self._currentCommand[0] in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
            return Parser.C_ARITHMETIC
        if self._currentCommand[0] in ['push']:
            return Parser.C_PUSH
        if self._currentCommand[0] in ['pop']:
            return Parser.C_POP
        if self._currentCommand[0] in ['label']:
            return Parser.C_LABEL
        if self._currentCommand[0] in ['goto']:
            return Parser.C_GOTO
        if self._currentCommand[0] in ['if-goto']:
            return Parser.C_IF
        if self._currentCommand[0] in ['function']:
            return Parser.C_FUNCTION
        if self._currentCommand[0] in ['return']:
            return Parser.C_RETURN
        if self._currentCommand[0] in ['call']:
            return Parser.C_CALL

    def arg1(self):
        return self._currentCommand[0] if self.commandType() == Parser.C_ARITHMETIC else self._currentCommand[1]

    def arg2(self):
        return self._currentCommand[2]

    def _getNextCommand(self):
        currentCommand = ''

        while not currentCommand:
            currentLine = self._file.readline()

            if not currentLine:
                return []

            currentCommand = self._removeComments(self._removeNewLine(currentLine)).split()

        return currentCommand

    def _removeNewLine(self, line):
        return re.sub('\n', '', line)

    def _removeComments(self, line):
        return re.sub('//.*', '', line)
