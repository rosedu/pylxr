#!/urs/bin/env python

import sys
import os


l = len(sys.argv)
if l < 2:
	print 'Too few arguments'
	sys.exit(1)
	
command = sys.argv[1]
idx = 2
while idx < l:
	command += ' ' + sys.argv[idx]
	idx += 1

os.system(command)

