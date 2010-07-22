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

# will add more
langmap = { 'c|c++':['.c++','.cc','.cp','.cpp','.cxx','.c','.h', \
					'.h++','.hh','.hp','.hpp','.hxx','.C','.H'], \
			'python':['.py','.pyx','.pxd','.pxi'], \
			'asm':['.asm','.ASM','.s','.S'], \
			'c#':['.cs'], \
			'java':['.java'], \
			'javascript':['.js'], \
			'html':['.htm','.html'], \
			'basic':['.bas','.bi','.bb','.pb'], \
			'php':['.php','.php3','.phtm'], \
			'perl':['.pl','.pm','.plx','.perl'], \
			'sh':['.sh','.SH','.bsh','.bash','.ksh','.zsh'], \
			'pascal':['.p','.pas']
		}
		
def printLang():
	''' print language map '''

	global langmap
	keys = langmap.keys()
	keys.sort()
	for k in keys:
		print k + ':', reduce(lambda x,y: x + ' ' + y, langmap[k])


def usage():
	''' print usage'''

	print 'Usage:'
	print '\trun:\tpython %s [-c <conf.ini>]' % __file__
	print 'or'
	print '\tlist languages:\tpython %s -l' % __file__


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
		
	# generate extmap from langmap
	global langmap
	global extmap
	extmap = dict([(v,k) for k in langmap for v in langmap[k]])
		
	srcpath = 'src'
	dbapth = 'newdb'
	xpath = 'xdb'
	lang = '*'
	
	# parsing ini file
	for s in parser.sections():
		if s=='root':
			continue
		print 'Started indexing project %s' % s
		for o in parser.items(s):
			if o[0] == 'src-dir':
				srcpath = o[1]
			elif o[0] == 'db-file':
				dbpath = o[1]
			elif o[0] == 'xapian-dir':
				xpath = o[1]
			elif o[0] == 'language':
				lang = o[1].lower().split()
				if '*' in lang:
					lang = ['*']
	

		indexAll(srcpath, dbpath, xpath, lang)
		print 'Finished indexing project %s\n' % s
		
	
if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'c:',['lang'])
	except getopt.GetoptError, msg:
		print msg
		usage()
		sys.exit()
	for o, a in opts:
		if o == '--lang':
			printLang()
			sys.exit(0)
		elif o == '-c':
			if len(args) != 0:
				print 'Too many arguments'
				usage()
				sys.exit(1)
			sys.exit(main(a))
	if len(sys.argv) == 1:
		sys.exit(main('../pylxr.ini'))
	print usage()
	sys.exit(1)

