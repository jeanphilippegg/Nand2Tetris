#!/usr/bin/env python3

import re

class Parser:

    A_COMMAND = 0
    C_COMMAND = 1
    L_COMMAND = 2

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
        if self._currentCommand[0] == '@':
            return Parser.A_COMMAND
        elif self._currentCommand[0] == '(':
            return Parser.L_COMMAND
        else:
            return Parser.C_COMMAND

    def symbol(self):
        return self._currentCommand[1:] if (self.commandType() == Parser.A_COMMAND) else self._currentCommand[1:-1]

    def dest(self):
        return self._currentCommand[:self._currentCommand.find('=')] if '=' in self._currentCommand else ''

    def comp(self):
        startIndex = 0 if '=' not in self._currentCommand else self._currentCommand.find('=') + 1
        endIndex = len(self._currentCommand) if ';' not in self._currentCommand else self._currentCommand.find(';')
        return self._currentCommand[startIndex:endIndex]

    def jump(self):
        return self._currentCommand[self._currentCommand.find(';')+1:] if ';' in self._currentCommand else ''

    def _getNextCommand(self):
        currentCommand = ''

        while currentCommand == '':
            currentLine = self._file.readline()

            if not currentLine:
                return ''

            currentCommand = self._removeComments(self._removeWhiteSpace(currentLine))

        return currentCommand

    def _removeWhiteSpace(self, line):
        return re.sub('[ \n]*', '', line)

    def _removeComments(self, line):
        return re.sub('//.*', '', line)
