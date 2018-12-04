#!/usr/bin/env python3

import re
import sys

class JackTokenizer:

    KEYWORD = 0
    SYMBOL = 1
    IDENTIFIER = 2
    INT_CONST = 3
    STRING_CONST = 4

    def __init__(self, inputPath):
        self._file = open(inputPath, 'r')
        self._tokens = self._tokenize(self._file.read())
        self._currentToken = ''

    def hasMoreTokens(self):
        return self._tokens != []

    def advance(self):
        self._currentToken = self._tokens.pop(0)

    def tokenType(self):
        if re.match(self.keyword, self._currentToken) != None:
            return JackTokenizer.KEYWORD
        elif re.match(self.symbol, self._currentToken) != None:
            return JackTokenizer.SYMBOL
        elif re.match(self.integerConstant, self._currentToken) != None:
            return JackTokenizer.INT_CONST
        elif re.match(self.StringConstant, self._currentToken) != None:
            return JackTokenizer.STRING_CONST
        elif re.match(self.identifier, self._currentToken) != None:
            return JackTokenizer.IDENTIFIER

    def keyWord(self):
        return self._currentToken

    def Symbol(self):
        return self._currentToken

    def Identifier(self):
        return self._currentToken

    def intVal(self):
        return int(self._currentToken)

    def stringVal(self):
        return self._currentToken.replace('"', '')

    keywords = [ 'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char',\
                 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return' ]
    keyword = '|'.join([kw + '(?!\w)' for kw in keywords])
    symbol = r'[{}()\[\]\.,;\+\-\*/&\|<>=~]'
    integerConstant = r'\d+'
    StringConstant = r'"[^"\n]*"'
    identifier = r'[a-zA-Z_]\w*'
    allTokensRegex = keyword + '|' + symbol + '|' + integerConstant + '|' + StringConstant + '|' + identifier

    def _tokenize(self, fileCharacters):
        fileCharacters = self._removeComments(fileCharacters)
        return re.findall(self.allTokensRegex, fileCharacters)

    def _removeComments(self, fileCharacters):
        return re.compile(r'//[^\n]*\n|/\*.*?\*/', re.DOTALL).sub('', fileCharacters)

if __name__ == '__main__':
    path = sys.argv[1]
    outputFile = open(path.replace('.jack', '.xml'), 'w')
    jackTokenizer = JackTokenizer(path)

    outputFile.write('<tokens>' + '\n')
    while jackTokenizer.hasMoreTokens():
        jackTokenizer.advance()
        type = jackTokenizer.tokenType()
        if type == JackTokenizer.KEYWORD:
            type = 'keyword'
            value = jackTokenizer.keyWord()
        elif type == JackTokenizer.SYMBOL:
            type = 'symbol'
            value = jackTokenizer.Symbol()
            if value == '<':
                value = '&lt;'
            elif value == '>':
                value = '&gt;'
            elif value == '&':
                value = '&amp;'
        elif type == JackTokenizer.IDENTIFIER:
            type = 'identifier'
            value = jackTokenizer.Identifier()
        elif type == JackTokenizer.INT_CONST:
            type = 'integerConstant'
            value = str(jackTokenizer.intVal())
        elif type == JackTokenizer.STRING_CONST:
            type = 'stringConstant'
            value = jackTokenizer.stringVal().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        outputFile.write('<' + type + '> ' + value + ' </' + type + '>\n')
    outputFile.write('</tokens>' + '\n')
    outputFile.close()
