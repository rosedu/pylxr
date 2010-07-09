from plex import *
from plex.traditional import re as RE

class CLexer:
    
    def __init__(self, filename):
        self.rKeyword = Str("auto") | Str("break") | Str("case") |\
            Str("char") | Str("const") | Str("continue") | Str("default") |\
            Str("do") | Str("double") | Str("else") | Str("enum") |\
            Str("extern") | Str("float") | Str("for") | Str("goto") |\
            Str("if") | Str("int") | Str("long") | Str("register") |\
            Str("return") | Str("short") | Str("signed") | Str("sizeof") |\
            Str("static") | Str("struct") | Str("switch") | Str("typedef") |\
            Str("union") | Str("unsigned") | Str("void") | Str("volatile") |\
            Str("while")
        self.rLetter = Range("AZaz")
        self.rDigit = Range("09")
        self.rDecimal = Rep1(Range("09"))
        self.rIdentifier = (self.rLetter | Str("_")) +\
            Rep(self.rLetter | self.rDigit | Str("_"))
        self.rShit = Any("{}()[];=,.|&*+-/%!:><~?\\") | RE("\?")
        self.rChar = Str("'") + Rep(Str("\\")) + AnyChar + Str("'")
        self.rSpace = RE("( )")
        self.rTab = RE("(\t)")
        self.rNewline = RE("(\n)")
        
        self.output = ""
        

        lex = Lexicon([
                (Str("/*"), self.fComment1),
                State('comment', [
                        (Str("*/"), self.fComment2),
                        (self.rTab, self.fTab),
                        (self.rNewline, self.fNewline),
                        (self.rSpace, self.fSpace),
                        (AnyChar, self.fPrint)
                        ]),
                (Str('"'), self.fString1),
                State('string', [
                        (Str('"'), self.fString2),
                        (self.rTab, self.fTab),
                        (self.rNewline, self.fNewline),
                        (self.rSpace, self.fSpace),
                        (AnyChar, self.fPrint)
                        ]),
                (RE("^\w*#"), self.fPreproc1),
                State('preproc', [
                        (Str('<'), self.fAngular1),
                        (Str('"'), self.fString3),
                        (self.rNewline, self.fPreproc2),
                        (self.rTab, self.fTab),
                        (self.rNewline, self.fNewline),
                        (self.rSpace, self.fSpace),
                        (AnyChar, self.fPrint)
                        ]),
                State('rstring', [
                        (Str('"'), self.fString4),
                        (self.rTab, self.fTab),
                        (self.rNewline, self.fNewline),
                        (self.rSpace, self.fSpace),
                        (AnyChar, self.fPrint)
                        ]),
                State('rangular', [
                        (Str('>'), self.fAngular2),
                        (self.rTab, self.fTab),
                        (self.rNewline, self.fNewline),
                        (self.rSpace, self.fSpace),
                        (AnyChar, self.fPrint)
                        ]),
                (self.rKeyword, self.fKeyword),
                (self.rIdentifier, self.fIdentifier),
                (self.rShit, self.fPrint),
                (self.rDecimal, self.fPrint),
                (self.rSpace, self.fPrint),
                (self.rChar, self.fChar),
                (self.rTab, self.fTab),
                (self.rNewline, self.fNewline)
                ])

        self.output = """<html><head><link rel=stylesheet href="style.css" type=
"text/css"></head><body>"""
        f = open(filename, "r")
        scanner = Scanner(lex, f, filename)
        while True:
            token = scanner.read()
            if token[0] is None:
                break
        self.output = self.output + "</body></html>"

    def __str__(self):
        return self.output
        
    def fComment1(self, scanner, text):
        scanner.begin('comment')
        self.output = self.output + '<span id="comment">/*'
            
    def fComment2(self, scanner, text):
        self.output = self.output + '*/</span>'
        scanner.begin('')
                
    def fKeyword(self, scanner, text):
        self.output = self.output + "".join([
                '<span id="keyword">',
                text,
                '</span>'
                ])

    def fIdentifier(self, scanner, text):
        self.output = self.output + "".join([
                '<a href="">',
                text,
                '</a>'
                ])

    def fPrint(self, scanner, text):
        self.output = self.output + text
        
    def fSpace(self, scanner, text):
        self.output = self.output + "&nbsp;"
        
    def fTab(self, scanner, text):
        self.output = self.output + "&nbsp;"*8

    def fNewline(self, scanner, text):
        self.output = self.output + "<br/>\n"

    def fChar(self, scanner, text):
        
        self.output = self.output + '<span id="string">' + text + '</span>'

    def fString1(self, scanner, text):
        scanner.begin('string')
        self.output = self.output + '<span id="string">"'

    def fString2(self, scanner, text):
        scanner.begin('')
        self.output = self.output + '"</span>'

    def fPreproc1(self, scanner, text):
        scanner.begin('preproc')
        self.output = self.output + '<span id="keyword">#'
        
    def fPreproc2(self, scanner, text):
        scanner.begin('')
        self.output = self.output + '</span><br/>'
    
    def fAngular1(self, scanner, text):
        scanner.begin('rangular')
        self.output = self.output + '<span id="string">&lt;'

    def fAngular2(self, scanner, text):
        scanner.begin('preproc')
        self.output = self.output + '&gt;</span>'
        
    def fString3(self, scanner, text):
        scanner.begin('rstring')
        self.output = self.output + '<span id="string">"'
        
    def fString4(self, scanner, text):
        scanner.begin('preproc')
        self.output = self.output + '"</span>'
            
