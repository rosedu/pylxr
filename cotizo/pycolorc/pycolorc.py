from plex import *
from plex.traditional import re as RE
import sys

# Rules
rKeyword = Str("auto") | Str("break") | Str("case") | Str("char") |\
    Str("const") | Str("continue") | Str("default") | Str("do") |\
    Str("double") | Str("else") | Str("enum") | Str("extern") |\
    Str("float") | Str("for") | Str("goto") | Str("if") | Str("int") |\
    Str("long") | Str("register") | Str("return") | Str("short") |\
    Str("signed") | Str("sizeof") | Str("static") | Str("struct") |\
    Str("switch") | Str("typedef") | Str("union") | Str("unsigned") |\
    Str("void") | Str("volatile") | Str("while")
rLetter = Range("AZaz")
rDigit = Range("09")
rDecimal = Rep1(Range("09"))
rIdentifier = (rLetter | Str("_")) + Rep(rLetter | rDigit | Str("_"))
rShit = Any("{}()[];=,.|&*+-/%!:><~?\\") | RE("\?")
rChar = Str("'") + Rep(Str("\\")) + AnyChar + Str("'")
rSpace = RE("( )")
rTab = RE("(\t)")
rNewline = RE("(\n)")
rPreprocessor = Str("#") + (Str("define") | Str("else") | Str("endif") |\
    Str("ifndef") | Str("ifdef") | Str("if") | Str("include") |\
    Str("undef"))

output = ""

def fComment1(scanner, text):
    scanner.begin('comment')
    global output
    output = output + '<span id="comment">/*'

def fComment2(scanner, text):
    global output
    output = output + '*/</span>'
    scanner.begin('')
    
def fKeyword(scanner, text):
    global output
    output = output + "".join([
            '<span id="keyword">',
            text,
            '</span>'
        ])

def fIdentifier(scanner, text):
    global output
    output = output + "".join([
            '<a href="">',
            text,
            '</a>'
        ])

def fPrint(scanner, text):
    global output
    output = output + text

def fSpace(scanner, text):
    global output
    output = output + "&nbsp;"
    
def fTab(scanner, text):
    global output
    output = output + "&nbsp;"*8

def fNewline(scanner, text):
    global output
    output = output + "<br/>\n"

def fChar(scanner, text):
    global output
    output = output + '<span id="string">' + text + '</span>'

def fString1(scanner, text):
    scanner.begin('string')
    global output
    output = output + '<span id="string">"'

def fString2(scanner, text):
    scanner.begin('')
    global output
    output = output + '"</span>'

def fPreproc1(scanner, text):
    scanner.begin('preproc')
    global output
    output = output + '<span id="keyword">#'
    
def fPreproc2(scanner, text):
    scanner.begin('')
    global output
    output = output + '</span><br/>'
    
def fAngular1(scanner, text):
    scanner.begin('rangular')
    global output
    output = output + '<span id="string">&lt;'

def fAngular2(scanner, text):
    scanner.begin('preproc')
    global output
    output = output + '&gt;</span>'

def fString3(scanner, text):
    scanner.begin('rstring')
    global output
    output = output + '<span id="string">"'

def fString4(scanner, text):
    scanner.begin('preproc')
    global output
    output = output + '"</span>'
    
# Lexicon
lex = Lexicon([
        (Str("/*"), fComment1),
        State('comment', [
                (Str("*/"), fComment2),
                (rTab, fTab),
                (rNewline, fNewline),
                (rSpace, fSpace),
                (AnyChar, fPrint)
                ]),
        (Str('"'), fString1),
        State('string', [
                (Str('"'), fString2),
                (rTab, fTab),
                (rNewline, fNewline),
                (rSpace, fSpace),
                (AnyChar, fPrint)
                ]),
        (RE("^\w*#"), fPreproc1),
        State('preproc', [
                (Str('<'), fAngular1),
                (Str('"'), fString3),
                (rPreprocessor, fPrint),
                (rNewline, fPreproc2),
                (rTab, fTab),
                (rNewline, fNewline),
                (rSpace, fSpace),
                (AnyChar, fPrint)
                ]),
        State('rstring', [
                (Str('"'), fString4),
                (rTab, fTab),
                (rNewline, fNewline),
                (rSpace, fSpace),
                (AnyChar, fPrint)
                ]),
        State('rangular', [
                (Str('>'), fAngular2),
                (rTab, fTab),
                (rNewline, fNewline),
                (rSpace, fSpace),
                (AnyChar, fPrint)
                ]),
        (rKeyword, fKeyword),
        (rIdentifier, fIdentifier),
        (rShit, fPrint),
        (rDecimal, fPrint),
        (rSpace, fPrint),
        (rChar, fChar),
        (rTab, fTab),
        (rNewline, fNewline)
])

def main(argv=None):
    if argv==None:
        argv = sys.argv[1:]
    # Header
    print """<html><head><link rel=stylesheet href="style.css" type=
"text/css"></head><body>"""

    filename = argv[0]
    f = open(filename, "r")
    scanner = Scanner(lex, f, filename)

    while True:
        token = scanner.read()
#        print token[0], token[1]
        if token[0] is None:
            break

    # Footer
    print """</body></html>"""

    print output
    return 0
    

if __name__=='__main__':
    sys.exit(main())
