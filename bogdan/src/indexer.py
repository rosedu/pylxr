import sys
import os
import ConfigParser 
from ctags import CTags, TagEntry
import sqlite3
from stat import *
import subprocess


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
	

# create table with files	
def fileDB(cursor, srcpath):

	# may need more columns
	command = 'CREATE TABLE Files (' + \
			'name TEXT NOT NULL, size INTEGER NOT NULL, ' + \
			'mtime INTEGER NOT NULL, type TEXT NOT)'
	try:
		cursor.execute(command)
	except sqlite3.Error, msg:
		print 'Error: ', msg
		print "Command: ", command
	walk(os.path.join(srcpath), '.', cursor)


def walk(top, path, cursor):
	dirpath = os.path.join(top, path)
	for f in  os.listdir(dirpath):
		abspath = os.path.join(dirpath, f)
		fstat  = os.stat(abspath)
		mode = fstat[ST_MODE]
		if path != '.':
			relpath = os.path.join(path, f)
		else:
			relpath = f
		if S_ISDIR(mode):
			walk(top, relpath, cursor)
		elif S_ISREG(mode):
			command = 'INSERT INTO Files (name, size, mtime) ' + \
				'values (\'%s\', %i, %i) ' % \
				(relpath, fstat.st_size, fstat.st_mtime)
			try:
				cursor.execute(command)
			except sqlite3.Error, msg:
				print 'Error: ', msg
				print "Command: ", command
				
			

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
	for s in parser.sections():
		for o in parser.items(s):
			if o[0] == 'src-dir':
				srcpath = o[1]
			if o[0] == 'db-file':
				dbpath = o[1]
		# I think it should be done like this :-?
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
	sys.exit(main('../pylxr.ini'))
