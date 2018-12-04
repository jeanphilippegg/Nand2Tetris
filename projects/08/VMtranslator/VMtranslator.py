#!/usr/bin/env python3

import os
import sys
import CodeWriter
import Parser

class VMtranslator:

    def translate(self, path):
        if os.path.isdir(path):
            output_path = path + '/' + os.path.basename(path) + '.asm'
        else:
            output_path = path.replace('.vm', '.asm')

        self._codeWriter = CodeWriter.CodeWriter(output_path)

        # Comment the following line to make previous programs work (chapter 7 and 3 first programs of chapter 8)
        self._codeWriter.writeInit()

        if os.path.isdir(path):
            vmFiles = [file for file in os.listdir(path) if file.endswith('.vm')]
            for vmFile in vmFiles:
                self._translateVMfile(path + '/' + vmFile)
        else:
            self._translateVMfile(path)

        self._codeWriter.Close()

    def _translateVMfile(self, path):
        parser = Parser.Parser(path)
        filename = os.path.basename(path)
        self._codeWriter.setFileName(filename)

        while parser.hasMoreCommands():
            parser.advance()

            if parser.commandType() == parser.C_ARITHMETIC:
                self._codeWriter.writeArithmetic(parser.arg1())
            elif parser.commandType() == parser.C_PUSH:
                self._codeWriter.WritePushPop('C_PUSH', parser.arg1(), int(parser.arg2()))
            elif parser.commandType() == parser.C_POP:
                self._codeWriter.WritePushPop('C_POP', parser.arg1(), int(parser.arg2()))
            elif parser.commandType() == parser.C_LABEL:
                self._codeWriter.writeLabel(parser.arg1())
            elif parser.commandType() == parser.C_GOTO:
                self._codeWriter.writeGoto(parser.arg1())
            elif parser.commandType() == parser.C_IF:
                self._codeWriter.writeIf(parser.arg1())
            elif parser.commandType() == parser.C_CALL:
                self._codeWriter.writeCall(parser.arg1(), int(parser.arg2()))
            elif parser.commandType() == parser.C_RETURN:
                self._codeWriter.writeReturn()
            elif parser.commandType() == parser.C_FUNCTION:
                self._codeWriter.writeFunction(parser.arg1(), int(parser.arg2()))

if __name__ == '__main__':
    path = sys.argv[1]
    vmtranslator = VMtranslator()
    vmtranslator.translate(path)
