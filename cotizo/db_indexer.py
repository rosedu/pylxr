import os
import sys
import sqlite3
from stat import *
from datetime import datetime

def walk(path, cmd, depth=-1):
    """Recursively inserts into DB. Call without parameters to walk the entire subdirectory tree."""

    if depth == 0:
        return

    try:
        content = os.listdir(path)
    except Exception as err:
        print err
        return

    query = "INSERT INTO tree (path, type, size, date) VALUES ('%s','%s','%s','%s')"

    for item in content:
        fullpath = os.path.join(path, item)

        # maybe try/except ?
        stat = os.stat(fullpath)
        mode = stat[ST_MODE]
        if S_ISDIR(mode):
            walk(fullpath, depth-1)
            cmd.execute(query % (fullpath,'dir','',''))
        elif S_ISREG(mode):
            size = stat[ST_SIZE]
            date = stat[ST_MTIME]
            cmd.execute(query % (fullpath,'reg',size,date))
                        

def main(argv=None):
    if argv==None:
        argv = sys.argv[1:]

    # TODO: test for table existance.
    sql = sqlite3.connect("pylxr.db")
    cmd = sql.cursor()

    walk(argv[0], cmd)
    
    sql.commit()
    sql.close()
    return 0
        
    

if __name__=='__main__':
    sys.exit(main())
