from plex import *
from plex.traditional import re as RE
import sys
import os

class CLexer:
    def __init__(self, ffilename, dbfile):
        self.rKeyword = Str("auto") | Str("break") | Str("case") |\
            Str("char") | Str("const") | Str("continue") | Str("default")|\
            Str("do") | Str("double") | Str("else") | Str("enum") |\
            Str("extern") | Str("float") | Str("for") | Str("goto") |\
            Str("if") | Str("int") | Str("long") | Str("NULL") |\
            Str("register") | Str("return") | Str("short") |\
            Str("signed") | Str("sizeof") | Str("static") | Str("struct")|\
            Str("switch") | Str("typedef") | Str("union") |\
            Str("unsigned") | Str("void") | Str("volatile") | Str("while")
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
        
        self.__filename = ffilename
        self.__lines = []
        self.__tmpLine = None
        self.__tmpElem = None
        self.__state = ''

        lex = Lexicon([
                # Comments
                (Str("/*"), self.fStartComment),
                State('comment', [
                        (Str("*/"), self.fEndComment),
                        (self.rTab, self.fTab),
                        (self.rNewline, self.fNewline),
                        (self.rSpace, self.fSpace),
                        (AnyChar, self.fPrint)
                        ]),
                # Strings
                (Str('"'), self.fStartString),
                State('string', [
                        (Str('"'), self.fEndString),
                        (self.rTab, self.fTab),
                        (self.rNewline, self.fNewline),
                        (self.rSpace, self.fSpace),
                        (AnyChar, self.fPrint)
                        ]),
                # Include directives
                (RE("^\w*#(include)"), self.fStartInclude),
                State('include', [
                        (Str('<'), self.fStartAngularReference),
                        (Str('"'), self.fStartStringReference),
                        (self.rNewline, self.fEndInclude),
                        (self.rTab, self.fTab),
                        (self.rSpace, self.fSpace),
                        (AnyChar, self.fPrint)
                        ]),
                # Other preprocessor directives
                (RE("^\w*#"), self.fStartPreprocessor),
                State('preproc', [
                        (self.rNewline, self.fEndPreprocessor),
                        (self.rTab, self.fTab),
                        (self.rSpace, self.fSpace),
                        (AnyChar, self.fPrint)
                        ]),
                # String reference
                State('rstring', [
                        (Str('"'), self.fEndStringReference),
                        (self.rTab, self.fTab),
                        (self.rNewline, self.fNewline),
                        (self.rSpace, self.fSpace),
                        (AnyChar, self.fPrint)
                        ]),
                # Angular reference
                State('rangular', [
                        (Str('>'), self.fEndAngularReference),
                        (self.rTab, self.fTab),
                        (self.rNewline, self.fNewline),
                        (self.rSpace, self.fSpace),
                        (AnyChar, self.fPrint)
                        ]),
                # Other stuff
                (self.rKeyword, self.fKeyword),
                (self.rIdentifier, self.fIdentifier),
                #(self.rShit, self.fPrint),
                (self.rDecimal, self.fPrint),
                (self.rSpace, self.fPrint),
                (self.rChar, self.fChar),
                (self.rTab, self.fTab),
                (self.rNewline, self.fNewline),
                (AnyChar, self.fPrint)
                ])

        ipath = os.path.join(os.path.dirname(__file__), "../dbaccess/")
        sys.path.append(ipath)
        self.DB = __import__("dbsearch").DBSearch(dbfile)

        self.create_output(lex, ffilename)

    def create_output(self, lex, ffilename):
        try:
            f = open(ffilename, "r")
            scanner = Scanner(lex, f, ffilename)
            while True:
                token = scanner.read()
                if token[0] is None:
                    break
                
                if self.__tmpLine is not None:
                    self.__lines.append(self.__tmpLine)
        except Exception as ex:
            s = str(scanner.position())
            raise Exception(s + '\n\n' + str(ex))

    def get(self):
        return self.__lines

    # HANDLERS  
    def fKeyword(self, scanner, text):
        if self.__tmpLine is None:
            self.__tmpLine = []
        if self.__tmpElem is not None:
            self.__tmpLine.append(self.__tmpElem)
        self.__tmpLine.append( ('keyword', text) )

        self.__tmpElem = None

        
    def fIdentifier(self, scanner, text):
        tag = self.DB.searchTag(text,self.__filename)
