#!/usr/bin/env python3

import Constant
import JackTokenizer

class CompilationEngine:

    def __init__(self, inputPath, outFile):
        self._jackTokenizer = JackTokenizer.JackTokenizer(inputPath)
        if self._jackTokenizer.hasMoreTokens():
            self._jackTokenizer.advance()
        self._outFile = outFile

    def CompileClass(self):
        self._writeNonTerminalStart('class')
        self._advance()     # class
        self._advance()     # className
        self._advance()     # {
        while self._getTokenValue() in [ 'static', 'field' ]:
            self.CompileClassVarDec()
        while self._getTokenValue() in [ 'constructor', 'function', 'method' ]:
            self.CompileSubroutine()
        self._advance()     # }
        self._writeNonTerminalEnd('class')

    def CompileClassVarDec(self):
        self._writeNonTerminalStart('classVarDec')
        self._advance()       # static, field
        self._advance()       # type
        self._advance()       # varName
        while self._getTokenValue() == ',':
            self._advance()   # ,
            self._advance()   # varName
        self._advance()       # ;
        self._writeNonTerminalEnd('classVarDec')

    def CompileSubroutine(self):
        self._writeNonTerminalStart('subroutineDec')
        self._advance()       # constructor, function, method
        self._advance()       # void, type
        self._advance()       # subroutineName
        self._advance()       # (
        self.compileParameterList()
        self._advance()       # )
        self._writeNonTerminalStart('subroutineBody')
        self._advance()       # {
        while self._getTokenValue() == 'var':
            self.compileVarDec()
        self.compileStatements()
        self._advance()       # }
        self._writeNonTerminalEnd('subroutineBody')
        self._writeNonTerminalEnd('subroutineDec')

    def compileParameterList(self):
        self._writeNonTerminalStart('parameterList')
        if self._getTokenValue() != ')':
            self._advance()      # type
            self._advance()      # varName
            while self._getTokenValue() == ',':
                self._advance()  # ,
                self._advance()  # type
                self._advance()  # varName
        self._writeNonTerminalEnd('parameterList')

    def compileVarDec(self):
        self._writeNonTerminalStart('varDec')
        self._advance()       # var
        self._advance()       # type
        self._advance()       # varName
        while self._getTokenValue() == ',':
            self._advance()   # ,
            self._advance()   # varName
        self._advance()       # ;
        self._writeNonTerminalEnd('varDec')

    def compileStatements(self):
        self._writeNonTerminalStart('statements')
        while self._getTokenValue() in [ 'let', 'if', 'while', 'do', 'return' ]:
            if self._getTokenValue() == 'let':
                self.compileLet()
            elif self._getTokenValue() == 'if':
                self.compileIf()
            elif self._getTokenValue() == 'while':
                self.compileWhile()
            elif self._getTokenValue() == 'do':
                self.compileDo()
            elif self._getTokenValue() == 'return':
                self.compileReturn()
        self._writeNonTerminalEnd('statements')

    def compileDo(self):
        self._writeNonTerminalStart('doStatement')
        self._advance()      # do
        self._advance()      # subroutineName, className, varName
        if self._getTokenValue() == '.':
            self._advance()  # .
            self._advance()  # subroutineName
        self._advance()      # (
        self.CompileExpressionList()
        self._advance()      # )
        self._advance()      # ;
        self._writeNonTerminalEnd('doStatement')

    def compileLet(self):
        self._writeNonTerminalStart('letStatement')
        self._advance()      # let
        self._advance()      # varName
        if self._getTokenValue() == '[':
            self._advance()  # [
            self.CompileExpression()
            self._advance()  # ]
        self._advance()      # =
        self.CompileExpression()
        self._advance()      # ;
        self._writeNonTerminalEnd('letStatement')

    def compileWhile(self):
        self._writeNonTerminalStart('whileStatement')
        self._advance()    # while
        self._advance()    # (
        self.CompileExpression()
        self._advance()    # )
        self._advance()    # {
        self.compileStatements()
        self._advance()    # }
        self._writeNonTerminalEnd('whileStatement')

    def compileReturn(self):
        self._writeNonTerminalStart('returnStatement')
        self._advance()    # return
        if self._getTokenValue() != ';':
            self.CompileExpression()
        self._advance()    # ;
        self._writeNonTerminalEnd('returnStatement')

    def compileIf(self):
        self._writeNonTerminalStart('ifStatement')
        self._advance()      # if
        self._advance()      # (
        self.CompileExpression()
        self._advance()      # )
        self._advance()      # {
        self.compileStatements()
        self._advance()      # }
        if self._getTokenValue() == 'else':
            self._advance()  # else
            self._advance()  # {
            self.compileStatements()
            self._advance()  # }
        self._writeNonTerminalEnd('ifStatement')

    def CompileExpression(self):
        self._writeNonTerminalStart('expression')
        self.CompileTerm()
        while self._getTokenValue() in [ '+', '-', '*', '/', '&', '|', '<', '>', '=' ]:
            self._advance()    # op
            self.CompileTerm()
        self._writeNonTerminalEnd('expression')

    def CompileTerm(self):
        self._writeNonTerminalStart('term')
        if self._getTokenType() in [ 'integerConstant', 'stringConstant']:
            self._advance()       # integerConstant, stringConstant
        elif self._getTokenValue() in [ 'true', 'false', 'null', 'this' ]:
            self._advance()       # keywordConstant
        elif self._getTokenType() == 'identifier':
            self._advance()       # varName or subroutineName
            if self._getTokenValue() == '[':
                self._advance()   # [
                self.CompileExpression()
                self._advance()   # ]
            elif self._getTokenValue() in [ '(', '.' ]:
                if self._getTokenValue() == '.':
                    self._advance()   # .
                    self._advance()   # subroutineName
                self._advance()       # (
                self.CompileExpressionList()
                self._advance()       # )
        elif self._getTokenValue() == '(':
            self._advance()           # (
            self.CompileExpression()
            self._advance()           # )
        elif self._getTokenValue() in [ '-', '~' ]:
            self._advance()           # unaryOp
            self.CompileTerm()
        self._writeNonTerminalEnd('term')

    def CompileExpressionList(self):
        self._writeNonTerminalStart('expressionList')
        if self._getTokenType() in [ 'integerConstant', 'stringConstant' ]\
           or self._getTokenValue() in [ 'true', 'false', 'null', 'this' ]\
           or self._getTokenType() == 'identifier'\
           or self._getTokenValue() == '('\
           or self._getTokenValue() in [ '+', '-', '*', '&', '|', '<', '>', '=' ]:
            self.CompileExpression()
            while self._getTokenValue() == ',':
                self._advance()   # ,
                self.CompileExpression()
        self._writeNonTerminalEnd('expressionList')

    def _writeNonTerminalStart(self, nonTerminalName):
        self._outFile.write('<' + nonTerminalName + '>\n')

    def _writeNonTerminalEnd(self, nonTerminalName):
        self._outFile.write('</' + nonTerminalName + '>\n')

    def _writeTerminal(self, terminalType, terminalName):
        terminalName = terminalName.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        self._outFile.write('<' + terminalType + '>' + terminalName + '</' + terminalType + '>\n')

    def _advance(self):
        self._writeTerminal(self._getTokenType(), self._getTokenValue())
        if self._jackTokenizer.hasMoreTokens():
            self._jackTokenizer.advance()

    def _getTokenType(self):
        terminalType = ''
        if self._jackTokenizer.tokenType() == JackTokenizer.JackTokenizer.KEYWORD:
            terminalType = 'keyword'
        elif self._jackTokenizer.tokenType() == JackTokenizer.JackTokenizer.SYMBOL:
            terminalType = 'symbol'
        elif self._jackTokenizer.tokenType() == JackTokenizer.JackTokenizer.INT_CONST:
            terminalType = 'integerConstant'
        elif self._jackTokenizer.tokenType() == JackTokenizer.JackTokenizer.STRING_CONST:
            terminalType = 'stringConstant'
        elif self._jackTokenizer.tokenType() == JackTokenizer.JackTokenizer.IDENTIFIER:
            terminalType = 'identifier'
        return terminalType

    def _getTokenValue(self):
        token = ''
        if self._jackTokenizer.tokenType() == JackTokenizer.JackTokenizer.KEYWORD:
            token = self._jackTokenizer.keyWord()
        elif self._jackTokenizer.tokenType() == JackTokenizer.JackTokenizer.SYMBOL:
            token = self._jackTokenizer.Symbol()
        elif self._jackTokenizer.tokenType() == JackTokenizer.JackTokenizer.INT_CONST:
            token = str(self._jackTokenizer.intVal())
        elif self._jackTokenizer.tokenType() == JackTokenizer.JackTokenizer.STRING_CONST:
            token = self._jackTokenizer.stringVal()
        elif self._jackTokenizer.tokenType() == JackTokenizer.JackTokenizer.IDENTIFIER:
            token = self._jackTokenizer.Identifier()
        return token
