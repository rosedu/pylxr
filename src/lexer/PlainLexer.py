from plex import *
from plex.traditional import re as RE
import sys
import os

class Lexer:
    def __init__(self, filename, dbfile):
        self.rNewline = RE("(\n)")
        
        self.__filename = filename
        self.__lines = []
        self.__tmpLine = None
        self.__tmpElem = None
        self.__state = ''

        lex = Lexicon([
                (self.rNewline, self.fNewline),
                (AnyChar, self.fPrint)
            ])

        self.create_output(lex, filename)

    def create_output(self, lex, filename):
        f = open(filename, "r")
        scanner = Scanner(lex, f, filename)
        while True:
            token = scanner.read()
            if token[0] is None:
                break

            if self.__tmpLine is not None:
                self.__lines.append(self.__tmpLine)

    def get(self):
        return self.__lines

    def fPrint(self, scanner, text):
        escape = {"<":"&lt;", ">":"&gt;", " ":"&nbsp;", "&":"&amp;", "\"":"&quot;"}
        if text in escape:
            text = escape[text]
        if self.__tmpElem is None:
            self.__tmpElem = ('print', '')
        (a,b) = self.__tmpElem
        self.__tmpElem  = (a, b+text)


    def fNewline(self, scanner, text):
        if self.__tmpLine is None:
            self.__tmpLine = []
        if self.__tmpElem is not None:
            self.__tmpLine.append(self.__tmpElem)

        self.__lines.append(self.__tmpLine)
        self.__tmpLine = None
        self.__tmpElem = None
