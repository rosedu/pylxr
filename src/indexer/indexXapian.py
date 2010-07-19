import sys
import xapian
import os

state = 0

def ignoreStrComm(line):
	''' ignore words in strings and comments'''
	global state

	ret = ''
	l = len(line)
	crt = 0
	while l != crt:
		if state == 0:
			if line[crt] == '\"':
				state = 1
				crt += 1
				ret += ' '
			elif line[crt] == '/' and crt+1 != l and line[crt+1] == '/':
				ret += '\n'
				return ret
			elif line[crt] == '/' and crt+1 != l and line[crt+1] == '*':
				crt += 2
				state = 2
				ret += ' '
			else:
				ret += line[crt]
				crt += 1
		elif state == 1:
			if line[crt] != '\\' and crt+1 != l and line[crt+1] == '\"':
				crt += 2
				state = 0
			else:
				crt += 1
		elif state == 2:
			if line[crt] == '*' and crt+1 != l and line[crt+1] == '/':
				crt += 2
				state = 0
			else:
				crt += 1
		else:
			ret += line[crt]
			crt += 1
	return ret
	

def indexFile(top, fname, db, indexer): 
	''' add file lines to xapian database '''
	
	f = open(os.path.join(top,fname), 'r')
	for idx,line in enumerate(f):
		doc = xapian.Document()
		line = ignoreStrComm(line).strip()
		if line != '':
			doc.set_data(line)
			doc.add_value(0, str(fname))
			doc.add_value(1, str(idx+1)) 
	
		indexer.set_document(doc)
		indexer.index_text(line)
		db.add_document(doc)


def main(dbpath, fname):
	try:
		db = xapian.WritableDatabase(dbpath, xapian.DB_CREATE_OR_OPEN)	
	except:
		print 'Error opening xapian database'
		sys.exit(1)
		
		
	indexer = xapian.TermGenerator()
	
	indexFile('.', fname, db, indexer)
	

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'Need path & file'
		sys.exit(1)
	else:
		main(sys.argv[1], sys.argv[2])

