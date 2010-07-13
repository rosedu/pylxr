import sys
import os
import ConfigParser
import ctags 
from ctags import CTags, TagEntry
import sqlite3

def usage():
	print 'Usage: pyhon makedb <conf.ini>'


# create table with tags
def tagDB(cursor, tagFile):
	entry = TagEntry()

	# create tagls table
	command = 'CREATE TABLE Tags (' + \
				'name TEXT NOT NULL, file TEXT NOT NULL, ' + \
				'lineNumber INTEGER NOT NULL, kind TEXT NOT NULL)'
	try : 
		cursor.execute(command)
	except sqlite3.Error, msg:
		print 'Error: ', msg
		print 'Command: ', command
	
	# add tags
	stat = tagFile.first(entry)
	while stat:
		command = 'INSERT INTO Tags ' + \
			'( name, file, lineNumber, kind) values ' + \
			'( \'%s\', \'%s\', \'%i\', \'%s\')' % \
			( entry['name'], entry['file'], \
			entry['lineNumber'], entry['kind'])
		try:
			cursor.execute(command)
		except sqlite3.Error, msg:
			print 'Error: ', msg
			print "Command: ", command
		stat = tagFile.next(entry)
	

# create table with files	
def fileDB(cursor, srcpath):

	# may need more columns
	command = 'CREATE TABLE Files (' + \
			'name TEXT NOT NULL, size INTEGER NOT NULL)'
	try:
		cursor.execute(command)
	except sqlite3.Error, msg:
		print 'Error: ', msg
		print "Command: ", command
	walk(os.path.join(srcpath),cursor)

def walk(path, cursor):
	for f in  os.listdir(path):
		print f

def main(conf):
	
	parser = ConfigParser.ConfigParser()
	try:
		parser.readfp(open(conf))
	except IOError, msg:
		print msg
		return 1
	except ConfigParser.Error, msg:
		print msg
		return 1
		
	# parsing paths
	dbpath = '.'
	srcpath = '.'
	rootpath = ''
	for s in parser.sections():
		if s == 'out_db':
			for o in parser.items(s):
				if o[0] == 'path':
					dbpath = o[1]
		if s == 'src_dir':
			for o in parser.items(s):
				if o[0] == 'path':
					srcpath = o[1]
		if s == 'root':
			for o in parser.items(s):
				if o[0] == 'path':
					rootpath = o[1]
					 
	srcpath = os.path.join(rootpath, srcpath)
	dbpath = os.path.join(rootpath, dbpath)
	
	try:
		os.popen('cd %s; ctags --fields=nK -R -f %s' % \
			(srcpath, os.path.abspath(os.path.join( \
		 	os.path.dirname(__file__),  'tags'))))
	except:
		print 'ctags run error'
		return 1
	
	try:
		tagFile = CTags('tags')
	except:
		print 'Error on open tags'
		return 1


	# open database
	try:
		db = sqlite3.connect(dbpath)
		cursor = db.cursor()
	except sqlite3.Error, msg:
		print dbpath
		print msg
		return 1

	tagDB(cursor, tagFile)
	fileDB(cursor, srcpath)
	
	db.commit()
	cursor.close()
	
	#remove tags file
	os.remove(os.path.abspath(os.path.join( \
		 os.path.dirname(__file__),  'tags')))
	
	
if __name__ == '__main__':
	if len(sys.argv) != 2:
		usage()
		sys.exit(1)
	sys.exit(main(sys.argv[1]))
