from mod_python import apache
import os
import re
import ConfigParser

def do_dir(config, path):
	import_dir = os.path.dirname(__file__)
	dbsearch = apache.import_module('dbsearch', path=[import_dir])
	page = "<html><body>"

	db_filename = config.get("pylxr", "db-file")
	DB = dbsearch.DBSearch(db_filename)
	content = DB.searchFile(path)
	return content

	if content == None:
		page = page + '<p style="color:red"> Forbidden? Or unavailable? Or even inexistent... IDK!</p>'
	else:
		content.sort(key = lambda (x,y,a): (y,x))
		page = page + "<table>"
		for (e, t, d) in content:
			page = page + "<tr>"
			f = os.path.join(path, e)
			if t == 'dir':
				page = page + "<td><a href='?d=%s'>%s/</a></td><td></td><td></td>" % (f,e)
			elif t=='reg':
				page = page + "<td><a href='?f=%s'>%s</a></td><td>%s</td><td>%s</td>" % (f,e, d['size'], d['date'])
			else:
				page = page + "<td>%s</td><td></td><td></td>" % e
			page = page + "</tr>"
		page = page + "</table>"
	
	page = page + "</body></html>"
	return page

def do_file(config, path):
	directory = os.path.join(os.path.dirname(__file__), "playground/pycolorc")
	pycolorc = apache.import_module('pycolorc', path=[directory])

	fullpath = os.path.join(os.path.dirname(__file__), path)
	ret = pycolorc.main([fullpath]) # TODO: oh btw, wth ?!? passing VECTOR ?!? fixme, please! :(
	return ret

def parse_config(filename='pylxr.ini'):
	config = ConfigParser.ConfigParser()
	fullpath = os.path.join(os.path.dirname(__file__), filename)
	config.read(fullpath)
	return config

def index(req):
	config = parse_config()
					   
	uri = req.unparsed_uri
	regexp = re.compile("(d=(?P<dir>.+))|(f=(?P<file>.+))")
	options = regexp.search(uri)
	if options == None:
		return do_dir(config, "src/")
	if options.group('dir') is not None:
		return do_dir(options.group(config, 'dir'))
	return do_file(options.group(config, 'file'))
