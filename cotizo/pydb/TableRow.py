import sqlite3
import re
import myrandom

class TableRow:
    def __init__(self, conn, name):
        self.conn = conn
        self.tbName = name

        cmd = self.conn.cursor()
        cmd.execute("SELECT sql FROM sqlite_master WHERE name=\"%s\"" % self.tbName)

        for row in cmd: # only one row, but... 
            self.types = re.findall("INTEGER|TEXT|NULL|REAL|BLOB", row[0])

    def row(self):
        
