from plex import *

''' lexicon definition -> work in progress '''

letter = Range('AZaz')
digit = Range('09')
preproc = Str('#') + Rep(AnyBut('\n')) + Str('\n')
name = Rep1(letter | Str('_')) + Rep(letter | digit | Str('_'))
number = Rep1(digit) | (Str('0x') + Rep1(digit))
special = Any('#{}()[];=,.^|&*+-/%!:><~?\\')
comment1 = Str('//') + Rep(AnyBut('\n')) + Str('\n')
space = Any(' \t\n')

lex = Lexicon( [ \
	(preproc | comment1, IGNORE), \
	(Str('/*'), Begin('comment')), 
	State('comment' , [ \
		(Str('*/'), Begin('')),
		(AnyChar, IGNORE) \
	]), \
	(name, TEXT), \
	(special | number | space, IGNORE) \
])

def getScanner(self, fname):
	f = open(fname, 'r')
	return  Scanner(lex, f, fname)


def indexFile(fname, cursor):
	sc = getScanner(lex, fname)
	while True:
		tok = sc.read()
		print tok
		print sc.position()
		if tok[0] is None:
			break
