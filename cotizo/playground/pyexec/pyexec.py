import subprocess
import sys

def main(argv=None):
    if argv==None:
        argv = sys.argv[1:]
    try:
        program = subprocess.Popen(argv)
        print "Program has pid %s. Waiting for it to finish..." % program.pid
        program.wait()
        print "Program has exited with return code %s!" % program.returncode
        return 0
    except (KeyboardInterrupt, SystemExit):
        print "Terminating program..."
        program.terminate()
        return 0
        

    

if __name__ == '__main__':
    sys.exit(main())
