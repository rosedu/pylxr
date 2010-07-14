#!/usr/bin/python

import os
import sys
import re
from stat import *

def trick(path):
    content = os.listdir(path)
    for item in content:
        fullpath = os.path.join(path, item)
        stat = os.stat(fullpath)
        mode = stat[ST_MODE]
        if S_ISDIR(mode):
            trick(fullpath)
        elif S_ISREG(mode):
            if re.search("~$", item) is not None:
                print fullpath
                os.remove(fullpath)

def main(argv=None):
    if argv == None:
        argv = sys.argv[1:]
    if len(argv) < 1:
        argv = ['.']

    print "Beginning temporary file killing >:)"
    trick(argv[0])
    

if __name__ == '__main__':
    sys.exit(main())
