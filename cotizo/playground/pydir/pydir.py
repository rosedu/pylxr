"""List directories"""

import os
import sys
from datetime import datetime
from string import ljust
from stat import *

def mywalk(path, depth, maxd):
    if depth==maxd:
        return 0
    
    try:
        content = os.listdir(path)
    except Exception as err:
        print err
        return 0

    s = 0
        
    for item in content:
        fullpath = os.path.join(path, item)
        print ljust(fullpath, 50),
        try:
            mode = os.stat(fullpath)[ST_MODE]
            if S_ISDIR(mode):
                print "Directory"
                m = mywalk(fullpath, depth+1, maxd)
                print "Directory size: ", m
                s = s+m
            elif S_ISREG(mode):
                print "Regular file\t%s\t%s" % (os.stat(fullpath)[ST_SIZE], datetime.fromtimestamp(os.stat(fullpath)[ST_MTIME]))
                s = s+int(os.stat(fullpath)[ST_SIZE])
            elif S_ISLNK(mode):
                print "Link"
            elif S_ISSOCK(mode):
                print "Socket"
            elif S_ISFIFO(mode):
                print "Pipe"

        except Exception as err:
            print err

    return s

            

def main(argv=None):
    if argv==None:
        argv = sys.argv[1:]
    maxd = int(argv[1])
    s = mywalk(argv[0], 0, maxd)
    print "Total size: ", s

if __name__=='__main__':
    sys.exit(main())
