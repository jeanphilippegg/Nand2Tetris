#!/usr/bin/env python3

import JackTokenizer
import SymbolTable
import VMWriter

class CompilationEngine:

    def __init__(self, inputPath, outputPath):
        self._jackTokenizer = JackTokenizer.JackTokenizer(inputPath)
        if self._jackTokenizer.hasMoreTokens():
            self._jackTokenizer.advance()
        self._vmWriter = VMWriter.VMWriter(outputPath)
        self._symbolTable = SymbolTable.SymbolTable()
        self._currentClassName = ''
        self._whileCount = self._ifCount = 0

    def CompileClass(self):
        self._advance()     # class
        self._currentClassName = self._getTokenValue()
        self._advance()     # className
        self._advance()     # {
        while self._getTokenValue() in [ 'static', 'field' ]:
            self.CompileClassVarDec()
        while self._getTokenValue() in [ 'constructor', 'function', 'method' ]:
            self.CompileSubroutine()
        self._advance()     # }
        self._vmWriter.close()

    def CompileClassVarDec(self):
        varKind = self._getTokenValue()
        self._advance()       # static, field
        varType = self._getTokenValue()
        self._advance()       # type
        varName = self._getTokenValue()
        self._advance()       # varName
        self._symbolTable.Define(varName, varType, SymbolTable.SymbolTable.STATIC if varKind == 'static' else SymbolTable.SymbolTable.FIELD)
        while self._getTokenValue() == ',':
            self._advance()   # ,
            varName = self._getTokenValue()
            self._advance()   # varName
            self._symbolTable.Define(varName, varType, SymbolTable.SymbolTable.STATIC if varKind == 'static' else SymbolTable.SymbolTable.FIELD)
        self._advance()       # ;

    def CompileSubroutine(self):
        self._symbolTable.startSubroutine()
        subroutineType = self._getTokenValue()
        self._advance()       # constructor, function, method
        self._advance()       # void, type
        subroutineName = self._getTokenValue()
        self._advance()       # subroutineName
        self._advance()       # (
        # We need to add a dummy entry in the arguments of the function for the 'this' object.
        # When this function is called, 'push argument 1' must refer to the first argument. 'argument 0' is for the 'this' object
        if subroutineType == 'method':
            self._symbolTable.Define('dummy', 'dummy', SymbolTable.SymbolTable.ARG)
        self.compileParameterList()
        self._advance()       # )
        self._advance()       # {
        while self._getTokenValue() == 'var':
            self.compileVarDec()
        self._vmWriter.writeFunction(self._currentClassName + '.' + subroutineName, self._symbolTable.VarCount(SymbolTable.SymbolTable.VAR))
        # There is no need to set 'this' for functions
        if subroutineType == 'method':
            self._vmWriter.writePush('argument', 0)
            self._vmWriter.writePop('pointer', 0) # Set 'this' to arg0
        elif subroutineType == 'constructor':
            self._vmWriter.writePush('constant', self._symbolTable.VarCount(SymbolTable.SymbolTable.FIELD))
            self._vmWriter.writeCall('Memory.alloc', 1)
            self._vmWriter.writePop('pointer', 0) # Set 'this' to a newly allocated object
        self.compileStatements()
        self._advance()       # }

    def compileParameterList(self):
        if self._getTokenValue() != ')':
            paramType = self._getTokenValue()
            self._advance()      # type
            paramName = self._getTokenValue()
            self._advance()      # varName
            self._symbolTable.Define(paramName, paramType, SymbolTable.SymbolTable.ARG)
            while self._getTokenValue() == ',':
                self._advance()  # ,
                paramType = self._getTokenValue()
                self._advance()  # type
                paramName = self._getTokenValue()
                self._advance()  # varName
                self._symbolTable.Define(paramName, paramType, SymbolTable.SymbolTable.ARG)

    def compileVarDec(self):
        self._advance()       # var
        varType = self._getTokenValue()
        self._advance()       # type
        varName = self._getTokenValue()
        self._advance()       # varName
        self._symbolTable.Define(varName, varType, SymbolTable.SymbolTable.VAR)
        while self._getTokenValue() == ',':
            self._advance()   # ,
            varName = self._getTokenValue()
            self._advance()   # varName
            self._symbolTable.Define(varName, varType, SymbolTable.SymbolTable.VAR)
        self._advance()       # ;

    def compileStatements(self):
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

    def compileDo(self):
        self._advance()      # do
        firstName = self._getTokenValue()
        className = functionName = ''
        numArguments = 0
        self._advance()      # subroutineName, className, varName
        if self._getTokenValue() == '.':
            self._advance()  # .
            # This is a function call with k arguments (always called with ClassName.functionName)
            if self._symbolTable.KindOf(firstName) == SymbolTable.SymbolTable.NONE:
                className = firstName
            # This is a method call with k+1 arguments (always called with varName.methodName)
            else:
                className = self._symbolTable.TypeOf(firstName)
                self._writePush(firstName) # Push 'varName' object on the stack (as the first argument of the method)
                numArguments += 1
            functionName = self._getTokenValue()
            self._advance()  # subroutineName
        # This is a method call within the current class with k+1 arguments
        else:
            className = self._currentClassName
            functionName = firstName
            self._vmWriter.writePush('pointer', 0) # Push 'this' on the stack (as the first argument of the method)
            numArguments += 1
        self._advance()      # (
        numArguments += self.CompileExpressionList()
        self._advance()      # )
        self._vmWriter.writeCall(className + '.' + functionName, numArguments)
        self._advance()      # ;
        # In a do statement, the return value is ignored. We need to pop it from the top of the stack.
        self._vmWriter.writePop('temp', 0)

    def compileLet(self):
        self._advance()      # let
        varName = self._getTokenValue()
        isArray = False
        self._advance()      # varName
        if self._getTokenValue() == '[':
            isArray = True
            self._advance()  # [
            self.CompileExpression()
            self._advance()  # ]
            self._writePush(varName)
            self._vmWriter.WriteArithmetic(VMWriter.VMWriter.ADD)
            # We cannot put the calculated address in 'that' here. The following CompileExpression() could override it.
            # So, we just leave it on the stack.
            #self._vmWriter.writePop('pointer', 1) # Put the array entry address in 'that'
        self._advance()      # =
        self.CompileExpression()
        self._advance()      # ;
        if not isArray:
            self._writePop(varName)
        else:
            # On the stack, we have the address of 'that' (not in 'pointer 1' yet) followed by the expression value.
            # The following lines put the address of 'that' in 'pointer 1', then the value of the expression at the address of 'that'.
            self._vmWriter.writePop('temp', 0)
            self._vmWriter.writePop('pointer', 1)
            self._vmWriter.writePush('temp', 0)
            self._vmWriter.writePop('that', 0)

    def compileWhile(self):
        self._advance()    # while
        self._advance()    # (
        self._whileCount += 1
        whileNumber = self._whileCount
        self._vmWriter.WriteLabel('WHILE_START' + str(whileNumber))
        self.CompileExpression()
        self._vmWriter.WriteArithmetic(VMWriter.VMWriter.NOT)
        self._vmWriter.WriteIf('WHILE_END' + str(whileNumber))
        self._advance()    # )
        self._advance()    # {
        self.compileStatements()
        self._advance()    # }
        self._vmWriter.WriteGoto('WHILE_START' + str(whileNumber))
        self._vmWriter.WriteLabel('WHILE_END' + str(whileNumber))

    def compileReturn(self):
        self._advance()    # return
        if self._getTokenValue() != ';':
            self.CompileExpression()
        else:
            self._vmWriter.writePush('constant', 0)
        self._advance()    # ;
        self._vmWriter.writeReturn()

    def compileIf(self):
        self._advance()      # if
        self._advance()      # (
        self.CompileExpression()
        self._ifCount += 1
        ifNumber = self._ifCount
        self._vmWriter.WriteArithmetic(VMWriter.VMWriter.NOT)
        self._vmWriter.WriteIf('ELSE' + str(ifNumber))
        self._advance()      # )
        self._advance()      # {
        self.compileStatements()
        self._advance()      # }
        self._vmWriter.WriteGoto('IF_END' + str(ifNumber))
        self._vmWriter.WriteLabel('ELSE' + str(ifNumber))
        if self._getTokenValue() == 'else':
            self._advance()  # else
            self._advance()  # {
            self.compileStatements()
            self._advance()  # }
        self._vmWriter.WriteLabel('IF_END' + str(ifNumber))

    def CompileExpression(self):
        self.CompileTerm()
        while self._getTokenValue() in [ '+', '-', '*', '/', '&', '|', '<', '>', '=' ]:
            tokenValue = self._getTokenValue()
            self._advance()    # op
            self.CompileTerm()

            if tokenValue == '+':
                self._vmWriter.WriteArithmetic(VMWriter.VMWriter.ADD)
            elif tokenValue == '-':
                self._vmWriter.WriteArithmetic(VMWriter.VMWriter.SUB)
            elif tokenValue == '*':
                self._vmWriter.writeCall('Math.multiply', 2)
            elif tokenValue == '/':
                self._vmWriter.writeCall('Math.divide', 2)
            elif tokenValue == '&':
                self._vmWriter.WriteArithmetic(VMWriter.VMWriter.AND)
            elif tokenValue == '|':
                self._vmWriter.WriteArithmetic(VMWriter.VMWriter.OR)
            elif tokenValue == '<':
                self._vmWriter.WriteArithmetic(VMWriter.VMWriter.LT)
            elif tokenValue == '>':
                self._vmWriter.WriteArithmetic(VMWriter.VMWriter.GT)
            elif tokenValue == '=':
                self._vmWriter.WriteArithmetic(VMWriter.VMWriter.EQ)

    def CompileTerm(self):
        if self._getTokenType() == 'integerConstant':
            tokenValue = self._getTokenValue()
            self._vmWriter.writePush('constant', int(tokenValue))
            self._advance()       # integerConstant
        elif self._getTokenType() == 'stringConstant':
            tokenValue = self._getTokenValue()
            self._vmWriter.writePush('constant', len(tokenValue))
            self._vmWriter.writeCall('String.new', 1)
            for letter in tokenValue:
                self._vmWriter.writePush('constant', ord(letter))
                self._vmWriter.writeCall('String.appendChar', 2)
            self._advance()       # stringConstant
        elif self._getTokenValue() in [ 'true', 'false', 'null', 'this' ]:
            tokenValue = self._getTokenValue()
            if tokenValue == 'true':
                self._vmWriter.writePush('constant', 1)
                self._vmWriter.WriteArithmetic(VMWriter.VMWriter.NEG)
            elif tokenValue == 'false':
                self._vmWriter.writePush('constant', 0)
            elif tokenValue == 'null':
                self._vmWriter.writePush('constant', 0)
            elif tokenValue == 'this':
                self._vmWriter.writePush('pointer', 0)
            self._advance()       # keywordConstant
        elif self._getTokenType() == 'identifier':
            firstName = self._getTokenValue()
            self._advance()       # varName or subroutineName
            if self._getTokenValue() == '[':
                self._advance()   # [
                self.CompileExpression()
                self._advance()   # ]
                self._writePush(firstName)
                self._vmWriter.WriteArithmetic(VMWriter.VMWriter.ADD)
                self._vmWriter.writePop('pointer', 1) # Put the array entry address in 'that'
                self._vmWriter.writePush('that', 0)
            elif self._getTokenValue() in [ '(', '.' ]:
                className = functionName = ''
                numArguments = 0
                if self._getTokenValue() == '.':
                    self._advance()  # .
                    # This is a function call with k arguments (always called with ClassName.functionName)
                    if self._symbolTable.KindOf(firstName) == SymbolTable.SymbolTable.NONE:
                        className = firstName
                    # This is a method call with k+1 arguments (always called with varName.methodName)
                    else:
                        className = self._symbolTable.TypeOf(firstName)
                        self._writePush(firstName) # Push 'varName' object on the stack (as the first argument of the method)
                        numArguments += 1
                    functionName = self._getTokenValue()
                    self._advance()  # subroutineName
                # This is a method call within the current class with k+1 arguments
                else:
                    className = self._currentClassName
                    functionName = firstName
                    self._vmWriter.writePush('pointer', 0) # Push 'this' on the stack (as the first argument of the method)
                    numArguments += 1
                self._advance()      # (
                numArguments += self.CompileExpressionList()
                self._advance()      # )
                self._vmWriter.writeCall(className + '.' + functionName, numArguments)
            else:
                self._writePush(firstName)
        elif self._getTokenValue() == '(':
            self._advance()           # (
            self.CompileExpression()
            self._advance()           # )
        elif self._getTokenValue() in [ '-', '~' ]:
            tokenValue = self._getTokenValue()
            self._advance()           # unaryOp
            self.CompileTerm()
            if tokenValue == '-':
                self._vmWriter.WriteArithmetic(VMWriter.VMWriter.NEG)
            elif tokenValue == '~':
                self._vmWriter.WriteArithmetic(VMWriter.VMWriter.NOT)

    # I added a return value to this function. I could not use a global variable for the number of arguments
    # because it would not work for nested function calls (func1(func2(1, 2), 3)).
    def CompileExpressionList(self):
        numExpressions = 0
        if self._getTokenType() in [ 'integerConstant', 'stringConstant' ]\
           or self._getTokenValue() in [ 'true', 'false', 'null', 'this' ]\
           or self._getTokenType() == 'identifier'\
           or self._getTokenValue() == '('\
           or self._getTokenValue() in [ '+', '-', '*', '&', '|', '<', '>', '=' ]:
            self.CompileExpression()
            numExpressions += 1
            while self._getTokenValue() == ',':
                self._advance()   # ,
                self.CompileExpression()
                numExpressions += 1
        return numExpressions

    def _advance(self):
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

    def _writePush(self, varName):
        if self._symbolTable.KindOf(varName) == SymbolTable.SymbolTable.VAR:
            self._vmWriter.writePush('local', self._symbolTable.IndexOf(varName))
        elif self._symbolTable.KindOf(varName) == SymbolTable.SymbolTable.ARG:
            self._vmWriter.writePush('argument', self._symbolTable.IndexOf(varName))
        elif self._symbolTable.KindOf(varName) == SymbolTable.SymbolTable.STATIC:
            self._vmWriter.writePush('static', self._symbolTable.IndexOf(varName))
        elif self._symbolTable.KindOf(varName) == SymbolTable.SymbolTable.FIELD:
            self._vmWriter.writePush('this', self._symbolTable.IndexOf(varName))

    def _writePop(self, varName):
        if self._symbolTable.KindOf(varName) == SymbolTable.SymbolTable.VAR:
            self._vmWriter.writePop('local', self._symbolTable.IndexOf(varName))
        elif self._symbolTable.KindOf(varName) == SymbolTable.SymbolTable.ARG:
            self._vmWriter.writePop('argument', self._symbolTable.IndexOf(varName))
        elif self._symbolTable.KindOf(varName) == SymbolTable.SymbolTable.STATIC:
            self._vmWriter.writePop('static', self._symbolTable.IndexOf(varName))
        elif self._symbolTable.KindOf(varName) == SymbolTable.SymbolTable.FIELD:
            self._vmWriter.writePop('this', self._symbolTable.IndexOf(varName))
