from plex import *
import os
import sqlite3

''' lexicon definition -> work in progress '''

letter = Range('AZaz')
digit = Range('09')
preproc = Str('#') + Rep(AnyBut('\n')) + Str('\n')
name = Rep1(letter | Str('_')) + Rep(letter | digit | Str('_'))
number = Rep1(digit) | (Str('0x') + Rep1(digit))
special = Any('{}()[];=,.^|&*+-/%!:><~?\\')
comment1 = Str('//') + Rep(AnyBut('\n')) + Str('\n')
space = Any(' \t\n')

lex = Lexicon( [ \
	(preproc | comment1, IGNORE), \
	(Str('/*'), Begin('comment2')), 
	State('comment2' , [ \
		(Str('*/'), Begin('')),
		(AnyChar, IGNORE) \
	]), \
	(Str('\"'), Begin('dquote')), 
	State('dquote' , [ \
		(Str('\\\"'), IGNORE), \
		(Str('\"'), Begin('')),
		(AnyChar, IGNORE) \
	]), \
	(Str('\''), Begin('quote')), \
	State('quote' , [ \
		(Str('\\\''), IGNORE), \
		(Str('\''), Begin('')),
		(AnyChar, IGNORE) \
	]), \
	(name, TEXT), \
	(special | number | space, IGNORE) \
])

def getScanner(self, fname):
	f = open(fname, 'r')
	return  Scanner(lex, f, fname)



def indexFile(top, fname, cursor):
	''' generate entries in table Search for tokens '''
	
	sc = getScanner(lex, os.path.join(top, fname))

	command = 'SELECT * FROM Tags WHERE file=\'%s\'' % fname
	try:
		cursor.execute(command)
	except sqlite3.Error, msg:
		print 'Error: ', msg
		print "Command: ", command
		
	tags = map(lambda x : x[0].encode(), cursor.fetchall())
	
	while True:
		tok = sc.read()
		if tok[0] is None:
			break
		if tok[0] in tags:
			command = 'INSERT INTO Search (tag, file, lineNumber) ' + \
				'values (\'%s\', \'%s\', %i) ' % \
				(tok[0], fname, sc.position()[1])
			try:
				cursor.execute(command)
			except sqlite3.Error, msg:
				print 'Error: ', msg
				print "Command: ", command
		
			
			
