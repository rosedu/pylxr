#!/usr/bin/env python

import ctags 
from ctags import CTags, TagEntry
import sys

try:
	tagFile = CTags('tags')
except:
	print 'Error on open tags'
	sys.exit(1)
	
entry = TagEntry()

if len(sys.argv) == 2:
	if tagFile.find(entry, sys.argv[1], ctags.TAG_FULLMATCH):
		print entry['file'], entry['lineNumber']
	else:
		print 'Symbol', sys.argv[1], 'not found'
else:
	stat = tagFile.first(entry)
	while stat:
		print entry['name'], entry['file'], entry['lineNumber'], entry['kind']
		stat = tagFile.next(entry)


