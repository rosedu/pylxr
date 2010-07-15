import sys
import os
import ConfigParser 
import getopt
from ctags import CTags, TagEntry
import sqlite3
from stat import *
import subprocess
import xapian
import indexXapian

# Commenting indexSearch out for the time being.
# import indexSearch


def usage():
	''' print usage'''

	print 'Usage:'
	print '\tpython indexer.py'
	print 'or'
	print '\tpython indexer.py -c <conf.ini>'	

def tagDB(cursor, tagFile):
	''' create table with tags'''

	entry = TagEntry()

	# create tagls table
	command = 'CREATE TABLE IF NOT EXISTS Tags (' + \
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
			'(name, file, lineNumber, kind) values ' + \
			'(\'%s\', \'%s\', \'%i\', \'%s\')' % \
			( entry['name'], entry['file'], \
			entry['lineNumber'], entry['kind'])
		try:
			cursor.execute(command)
		except sqlite3.Error, msg:
			print 'Error: ', msg
			print "Command: ", command
		stat = tagFile.next(entry)
	

	
def fileDB(cursor, srcpath, dbpath):
	''' create table with files and search tokens'''
	
	# may need more columns
	command = 'CREATE TABLE IF NOT EXISTS Files (' + \
			'name TEXT NOT NULL, size INTEGER, ' + \
			'mtime INTEGER, type TEXT NOT NULL)'
	try:
		cursor.execute(command)
	except sqlite3.Error, msg:
		print 'Error: ', msg
		print "Command: ", command
		
	command = 'CREATE TABLE IF NOT EXISTS Search (' + \
			'tag TEXT NOT NULL, file TEXT NOT NULL,' + \
			'lineNumber INTEGER NOT NULL)' 
	
	try:
		cursor.execute(command)
	except sqlite3.Error, msg:
		print 'Error: ', msg
		print "Command: ", command
	
	# create xapian databse
	# need to resolve dbpath somehow
	dbpath = os.path.join(os.path.dirname(dbpath), 'xapiandb')
	try:
		xdb = xapian.WritableDatabase(dbpath, xapian.DB_CREATE_OR_OPEN)	
	except xapian.Error, msg:
		print 'Error opening xapian database'
		print msg
		sys.exit(1)	
	indexer = xapian.TermGenerator()

	walk(os.path.join(srcpath), '.', cursor, xdb, indexer)


def walk(top, path, cursor, xdb, indexer):
	''' recursive folder walk'''
	
	dirpath = os.path.join(top, path)
	
	if path != '.':
		command = 'INSERT INTO Files (name, size, mtime, type) ' + \
				'values (\'%s\', NULL, NULL, \'dir\') ' % ("/" + path)
		try:
			cursor.execute(command)
		except sqlite3.Error, msg:
			print 'Error: ', msg
			print "Command: ", command
	
	for f in  os.listdir(dirpath):
		abspath = os.path.join(dirpath, f)
		fstat  = os.stat(abspath)
		mode = fstat[ST_MODE]
		if path != '.':
			relpath = os.path.join(path, f)
		else:
			relpath = f
		if S_ISDIR(mode):
			walk(top, relpath, cursor, xdb, indexer)
		elif S_ISREG(mode):
			command = 'INSERT INTO Files (name, size, mtime, type) ' + \
				'values (\'%s\', %i, %i, \'reg\') ' % \
				("/"+relpath, fstat.st_size, fstat.st_mtime)
			try:
				cursor.execute(command)
			except sqlite3.Error, msg:
				print 'Error: ', msg
				print "Command: ", command
			
			
			indexXapian.indexFile(top, relpath, xdb, indexer)
			#indexSearch.indexFile(top, relpath, cursor)
				
			

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
		
	# parsing ini file
	for s in parser.sections():
		for o in parser.items(s):
			if o[0] == 'src-dir':
				srcpath = o[1]
			if o[0] == 'db-file':
				dbpath = o[1]
		
		# I think it should be done like this :-?
		# [Edit Cotizo]: Yep, that's the way
		# Maybe jailing it to a chroot-ed directory, but I think it's too much.
		try:
			command = 'ctags --fields=nK -R -f %s' % \
				os.path.abspath(os.path.join( \
			 	os.path.dirname(__file__), 'tags'))
			prog = subprocess.Popen(command.split(), cwd = srcpath)
			prog.wait()
		except (KeyboardInterrupt, SystemExit):
			prog.terminate()

		# open tag file
		try:
			tagFile = CTags(os.path.abspath(os.path.join( \
					 os.path.dirname(__file__),  'tags')))
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
		fileDB(cursor, srcpath, dbpath)
	
		db.commit()
		cursor.close()
	
		#remove tags file
		os.remove(os.path.abspath(os.path.join( \
			 os.path.dirname(__file__),  'tags')))
	
	
if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'c:')
	except getopt.GetoptError, msg:
		print msg
		usage()
		sys.exit()
	for o, a in opts:
		if o == '-c':
			if len(args) != 0:
				print 'Too many arguments'
				usage()
				sys.exit(1)
			sys.exit(main(a))
	if len(sys.argv) == 1:
		sys.exit(main('../pylxr.ini'))
	print usage()

