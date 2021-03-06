''' main indexer script '''

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


def usage():
	''' print usage'''

	print 'Usage:'
	print '\tpython %s [-c conf.ini] [-p project]' % __file__
	print 'Options:'
	print '\t-c: specify config file (default is ../pylxr.ini)'
	print '\t-p: specify single project to index'


def tagDB(cursor, tagFile, lang):
	''' create table with tags'''
	global extmap

	print '[Step 2/3]Inserting tags into database (this may take a while)'
	entry = TagEntry()

	# create tagls table
	command = 'CREATE TABLE IF NOT EXISTS Tags (' + \
				'name TEXT NOT NULL, file TEXT NOT NULL, ' + \
				'lineNumber INTEGER NOT NULL, kind TEXT NOT NULL, ' + \
				'UNIQUE (name,file,lineNumber,kind) )'
	try : 
		cursor.execute(command)
	except sqlite3.Error, msg:
		print 'Error: ', msg
		print 'Command: ', command
	
	# add tags
	stat = tagFile.first(entry)
	while stat:
		if skip(entry['file'], lang, extmap):
			stat = tagFile.next(entry)	
			continue
		command = 'REPLACE INTO Tags ' + \
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


def fileDB(cursor, srcpath, xpath, lang):
	''' create table with files and search tokens'''
	global langmap
	
	print '[Step 3/3]Indexing files'
	print 'Counting files'
	n = count(srcpath, lang, 0)
	if n == 0:
		print 'No files found, won\'t index any file'
	else:
		print 'Found %i files' % n
	
	# may need more columns
	command = 'CREATE TABLE IF NOT EXISTS Files (' + \
			'name TEXT NOT NULL, size INTEGER, ' + \
			'mtime INTEGER, type TEXT NOT NULL, ' +\
			'UNIQUE (name))'
	try:
		cursor.execute(command)
	except sqlite3.Error, msg:
		print 'Error: ', msg
		print "Command: ", command
	
	# create xapian databse
	try:
		xdb = xapian.WritableDatabase(xpath, xapian.DB_CREATE_OR_OVERWRITE)	
	except xapian.Error, msg:
		print 'Error opening xapian database'
		print msg
		sys.exit(1)

	indexer = xapian.TermGenerator()
	walk(os.path.join(srcpath), '.', cursor, xdb, indexer, lang, 0, n)
	xdb.flush()


def walk(top, path, cursor, xdb, indexer, lang, crtn, totaln):
	''' recursive folder walk'''
	global extmap
	
	dirpath = os.path.join(top, path)

	if path != '.':
		command = 'REPLACE INTO Files (name, size, mtime, type) ' + \
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
			crtn = walk(top, relpath, cursor, xdb, indexer, lang, crtn, totaln)
		elif S_ISREG(mode):
		
		
			command = 'REPLACE INTO Files (name, size, mtime, type) ' + \
				'values (\'%s\', %i, %i, \'reg\')' % \
				("/"+relpath, fstat.st_size, fstat.st_mtime)
			try:
				cursor.execute(command)
			except sqlite3.Error, msg:
				print 'Error: ', msg
				print "Command: ", command

			if totaln != 0:
				if skip(relpath, lang, extmap):
					print '[%i%s]Skipping file %s' % (crtn*100/totaln, '%', relpath)
				else:
					print '[%i%s]Indexing file %s' % (crtn*100/totaln, '%', relpath)
					ext = os.path.splitext(relpath)
					l = extmap[ext[1]]
					indexXapian.indexFile(top, relpath, xdb, indexer, l)
					crtn = crtn + 1
	return crtn


def count(dirpath, lang, n):
	''' count files for indexing'''
	global extmap
	
	for f in os.listdir(dirpath):
		relpath = os.path.join(dirpath, f)
		mode = os.stat(relpath)[ST_MODE]
		if S_ISDIR(mode):
			n = count(relpath, lang, n)
		elif S_ISREG(mode) and skip(relpath, lang, extmap) == False:
			n += 1
	return n


def indexAll(srcpath, dbpath, xpath, lang):
	''' main indexer function'''
	global langmap
	
	print '[Step 1/3]Generating tag file (this may take a while)'
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

	tagDB(cursor, tagFile, lang) 
	fileDB(cursor, srcpath, xpath, lang)

	db.commit()
	cursor.close()

	#remove tags file
	os.remove(os.path.abspath(os.path.join( \
		 os.path.dirname(__file__),  'tags')))


def skip(fname, lang, extmap):
	try:
		ext = os.path.splitext(fname)
		l = extmap[ext[1]]
	except KeyError, msg:
		return True
	if lang[0] == '*':
		return False
	if l in lang:
		return False
	return True
	
def loadLang():
	global langmap
	
	try:
		f = open(os.path.join('lang','langmap'), 'r')
	except IOError, msg:
		print 'Error openning langmap'
		print 'Message:', msg 
		sys.exit(1)
	
	langmap = {}
	for line in f:
		line = line.strip()
		# ignore comment or blank line
		if len(line) == 0 or line[0] == '#':
			continue
		
		toks = line.split()
		langmap[toks[0]] = [ext for ext in toks[1:]]	
	
def main(conf, p):
	
	parser = ConfigParser.ConfigParser()
	try:
		parser.readfp(open(conf))
	except IOError, msg:
		print msg
		return 1
	except ConfigParser.Error, msg:
		print msg
		return 1
		
	# generate extmap from langmap
	global langmap
	global extmap
	loadLang()
	extmap = dict([(v,k) for k in langmap for v in langmap[k]])

	# parsing ini file
	if p == None:
		# all projects
		projects = parser.get('root', 'projects').split(',')
		for proj in projects:
			print 'Started indexing project %s' % proj
			try:
				srcpath = parser.get(proj, 'src-dir')
				dbpath = parser.get(proj, 'db-file')
				xpath = parser.get(proj, 'xapian-dir')
				lang = parser.get(proj, 'language').split()
			except ConfigParser.NoOptionError, msg:
				print msg
				print 'Skipping project %s\n' % proj
				continue
			indexAll(srcpath, dbpath, xpath, lang)
			print 'Finished indexing project %s\n' % proj
	else:
		# single project
		proj = p
		print 'Started indexing project %s' % proj
		try:
			srcpath = parser.get(proj, 'src-dir')
			dbpath = parser.get(proj, 'db-file')
			try:
				os.remove(dbpath)
			except:
				pass
			xpath = parser.get(proj, 'xapian-dir')
			lang = parser.get(proj, 'language').split()
		except ConfigParser.NoOptionError, msg:
			print msg
			return 1
		indexAll(srcpath, dbpath, xpath, lang)
		print 'Finished indexing project %s\n' % proj
	
if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'c:p:')
	except getopt.GetoptError, msg:
		print msg
		usage()
		sys.exit()
	conf = '../pylxr.ini'
	p = None
	for o, a in opts:
		if o == '-c':
			if len(args) != 0:
				print 'Too many arguments'
				usage()
				sys.exit(1)
			conf = a
		if o == '-p':
			if len(args) != 0:
				print 'Too many arguments'
				usage()
				sys.exit(1)
			p = a
	sys.exit(main(conf,p))
	if len(sys.argv) == 1:
		sys.exit(main('../pylxr.ini',None))
	print usage()
	sys.exit(1)

