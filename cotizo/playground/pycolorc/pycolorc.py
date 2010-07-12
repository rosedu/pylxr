import sys
import ConfigParser
import CLexer

def main(argv=None):
    console = False
    if argv==None:
        argv=sys.argv[1:]
        console = True

    filename = argv[0]
    formatted = CLexer.CLexer(filename)

    if console:
        print formatted
        return 0
    else:
        return formatted

    

if __name__=='__main__':
    sys.exit(main())