#        tag = self.DB.searchTag(text)
        r = {'disp': text}
        if tag is None:
            r['link'] = None
        else:
            (f,l,k) = tag
            r['link'] = "?r=/%s#%s" % (f,l)

        if self.__tmpLine is None:
            self.__tmpLine = []
        if self.__tmpElem is not None:
            self.__tmpLine.append(self.__tmpElem)
        self.__tmpLine.append( ('identifier', r) )

        self.__tmpElem = None


    def fPrint(self, scanner, text):
        if self.__tmpElem is None:
            self.__tmpElem = ('print', '')
        (a,b) = self.__tmpElem
        self.__tmpElem  = (a, b+text)

        
    def fSpace(self, scanner, text):
        c = "&nbsp;" # Space char

        if self.__tmpElem is None:
            self.__tmpElem = ('print', '')
        (a,b) = self.__tmpElem
        self.__tmpElem  = (a, b+c)

        
    def fTab(self, scanner, text):
        c = "&nbsp;" * 8 # Tab char

        if self.__tmpElem is None:
            self.__tmpElem = ('print', '')
        (a,b) = self.__tmpElem
        self.__tmpElem  = (a, b+c)

        
    def fNewline(self, scanner, text):
        if self.__tmpElem is not None:
            if self.__tmpLine is None:
                self.__tmpLine = []
            self.__tmpLine.append(self.__tmpElem)
            (a,b) = self.__tmpElem
            self.__tmpElem = (a, '')
            
        self.__lines.append(self.__tmpLine)
        self.__tmpLine = None
        self.__tmpElem = None
        


    def fChar(self, scanner, text):
        if self.__tmpLine is None:
            self.__tmpLine = []
        self.__tmpLine.append( ('char', text) )

        self.__tmpElem = None

        
    def fStartComment(self, scanner, text):
        if self.__tmpElem is not None:
            if self.__tmpLine is None:
                self.__tmpLine = []
            self.__tmpLine.append(self.__tmpElem)
            
        scanner.begin('comment')
        self.__state = 'comment'
        self.__tmpElem = ('comment', '/*')
        
            
    def fEndComment(self, scanner, text):
        scanner.begin('')
        self.__state = ''
        b = ''
        if self.__tmpElem is not None:
            (a,b) = self.__tmpElem
        self.__tmpElem = ('comment', b+'*/')

        if self.__tmpLine is None:
            self.__tmpLine = []
        self.__tmpLine.append(self.__tmpElem)
        self.__tmpElem = None


        
    def fStartString(self, scanner, text):
        if self.__tmpElem is not None:
            if self.__tmpLine is None:
                self.__tmpLine = []
            self.__tmpLine.append(self.__tmpElem)
            
        scanner.begin('string')
        self.__state = 'string'
        self.__tmpElem = ('string', '"')


    def fEndString(self, scanner, text):
        scanner.begin('')
        self.__state = ''
        (a,b) = self.__tmpElem
        self.__tmpElem = (a, b+'"')
        
        if self.__tmpLine is None:
            self.__tmpLine = []
        self.__tmpLine.append(self.__tmpElem)
        self.__tmpElem = None


    def fStartPreprocessor(self, scanner, text):
        if self.__tmpElem is not None:
            if self.__tmpLine is None:
                self.__tmpLine = []
            self.__tmpLine.append(self.__tmpElem)
            
        scanner.begin('preproc')
        self.__state = 'preproc'
        self.__tmpElem = ('preprocessor', text)
        
    def fEndPreprocessor(self, scanner, text):
        scanner.begin('')
        self.__state = ''
        (a,b) = self.__tmpElem
        self.__tmpElem = (a, b)
        
        if self.__tmpLine is None:
            self.__tmpLine = []
        self.__tmpLine.append(self.__tmpElem)
        self.__tmpElem = None
        
        self.__lines.append(self.__tmpLine)
        self.__tmpLine = None

        
    def fStartInclude(self, scanner, text):
        if self.__tmpElem is not None:
            if self.__tmpLine is None:
                self.__tmpLine = []
            self.__tmpLine.append(self.__tmpElem)
            
        scanner.begin('include')
        self.__state = 'include'
        self.__tmpElem = ('preprocessor', text)
        
        if self.__tmpLine is None:
            self.__tmpLine = []
        self.__tmpLine.append(self.__tmpElem)
        
    def fEndInclude(self, scanner, text):
        scanner.begin('')
        self.__state = ''

        self.__lines.append(self.__tmpLine)
        self.__tmpLine = None
        self.__tmpElem = None        

    
    def fStartAngularReference(self, scanner, text):
        if self.__tmpElem is not None:
            if self.__tmpLine is None:
                self.__tmpLine = []
            self.__tmpLine.append(self.__tmpElem)
            
        scanner.begin('rangular')
        self.__state = 'rangular'
        self.__tmpElem = ('string', '&lt;')


    def fEndAngularReference(self, scanner, text):
        scanner.begin('include')
        self.__state = 'include'
        (a,b) = self.__tmpElem
        self.__tmpElem = (a, b+'&gt')
        
        if self.__tmpLine is None:
            self.__tmpLine = []
        self.__tmpLine.append(self.__tmpElem)
        self.__tmpElem = None

        
    def fStartStringReference(self, scanner, text):
        if self.__tmpElem is not None:
            if self.__tmpLine is None:
                self.__tmpLine = []
            self.__tmpLine.append(self.__tmpElem)
            
        scanner.begin('rstring')
        self.__state = 'rstring'
        self.__tmpElem = ('string', '"')

        
    def fEndStringReference(self, scanner, text):
        scanner.begin('include')
        self.__state = 'include'
        (a,b) = self.__tmpElem
        self.__tmpElem = (a, b+'"')
        
        if self.__tmpLine is None:
            self.__tmpLine = []
        self.__tmpLine.append(self.__tmpElem)
        self.__tmpElem = None

            
