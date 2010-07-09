#!/usr/bin/env python

import os
from stat import *
import sys

def visit(path, level, maxl):
	if maxl == level:
		return;
	for f in os.listdir(path):
		fullname = os.path.join(path, f)
		fstat  = os.stat(fullname)
		mode = fstat[ST_MODE]
		for i in range(level):
			print '\t',
		print f,':',
		if S_ISDIR(mode):
			print 'dir', fstat.st_size, fstat.st_mtime
			visit(fullname, level+1, maxl)
		else:
			if S_ISREG(mode):
				print 'file',
			if S_ISFIFO(mode):
				print 'fifo',
			if S_ISLNK(mode):
				print 'link',
			if S_ISSOCK(mode):
				print 'sock',
			print fstat.st_size, fstat.st_mtime		
		
			
if len(sys.argv) != 3:
	print 'Usage: python p1.py <folder_name> <depth>'
	sys.exit(1)

visit(sys.argv[1], 0, int(sys.argv[2]))
