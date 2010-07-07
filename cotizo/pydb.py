# TODO : rewrite Usage class, raise it as needed 

import sqlite3
import sys
import getopt
import random
from print_r import print_r

def usage():
    print """Usage:\t\t\tpython pydb.py [-r|-q]
-q DATABASE QUERY\texecutes a query on DATABASE
-r DATABASE TAB NR\tinserts NR random entries in table TAB from DATABASE

Note that the two options are mutually exclusive.
... also note that your usage is OK, but another stupid error raised at runtime [TODO: FIXME :)]
"""

def fQuery(db,query):
    # could use some error handling here ...
    # note that in case of error, usage() saves the day :( (and fails)
    print 'fq', db, query # remove me
    sql = sqlite3.connect(db)
    cmd = sql.cursor()
    cmd.execute(query)
    sql.commit()
    for row in cmd:
        print row
    sql.close()

# ROADMAP :
# * TableRow calss // get the header from the connection and parse it
# will enable to generate random TYPED(aka with type) values
# push random rows in database
# * clean up the try..except in script
# * implement a main() for simple life
# * respect the main() guidelines recommended by Razvan's third link
    
def fRandom(db,table,nr):
    print 'fr', db, table, nr # remove me
    sql = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cmd = sql.cursor()
    cmd.execute('select * from %s' % table)
    length = len(cmd.description)
    execString = "insert into %s values (?%s)" % (table,",?"*(length-1))

    for i in xrange(nr):
        r = [random.random() for z in xrange(length)]
        cmd.execute(execString, r)
    
    
if __name__=='__main__':
    try:
        options, args = getopt.getopt(sys.argv[1:], 'qr')
        unrecognised = True
        for (o,v) in options:
            if o=='-q':
                query = " ".join(args[1:])
                fQuery(args[0],query)
                unrecognised = False
            elif o=='-r':
                if len(args) < 2:
                    raise Exception('NotEnoughArguments')
                fRandom(args[0], args[1], args[2])
                unrecognised = False
        if unrecognised:
            raise Exception('UnknownOption')
    except Exception as inst:
        print inst
        usage()
        sys.exit(1)
   
