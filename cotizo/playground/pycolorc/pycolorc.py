import sys
import ConfigParser
import CLexer

def main(argv=None):
    if argv==None:
        argv=sys.argv[1:]

    filename = argv[0]
    formatted = CLexer.CLexer(filename)

    print formatted


    

if __name__=='__main__':
    sys.exit(main())
