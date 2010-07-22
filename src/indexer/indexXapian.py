import sys
import xapian
import os

def indexFile(top, fname, db, indexer, lang): 
	''' add file lines to xapian database '''
	
	try:
		module = __import__(name='lang.'+lang,fromlist=['CommentParser'])
		ign = module.CommentParser()
	except:
		lang = None
	
	f = open(os.path.join(top,fname), 'r')
	for idx,line in enumerate(f):
		doc = xapian.Document()
		if lang != None: 
			line = ign.ignoreComment(line).strip()
		else:
			line = line.strip()
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

