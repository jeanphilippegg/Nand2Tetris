#!/usr/bin/env python3

import sys
import Code
import Parser
import SymbolTable

class Assembler:

    def __init__(self):
        self._symbolTable = SymbolTable.SymbolTable()

    def assemble(self, path):
        self.initialize()
        self.firstPass(path)
        self.secondPass(path)

    def initialize(self):
        self._symbolTable.addEntry('SP', 0)
        self._symbolTable.addEntry('LCL', 1)
        self._symbolTable.addEntry('ARG', 2)
        self._symbolTable.addEntry('THIS', 3)
        self._symbolTable.addEntry('THAT', 4)
        self._symbolTable.addEntry('R0', 0)
        self._symbolTable.addEntry('R1', 1)
        self._symbolTable.addEntry('R2', 2)
        self._symbolTable.addEntry('R3', 3)
        self._symbolTable.addEntry('R4', 4)
        self._symbolTable.addEntry('R5', 5)
        self._symbolTable.addEntry('R6', 6)
        self._symbolTable.addEntry('R7', 7)
        self._symbolTable.addEntry('R8', 8)
        self._symbolTable.addEntry('R9', 9)
        self._symbolTable.addEntry('R10', 10)
        self._symbolTable.addEntry('R11', 11)
        self._symbolTable.addEntry('R12', 12)
        self._symbolTable.addEntry('R13', 13)
        self._symbolTable.addEntry('R14', 14)
        self._symbolTable.addEntry('R15', 15)
        self._symbolTable.addEntry('SCREEN', 16384)
        self._symbolTable.addEntry('KBD', 24576)

        def firstPass(self, path):
        parser = Parser.Parser(path)

        currentAddress = 0

        while parser.hasMoreCommands():
            parser.advance()

            if parser.commandType() == Parser.Parser.A_COMMAND or parser.commandType() == Parser.Parser.C_COMMAND:
                currentAddress += 1
            else:
                self._symbolTable.addEntry(parser.symbol(), currentAddress)

    def secondPass(self, path):
        output_path = path.replace('.asm', '.hack')
        output_file = open(output_path, 'w')

        parser = Parser.Parser(path)
        code = Code.Code()

        nextAvailableAddress = 16

        while parser.hasMoreCommands():
            parser.advance()

            if parser.commandType() == Parser.Parser.A_COMMAND:
                if parser.symbol().isdigit():
                    output_file.write('0' + self._decToBin(parser.symbol()) + '\n')
                else:
                    if not self._symbolTable.contains(parser.symbol()):
                        self._symbolTable.addEntry(parser.symbol(), nextAvailableAddress)
                        nextAvailableAddress += 1
                    output_file.write('0' + self._decToBin(self._symbolTable.GetAddress(parser.symbol())) + '\n')

            elif parser.commandType() == Parser.Parser.C_COMMAND:
                output_file.write('111' + code.comp(parser.comp()) + code.dest(parser.dest()) + code.jump(parser.jump()) + '\n')

        output_file.close()

    def _decToBin(self, d):
        return bin(int(d))[2:].zfill(15)

if __name__ == '__main__':
    path = sys.argv[1]
    assembler = Assembler()
    assembler.assemble(path)
