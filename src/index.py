""" Main index file. Will handle most of the requests. """

from mod_python import apache, psp
import os
import re
import ConfigParser
import pickle
from datetime import datetime

def do_dir(req, config, path):
	""" Does the stuff needed for a directory (when we have a "?d=..." GET directive). """
	
	import_dir = os.path.join(os.path.dirname(__file__), "dbaccess")
	dbsearch = apache.import_module('dbsearch', path=[import_dir])

	db_filename = config.get("pylxr", "db-file")
	DB = dbsearch.DBSearch(db_filename)
	content = DB.searchFile(path+"%")

	DEBUG = None
	listing = []
	if content is None:
		DEBUG = ['Forbidden? Or unavailable? Or even inexistent... IDK!']
	else:
		content.sort(key = lambda (x,y,z,t): (t,x))
		listing = []
		for (f, s, d, t) in content:
			father = re.search("^(.*)/",f).group(0)[:-1]
			if path != father:
				continue
			e = re.search("[\w.\s]*\w$", f).group(0) # somehow, it works ?!?
			if t == 'dir':
				listing.append( {'type':'dir', 'link':f, 'display':e} )
			elif t=='reg':
				listing.append( {'type':'reg', 'link':f, 'display':e, 'size':s, 'date':datetime.fromtimestamp(d)} )
			else:
				listing.append( {'type':'n/a', 'display':e} )

	req.content_type = 'html'
	tmpl = psp.PSP(req, filename='templates/dirlist.tmpl')
	tmpl.run( vars={
			'DEBUG': DEBUG,
			'listing': listing,
			'dirpath': path
			})
	

def do_file(req, config, path):
	""" Will pass the file to the lexer, and then the structure will be returned to the server page and processed there. """
	
	directory = os.path.join(os.path.dirname(__file__), "lexer/")
	CLexer = apache.import_module('CLexer', path=[directory])

	fullpath = os.path.join(config.get('pylxr', 'src-dir'), path[1:])
	lexer = CLexer.CLexer(fullpath, config.get('pylxr', 'db-file'))

	req.content_type = 'html'
	tmpl = psp.PSP(req, filename='templates/source.tmpl')
	tmpl.run( vars = {
			'filename': path,
			'lines':lexer.get()
			})

def parse_config(filename='pylxr.ini'):
	""" Just get the config file and pass it around... """
	
	config = ConfigParser.ConfigParser()
	fullpath = os.path.join(os.path.dirname(__file__), filename)
	config.read(fullpath)
	return config

def index(req):
	""" Main entrypoint. """
	
	config = parse_config()
					   
	uri = req.unparsed_uri
	regexp = re.compile("(d=(?P<dir>.+))|(r=(?P<file>.+))")
	options = regexp.search(uri)
	if options is None:
		return do_dir(req, config, "")
	if options.group('dir') is not None:
		return do_dir(req, config, options.group('dir'))
	return do_file(req, config, options.group('file'))
