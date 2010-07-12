""" Configuration Parser """

import ConfigParser
import sys

def read_demo():
    print "Config file reading demo..."
    config = ConfigParser.ConfigParser()
    config.read('test.ini')

    for section in config.sections():
        print "In section %s:" % section
        for option in config.options(section):
            print "Option %s has value %s." % (option, config.get(section,option))
    
def write_demo():
    print "Config file writing demo..."
    c = ConfigParser.ConfigParser()
    c.add_section('main')
    c.set('main', 'name', 'pyconfig')
    c.set('main', 'version', '0.0')
    c.set('main', 'modules', '2')
    c.add_section('module0')
    c.set('module0', 'name', 'ConfigParser')
    c.add_section('module1')
    c.set('module1', 'name', 'sys')
    with open('test.ini', 'wb') as filename:
        c.write(filename)

def main(argv=None):
    if argv==None:
        argv = sys.argv[1:]
    if argv[0]=='r':
        read_demo()
    elif argv[0]=='w':
        write_demo()
    else:
        print "Unkown option. Use w/r."
        return 1

    return 0

if __name__=='__main__':
    sys.exit(main())
