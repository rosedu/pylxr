"""Provides TableRow class
"""

import sqlite3
import re
import myrandom

class TableRow:
    def __init__(self, conn, name):
        """Based on the sqlite connection "conn" and table name "name", will parse the table header from
        sqlite_master table and therefore will determine the needed datatypes for each column
        """
        self.conn = conn
        self.tbName = name

        cmd = self.conn.cursor()
        cmd.execute("SELECT sql FROM sqlite_master WHERE name=\"%s\"" % self.tbName)

        for row in cmd: # only one row, but...
            self.types = re.findall("INTEGER|TEXT|(?<!NOT )NULL|REAL|BLOB", row[0])

    def random(self):
        """Provides a tuple of random values with the parsed types, ready to be inserted into a table using:
        cursor.execute("INSERT INTO table VALUES (?,?,?,...)", returned_value)
        """
        row = []
        for type in self.types:
            if type == "INTEGER":
                row.append(myrandom.Integer(0,100))
            elif type == "TEXT":
                row.append(myrandom.Text())
            elif type == "REAL":
                row.append(myranom.Real(0,100))
            elif type == "BLOB":
                row.append(myrandom.Text())
            else:
                row.append(None)
        return tuple(row)
