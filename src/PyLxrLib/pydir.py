import os
import sys
from datetime import datetime
from stat import *
import sqlite3

# TODO : recursive calls ? :)
class filesystem():
    def listDir(self, path, maxd=1):
        """List directory contents, recursively.
        path = path to directory to list
        maxd = if 0, method returns; decreased at each recursive call"""
        
        if maxd == 0:
            return None
        
        try:
            content = os.listdir(path)
        except Exception as err:
            return None
        
        ret = []
        for item in content:
            fullpath = os.path.join(path, item)
            to_add = ()
            try:
                stat = os.stat(fullpath)
                mode = stat[ST_MODE]
                if S_ISDIR(mode):
                    to_add = (item, 'dir',[])
                elif S_ISREG(mode):
                    to_add = (item, 'reg', {
                            'size': stat[ST_SIZE],
                            'date': datetime.fromtimestamp(stat[ST_MTIME])
                            })
                else:
                    to_add = (item, None, None)
            except:
                continue
            ret.append(to_add)
            return ret

class database():
    def __init__(self, dbname, table):
        raise Exception(dbname)
        self.sql = sqlite3.connect(dbname)
        self.cmd = self.sql.cursor()
        self.query = "SELECT * FROM %s WHERE path=" % table

    def __del__(self):
        self.sql.close()
        
    def listDir(self, path, maxd=1):
        """List directories based on a database"""
        self.cmd.execute(self.query+'"'+path+'"')
        for row in self.cmd:
            print row
        
        
