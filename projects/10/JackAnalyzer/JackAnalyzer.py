#!/usr/bin/env python3

import os
import sys
import CompilationEngine

class JackAnalyzer:

    def analyze(self, path):
        if os.path.isdir(path):
            jackFiles = [file for file in os.listdir(path) if file.endswith('.jack')]
            for jackFile in jackFiles:
                self._analyzeFile(path + '/' + jackFile)
        else:
            self._analyzeFile(path)

    def _analyzeFile(self, inputPath):
        outputPath = inputPath.replace('.jack', '.xml')
        outputFile = open(outputPath, 'w')
        compilationEngine = CompilationEngine.CompilationEngine(inputPath, outputFile)
        compilationEngine.CompileClass()
        outputFile.close()

if __name__ == '__main__':
    path = sys.argv[1]
    jackAnalyzer = JackAnalyzer()
    jackAnalyzer.analyze(path)
