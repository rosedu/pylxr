from mod_python import apache
import os
import sqlite3

def prnt(string):
	return """ <html> <body> Error !!! <br /> Msg: %s </body> </html>""" % string 

cale = '/home/quible/pylxr/bogdan/db'


def index(req):
	return """
		<html>
		<form action="index.py/linkaux" method="POST">
			Fname <input type="text" name="fname"> <br />
			<input type="submit">
		</form>
		</html>
	"""

def linkaux(req):
	info = req.form
	return link(info['fname'])

def link(fname):
	global cale
	
	color = apache.import_module('color', path = [cale])
	usedb = apache.import_module('usedb', path = [cale])
	
	toks = []
	try:
		f = open(fname, 'r')
		toks = color.tokenize(f.read())
		f.close()
	except:
		return prnt(fname)

	db = os.path.join(cale, 'newdb')

	s  = '<html> <body>' 

	for tok in toks:
		entry = []
		try:
			entry = usedb.search(db, tok)
		except sqlite3.Error,msg:
			prnt(msg)
			
		if tok == '\n':
			s += '<br />'
		elif tok == '<':
			s += '&lt;'
		elif tok == '\t':
			for x in range(8):
				s += '&nbsp;'
		elif len(entry) > 0:
			s += '<a href ="link?fname=%s"> %s </a>' \
				% (entry[0][0].encode(),tok)
		else:
			s += tok 
		
	s += '</body> </html>'
	return s

