import sqlite3
import sys

def search(database, tag):
	db = sqlite3.connect(database)
	cursor = db.cursor()
	
	command = 'SELECT file, lineNumber FROM Tags WHERE name=\'%s\'' % tag
	cursor.execute(command)
	
	return cursor.fetchall()
		
if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'Invalid args'
		sys.exit(1)
	print search(sys.argv[1], sys.argv[2])
