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

        if os.path.isdir(path):
            vmFiles = [file for file in os.listdir(path) if file.endswith('.vm')]
            for vmFile in vmFiles:
                self._translateVMfile(path + '/' + vmFile)
        else:
            self._translateVMfile(path)

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

if __name__ == '__main__':
    path = sys.argv[1]
    vmtranslator = VMtranslator()
    vmtranslator.translate(path)
