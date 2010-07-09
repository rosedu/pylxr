import sqlite3
import sys
import getopt
import myrandom
import TableRow
# from print_r import print_r

class Usage(Exception):
    def __init__(self, msg=None):
        if msg == None:
            self.msg ="""Usage:\t\t\tpython pydb.py [-r|-q]
-q DATABASE QUERY\texecutes a query on DATABASE
-r DATABASE TAB NR\tinserts NR random entries in table TAB from DATABASE

Note that the two options are mutually exclusive.
"""
        else:
            self.msg = msg

def fQuery(db,query):
    print '[DEBUG] Query:', db, query
    sql = sqlite3.connect(db)
    cmd = sql.cursor()
    cmd.execute(query)
    sql.commit()
    for row in cmd:
        print row
    sql.close()

    
def fRandom(db,table,nr):
    print '[DEBUG] Random Insert:', db, table, nr
    sql = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cmd = sql.cursor()
    cmd.execute("select * from %s" % table)
    length = len(cmd.description)
    execString = "insert into %s values (?%s)" % (table,",?"*(length-1))

    myrow = TableRow.TableRow(sql, table)
    manyRows = [myrow.random() for i in xrange(int(nr))]
    print "Inserting:\n", manyRows
    cmd.executemany(execString, manyRows)
        
    sql.commit()
    sql.close()

def main(argv = None):
    if argv == None:
        argv = sys.argv[1:]
    try:
        try: 
            options, args = getopt.getopt(argv, 'qr')
        except getopt.error, msg:
            print msg, "\n"
            raise Usage()
        
        for (o,v) in options:
            if o=='-q':
                query = " ".join(args[1:])
                fQuery(args[0],query)
            elif o=='-r':
                if len(args) < 2:
                    raise Exception('Not enough arguments for -r command (needed 3)')
                fRandom(args[0], args[1], args[2])
    except Exception as err:
        print err
        return 1
    return 0
    

if __name__=='__main__':
    sys.exit(main())
