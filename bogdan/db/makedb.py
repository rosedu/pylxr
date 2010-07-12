import sys
import os
import ConfigParser
import ctags 
from ctags import CTags, TagEntry
import sqlite3

def usage():
	print 'Usage: pyhon makedb <conf.ini>'


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
	dbpath = '.'
	filepath = '.'
	for s in parser.sections():
		if s == 'database':
			for o in parser.items(s):
				if o[0] == 'path':
					dbpath = o[1]
		if s == 'files':
			for o in parser.items(s):
				if o[0] == 'path':
					filepath = o[1]
	# file add needs work	
	try:
		f = os.path.dirname(__file__)
		print f
		os.system('ctags --fields=n -R')
	except:
		print 'ctags error'
		return 1
	
	try:
		tagFile = CTags('tags')
	except:
		print 'Error on open tags'
		return 1

	entry = TagEntry()
	
	# open database
	try:
		db = sqlite3.connect(dbpath)
		cursor = db.cursor()
	except sqlite3.Error, msg:
		print dbpath
		print msg
		return 1

	# create table
	command = 'CREATE TABLE Tags (tagID INTEGER PRIMARY KEY, ' + \
				'name TEXT NOT NULL, file TEXT NOT NULL, ' + \
				'lineNumber INTEGER NOT NULL, kind TEXT NOT NULL)'
	try : 
		cursor.execute(command)
	except sqlite3.Error, msg:
		print 'Error: ', msg
		print 'Command: ', command
	
	# add tags
	idx = 0
	stat = tagFile.first(entry)
	while stat:
		command = 'INSERT INTO Tags ' + \
			'(tagId, name, file, lineNumber, kind) values ' + \
			'(%i, \'%s\', \'%s\', \'%i\', \'%s\')' % \
			(idx, entry['name'], os.path.abspath(entry['file']), \
			entry['lineNumber'], entry['kind'])
		try:
			cursor.execute(command)
		except sqlite3.Error, msg:
			print 'Error: ', msg
			print "Command: ", command
		idx += 1
		stat = tagFile.next(entry)
	
	db.commit()
	cursor.close()
	
	
if __name__ == '__main__':
	if len(sys.argv) != 2:
		usage()
		sys.exit(1)
	sys.exit(main(sys.argv[1]))
