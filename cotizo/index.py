from mod_python import apache
import os
import re

def do_dir(path):
	# BEWARE !
	# insecure / can be injected ... like hell :(
	# it should only permit acessing files INSIDE the
	# index tree, as in "src/". TO BE FIXED !!!!!!!!!!!!!!!!!!!!!!!
	# SOLUTION:
	# well, we have all our files in a db anyway. if we retain a directory structure there... job done ^^
	
	directory = os.path.join(os.path.dirname(__file__), "PyLxrLib")
	pydir = apache.import_module('pydir', path=[directory])
	page = "<html><body>"

	fullpath = os.path.join(os.path.dirname(__file__), path)
	content = pydir.listDir(fullpath)
	# Fancy some sorting? :)
	content.sort(key = lambda (x,y,a): (y,x))
	if content == None:
		page = page + '<p style="color:red"> Forbidden? Or unavailable? Or even inexistent... IDK!</p>'
	else:
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

def do_file(path):
	# TODO: move module from playground to PyLxrLib, make it more esthetically pleasent [spelling :-/]
	# some sort of verification for the lexer? wth, pycolorc should cope with it...
	
	directory = os.path.join(os.path.dirname(__file__), "playground/pycolorc")
	pycolorc = apache.import_module('pycolorc', path=[directory])

	fullpath = os.path.join(os.path.dirname(__file__), path)
	ret = pycolorc.main([fullpath]) # TODO: oh btw, wth ?!? passing VECTOR ?!? fixme, please! :(
	return ret
	

def index(req):
	uri = req.unparsed_uri
	regexp = re.compile("(d=(?P<dir>.+))|(f=(?P<file>.+))")
	options = regexp.search(uri)
	if options == None:
		return do_dir("src/")
	if options.group('dir') is not None:
		return do_dir(options.group('dir'))
	return do_file(options.group('file'))
