#!/urs/bin/env python

import ConfigParser

def main():
	parser = ConfigParser.ConfigParser()
	parser.readfp(open('conf.ini'))
	for s in parser.sections():
		print s
		for o in parser.items(s):
			print '\t', o[0], ' = ', o[1]
			
if __name__ == '__main__':
	main()
