import xml.parsers.expat

tab = 0

def start(name, attrs):
	global tab
	for i in range(tab):
		print '\t',
	print name + ':',
	for k in attrs:
		print k,  '=', attrs[k], '',
	print ''
	tab += 1
	
def end(name):
	global tab
	tab -= 1

def char_data(data):
	global tab
	# ignore whitespace 
	if data.strip() == '':
		return
	for i in range(tab):
		print '\t',
	print data


def main():
	parser = xml.parsers.expat.ParserCreate()
	
	parser.StartElementHandler = start
	parser.EndElementHandler = end
	parser.CharacterDataHandler = char_data
	
	f = open('conf.xml')
	parser.Parse(f.read(),1)
	f.close()

if __name__ == '__main__':
	main()

