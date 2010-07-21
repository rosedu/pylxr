from plex import *
from plex.traditional import re as RE
import sys
import os

class Lexer:
    def __init__(self, filename, dbfile):
        self.rKeyword = Str("and") | Str("as") | Str("assert") |\
            Str("break") | Str("class") | Str("continue") | Str("def") |\
            Str("del") | Str("elif") | Str("else") | Str("except") |\
            Str("exec") | Str("finally") | Str("for") | Str("from") |\
            Str("global") | Str("if") | Str("import") | Str("in") |\
            Str("is") | Str("lambda") | Str("not") | Str("or") |\
            Str("pass") | Str("print") | Str("raise") | Str("return") |\
            Str("try") | Str("while") | Str("with") | Str("yield")

        self.rComment = Str("#") + Rep(AnyChar) + Eol
        
        self.rLetter = Range("AZaz")
        self.rDigit = Range("09")

        self.rIdentifier = (self.rLetter | Str("_")) +\
            Rep(self.rLetter | self.rDigit | Str("_"))

        # Strings 
        self.rLongStringItem = AnyBut('\\')
        self.rShortStringItemDQ = AnyBut('\\\n"') | RE("\\.")
        self.rShortSrtingItemQ = AnyBut("\\\n'") | RE("\\.")
        self.rLongString = (Str("'''") + Rep(self.rLongStringItem) +\
                                 Str("'''")) |\
            (Str('"""') + Rep(self.rLongStringItem) + Str('"""'))
        self.rShortString = (Str("'") + Rep(self.rShortStringItemQ) +\
                                 Str("'")) |\
            (Str('"') + Rep(self.rShortStringItemDQ) + Str('"'))
        self.rStringPrefix = Str("r", "u", "ur", "R", "U", "UR", "Ur", "uR")
        self.rStringLiteral = Opt(self.rStringPrefix) +\
            (self.rShortString | self.rLongString)

        self.rOperators = Str("+","-","*","**","/","//","%","<<",">>","&",\
                                  "|","^","~","<",">","<=",">=","==","!=",\
                                  "<>")
        self.rDelimiters = Str("(",")","[","]","{","}","@",",",":",".","`",\
                                   "=",";","+=","-=","*=","/=","//=","%=",\
                                   "&=","|=","^=",">>=","<<=","**=")

        lex = Lexicon([
                (self.rKeyword, self.fKeyword),
                (self.rComment, self.fComment),
                (self.rIdentifier, self.fIdentifier),
                (self.rStringLiteral, self.fStringLiteral),
                (self.rOperators, self.fPrint),
                (self.rDelimiters, self.fPrint),
                (AnyChar, self.fPrint)
                ])

        self.__filename = filename
        self.__lines = []
        self.__tmpLine = None
        self.__tmpElem = None
        
        ipath = os.path.join(os.path.dirname(__file__), "../dbaccess")
        sys.path.append(ipath)
        self.DB = __import__("dbsearch").DBSearch(dbfile)

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

    def safe_add(self, elem=None):
        if self.__tmpLine is None:
            self.__tmpLine = []
        if self.__tmpElem is not None:
            self.__tmpLine.append(self.__tmpElem)
        self.__tmpElem = None
        
        if elem is not None:
            self.__tmpLine.append(elem)

    # Matching methods
    def fKeyword(self, scanner, text):
        self.safe_add()
        self.safe_add( ('keyword',text) )

    def fComment(self, scanner, text):
        self.safe_add()
        self.safe_add( ('comment', text) )

    def fIdentifier(self, scanner, text):
        tag = self.DB.searchTag(text, self.__filename)
        r = {'disp':text}
        if tag is None:
            r['link'] = None
        else:
            (f,l,k) = tag
            r['link'] = "?r=/%s#%s" % (f,l)

        self.safe_add()
        self.safe_add( ('identifier',r) )

    def fStringLiteral(self, scanner, text):
        self.safe_add()
        self.safe_add( ('string', text) )

    def fPrint(self, scanner, text):
        escape = {"<":"&lt;", ">":"&gt;", " ":"&nbsp;", "&":"&amp;",\
                      "\"":"&quot;", "\t":" "*8}
        for (l,t) in escape.items():
            text = text.replace(l,t)
        
        (a,b) = self.__tmpElem
        self.__tmpElem = (a, b+text)
