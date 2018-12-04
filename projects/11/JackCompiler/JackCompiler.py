#!/usr/bin/env python3

import os
import sys
import CompilationEngine

class JackCompiler:

    def compile(self, path):
        if os.path.isdir(path):
            jackFiles = [file for file in os.listdir(path) if file.endswith('.jack')]
            for jackFile in jackFiles:
                self._compileFile(path + '/' + jackFile)
        else:
            self._compileFile(path)

    def _compileFile(self, inputPath):
        outputPath = inputPath.replace('.jack', '.vm')
        compilationEngine = CompilationEngine.CompilationEngine(inputPath, outputPath)
        compilationEngine.CompileClass()

if __name__ == '__main__':
    path = sys.argv[1]
    jackCompiler = JackCompiler()
    jackCompiler.compile(path)
