#!/usr/bin/env python3

class CodeWriter:

    def __init__(self, path):
        self._outFile = open(path, 'w')
        self._fileName = ''
        self._boolean = 0
        self._returnAddressCount = 0
        self._currentFunctionName = ''

    def setFileName(self, fileName):
        self._fileName = fileName

    def writeInit(self):
        self._writeLine('@256')
        self._writeLine('D=A')
        self._writeLine('@SP')
        self._writeLine('M=D')
        self.writeCall('Sys.init', 0)

    def writeArithmetic(self, command):
        # Unary commands
        if command == 'neg':
            self._decrementSP()
            self._setAtoSP()
            self._writeLine('M=-M')
            self._incrementSP()
        elif command == 'not':
            self._decrementSP()
            self._setAtoSP()
            self._writeLine('M=!M')
            self._incrementSP()
        # Binary commands
        else:
            # Get operands in M and D
            self._decrementSP()
            self._setDtoValueAtSP()
            self._decrementSP()
            self._setAtoSP()

            if command == 'add':
                self._writeLine('M=M+D')
            elif command == 'sub':
                self._writeLine('M=M-D')
            elif command == 'and':
                self._writeLine('M=M&D')
            elif command == 'or':
                self._writeLine('M=M|D')
            elif command in ['eq', 'gt', 'lt']:
                # If x - y < 0, jump to SETBOOLX (to push True on the stack)
                self._writeLine('D=M-D')
                self._writeLine('@SETBOOL' + str(self._boolean))
                if command == 'eq':
                    self._writeLine('D;JEQ')
                elif command == 'gt':
                    self._writeLine('D;JGT')
                else:
                    self._writeLine('D;JLT')
                # Push False on the stack and jump to ENDSETBOOLX
                self._setAtoSP()
                self._writeLine('M=0')
                self._writeLine('@ENDSETBOOL' + str(self._boolean))
                self._writeLine('0;JMP')
                self._writeLine('(SETBOOL' + str(self._boolean) + ')')
                # Push True on the stack
                self._setAtoSP()
                self._writeLine('M=-1')
                self._writeLine('(ENDSETBOOL' + str(self._boolean) + ')')
                self._boolean += 1

            self._incrementSP()

    def WritePushPop(self, command, segment, index):
        if command == 'C_PUSH' and segment == 'constant':
            self._writeLine('@' + str(index))
            self._writeLine('D=A')
            self._setAtoSP()
            self._writeLine('M=D')
            self._incrementSP()
        elif command == 'C_PUSH' and segment == 'local':
            self._writePushRegister(index, 'LCL', False)
        elif command == 'C_POP' and segment == 'local':
            self._writePopRegister(index, 'LCL', False)
        elif command == 'C_PUSH' and segment == 'argument':
            self._writePushRegister(index, 'ARG', False)
        elif command == 'C_POP' and segment == 'argument':
            self._writePopRegister(index, 'ARG', False)
        elif command == 'C_PUSH' and segment == 'this':
            self._writePushRegister(index, 'THIS', False)
        elif command == 'C_POP' and segment == 'this':
            self._writePopRegister(index, 'THIS', False)
        elif command == 'C_PUSH' and segment == 'that':
            self._writePushRegister(index, 'THAT', False)
        elif command == 'C_POP' and segment == 'that':
            self._writePopRegister(index, 'THAT', False)
        elif command == 'C_PUSH' and segment == 'pointer':
            self._writePushRegister(index, 'R3', True)
        elif command == 'C_POP' and segment == 'pointer':
            self._writePopRegister(index, 'R3', True)
        elif command == 'C_PUSH' and segment == 'temp':
            self._writePushRegister(index, 'R5', True)
        elif command == 'C_POP' and segment == 'temp':
            self._writePopRegister(index, 'R5', True)
        elif command == 'C_PUSH' and segment == 'static':
            self._writeLine('@' + self._getFileName() + '.' + str(index))
            self._writeLine('D=M')
            self._setAtoSP()
            self._writeLine('M=D')
            self._incrementSP()
        elif command == 'C_POP' and segment == 'static':
            self._decrementSP()
            self._setDtoValueAtSP()
            self._writeLine('@' + self._getFileName() + '.' + str(index))
            self._writeLine('M=D')

    def writeLabel(self, label):
        self._writeLine('(' + self._currentFunctionName + '$' + label + ')')

    def writeGoto(self, label):
        self._writeLine('@' + self._currentFunctionName + '$' + label)
        self._writeLine('0;JMP')

    def writeIf(self, label):
        self._decrementSP()
        self._setDtoValueAtSP()
        self._writeLine('@' + self._currentFunctionName + '$' + label)
        self._writeLine('D;JNE')

    def writeCall(self, functionName, numArgs):
        # See page 163
        self._returnAddressCount += 1
        # Push RETURNADDRESSX on stack
        self._writeLine('@RETURNADDRESS' + str(self._returnAddressCount))
        self._writeLine('D=A')
        self._setAtoSP()
        self._writeLine('M=D')
        self._incrementSP()
        # Push LCL, ARG, THIS, THAT on stack
        self._pushLabelValueOnStack('LCL')
        self._pushLabelValueOnStack('ARG')
        self._pushLabelValueOnStack('THIS')
        self._pushLabelValueOnStack('THAT')
        # ARG = SP-n-5
        self._writeLine('@SP')
        self._writeLine('D=M')
        self._writeLine('@' + str(numArgs + 5))
        self._writeLine('D=D-A')
        self._writeLine('@ARG')
        self._writeLine('M=D')
        # LCL = SP
        self._writeLine('@SP')
        self._writeLine('D=M')
        self._writeLine('@LCL')
        self._writeLine('M=D')
        # goto f
        self._writeLine('@' + functionName)
        self._writeLine('0;JMP')
        # (RETURNADDRESSX)
        self._writeLine('(RETURNADDRESS' + str(self._returnAddressCount) + ')')

    def writeReturn(self):
        # See page 163
        # FRAME = LCL
        self._writeLine('@LCL')
        self._writeLine('D=M')
        self._writeLine('@FRAME')
        self._writeLine('M=D')
        # RET = *(FRAME-5)
        self._writeLine('D=M')
        self._writeLine('@5')
        self._writeLine('A=D-A')
        self._writeLine('D=M')
        self._writeLine('@RET')
        self._writeLine('M=D')
        # *ARG = pop()
        self._decrementSP()
        self._setAtoSP()
        self._writeLine('D=M')
        self._writeLine('@ARG')
        self._writeLine('A=M')
        self._writeLine('M=D')
        # SP = ARG + 1
        self._writeLine('@ARG')
        self._writeLine('D=M')
        self._writeLine('@SP')
        self._writeLine('M=D+1')
        # Set THAT, THIS, ARG, LCL
        self._setLabelToFrame('THAT', 1)
        self._setLabelToFrame('THIS', 2)
        self._setLabelToFrame('ARG', 3)
        self._setLabelToFrame('LCL', 4)
        # goto RET
        self._writeLine('@RET')
        self._writeLine('A=M')
        self._writeLine('0;JMP')

    def writeFunction(self, functionName, numLocals):
        # See page 163
        self._currentFunctionName = functionName
        self._writeLine('(' + functionName + ')')
        while numLocals > 0:
            self._setAtoSP()
            self._writeLine('M=0')
            self._incrementSP()
            numLocals -= 1

    def _writePushRegister(self, index, register, useRegisterDirectly):
        self._writeLine('@' + str(index))
        self._writeLine('D=A')
        self._writeLine('@' + register)
        self._writeLine('A=D+' + ('A' if useRegisterDirectly else 'M'))
        self._writeLine('D=M')
        self._setAtoSP()
        self._writeLine('M=D')
        self._incrementSP()

    def _writePopRegister(self, index, register, useRegisterDirectly):
        self._decrementSP()
        self._writeLine('@' + str(index))
        self._writeLine('D=A')
        self._writeLine('@' + register)
        self._writeLine('D=D+' + ('A' if useRegisterDirectly else 'M'))
        self._writeLine('@POPADDRESS')
        self._writeLine('M=D')
        self._setDtoValueAtSP()
        self._writeLine('@POPADDRESS')
        self._writeLine('A=M')
        self._writeLine('M=D')

    def _decrementSP(self):
        self._writeLine('@SP')
        self._writeLine('M=M-1')

    def _incrementSP(self):
        self._writeLine('@SP')
        self._writeLine('M=M+1')

    def _pushLabelValueOnStack(self, label):
        self._writeLine('@' + label)
        self._pushMonStack()

    def _pushMonStack(self):
        self._writeLine('D=M')
        self._writeLine('@SP')
        self._writeLine('A=M')
        self._writeLine('M=D')
        self._incrementSP()

    def _setLabelToFrame(self, label, offset):
        self._writeLine('@FRAME')
        self._writeLine('D=M')
        self._writeLine('@' + str(offset))
        self._writeLine('A=D-A')
        self._writeLine('D=M')
        self._writeLine('@' + label)
        self._writeLine('M=D')

    def _setDtoValueAtSP(self):
        self._writeLine('@SP')
        self._writeLine('A=M')
        self._writeLine('D=M')

    def _setAtoSP(self):
        self._writeLine('@SP')
        self._writeLine('A=M')

    def _writeLine(self, line):
        self._outFile.write(line + '\n')

    def _getFileName(self):
        return self._fileName.replace('.vm', '')

    def Close(self):
        self._outFile.close()
