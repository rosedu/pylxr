import sqlite3
import sys
import re
import random

def help():
	print 'Command list:'
	print 'python sql.py <query> -> executes query (default database newdb)'
	print 'python sql.py <db> <tab> insert <n> -> inserts', \
		'n random entries in database db, table tab'
	print 'python sql.py help -> prints command list'


def query(q):
	try:
		db = sqlite3.connect('newdb')
	except:
		print 'Error conecting to newdb'
		sys.exit(1)
	cursor = db.cursor()
	try:
		cursor.execute(q)
	except sqlite3.OperationalError, msg:
		print msg
	else:
		if q.lstrip().upper()[:6] == 'SELECT':
			for row in cursor:
				print row
		else:
			db.commit()
	cursor.close()	

def insert(dbase, tab, n):
	try:
		db = sqlite3.connect(dbase, detect_types=sqlite3.PARSE_DECLTYPES)
		cursor = db.cursor()
	
		# get column names
		cursor.execute("SELECT * FROM %s" % tab)
		col_name = [tuple[0] for tuple in cursor.description]
		alphabet = 'abcdefghijklmnopqrstuvwxyz'
		col_type = []
		for col in col_name:
			cursor.execute("SELECT typeof(%s) FROM %s" % (col, tab))
			col_type.append([cursor.fetchall()[0][0]])
	except sqlite3.Error, msg:
		print msg
		sys.exit(1)
	
	nr = 0
	base_id = 100
	while(1):
		if nr == n:
			break;
		values = ''
		for col in col_type:
			if col[0] == 'text':
				values += '\''
				for char in random.sample(alphabet, random.randint(5,10)):
					values += char
				values += "\',"
			if col[0] == 'integer':
				values += str(random.randint(1, base_id)) + ','	
		values = values.rstrip(',')
		# try to insert, may not work because of unique keys
		try:
			cursor.execute("INSERT INTO %s VALUES (%s)" % (tab, values))
			nr = nr + 1
		except sqlite3.Error, msg:
			base_id += 10

	try:
		db.commit()
		cursor.close()
	except sqlite3.Error, msg:
		print msg

def main():
	if(len(sys.argv) == 2):
		if sys.argv[1] == 'help':
			help()
		else:
			query(sys.argv[1])
	else:
		if(len(sys.argv) == 5 and sys.argv[3] == 'insert'):
			insert(sys.argv[1], sys.argv[2], int(sys.argv[4]))
		else:
			print 'Invalid script call'
			help()


if __name__ == '__main__':
	main()
