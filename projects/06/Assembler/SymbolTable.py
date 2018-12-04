#!/usr/bin/env python3

class SymbolTable:

    def __init__(self):
        self._symbolTable = {}

    def addEntry(self, symbol, address):
        self._symbolTable[symbol] = address

    def contains(self, symbol):
        return symbol in self._symbolTable

    def GetAddress(self, symbol):
        return self._symbolTable[symbol]
