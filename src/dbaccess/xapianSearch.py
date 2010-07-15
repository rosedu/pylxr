import sys
import xapian
import os

def search(dbpath, qry):
	'''
	Use for xapian database query
	++ [(file, lineNumber)]
	'''
	try:
		db = xapian.Database(dbpath)
	except:
		print 'Error opening database'

	enquire = xapian.Enquire(db)
	qp = xapian.QueryParser()
	
	qp.set_database(db)
	qp.set_stemming_strategy(xapian.QueryParser.STEM_NONE)
	
	query = qp.parse_query(qry)

	enquire.set_query(query)
	
	ret = []
	for m in enquire.get_mset(0,200):
		ret.append((m.document.get_value(0), \
				int(m.document.get_value(1))))
	return ret

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'Need path & query' 
		sys.exit(1)
	else:
		print search(sys.argv[1], sys.argv[2])
