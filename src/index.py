""" Main index file. Will handle most of the requests. """

from mod_python import apache, psp
import os
import re
import ConfigParser
import pickle
import subprocess
from datetime import datetime
import urllib

langmap = [
	('CLexer',['c++','cc','cp','cpp','cxx','c','h',
		   'h++','hh','hp','hpp','hxx','C','H']),
	('PyLexer', ['py'])
	]

def do_dir(req, config, proj, path):
	""" Does the stuff needed for a directory (when we have a "?d=..." GET directive). """
	
	import_dir = os.path.join(os.path.dirname(__file__), "dbaccess")
	dbsearch = apache.import_module('dbsearch', path=[import_dir])

	db_filename = config.get(proj, "db-file")
	DB = dbsearch.DBSearch(db_filename)
	content = DB.searchFile(path+"%")

	# Get the parent of the current path and output it
	parent = '/'.join(path.split('/')[:-1])
	if parent == '/':
		parent = '' # don't ask me why ...

	DEBUG = None
	listing = []
	if content is None:
		DEBUG = ['Forbidden? Or unavailable? Or even inexistent... IDK!']
	else:
		content.sort(key = lambda (x,y,z,t): (t,x))
		# Hardcoding insertion of '.' and '..' in listing
		listing = [{'type':'dir', 'link':path, 'display':'.'}, {'type':'dir', 'link':parent, 'display':'..'}]
		for (f, s, d, t) in content:
			father = re.search("^(.*)/*(.*)/",f).group(0)[:-1]
			if path != father:
				continue
			e = f[::-1]
			e = re.search("[a-zA-Z_\-0-9\.]+/", e).group(0)
			e = e[::-1]
			if t == 'dir':
				listing.append( {'type':'dir', 'link':f, 'display':e} )
			elif t=='reg':
				listing.append( {'type':'reg', 'link':f, 'display':e, 'size':s, 'date':datetime.fromtimestamp(d)} )
			else:
				listing.append( {'type':'n/a', 'display':e} )

	req.content_type = 'html'
	tmpl = psp.PSP(req, filename='templates/dirlist.tmpl')
	tmpl.run( vars={
			'proj': proj,
			'DEBUG': DEBUG,
			'listing': listing,
			'dirpath': path
			})
	

def do_file(req, config, proj, path):
	""" Will pass the file to the lexer, and then the structure will be returned to the server page and processed there. """

	extension = path.split('.')[-1:][0]

	lexer = None
	for (l,e) in langmap:
		if extension in e:
			lexer = l
	if lexer is None:
		lexer = 'PlainLexer'

	directory = os.path.join(os.path.dirname(__file__), "lexer/")
	Lexer = apache.import_module(lexer, path=[directory])
	
	fullpath = os.path.join(config.get(proj, 'src-dir'), path[1:])
	lexer = Lexer.Lexer(fullpath, config.get(proj, 'db-file'))
	
	req.content_type = 'html'
	tmpl = psp.PSP(req, filename='templates/source.tmpl')
	tmpl.run( vars = {
			'proj': proj,
			'filename': path,
			'lines':lexer.get()
			})

def parse_config(filename='pylxr.ini'):
	""" Just get the config file and pass it around... """
	
	config = ConfigParser.ConfigParser()
	fullpath = os.path.join(os.path.dirname(__file__), filename)
	config.read(fullpath)
	return config

def search(req):
	try:
		search = req.form['tag']
		proj = req.form['proj']
		
		config = parse_config()
		dbfile = config.get(proj, 'db-file')
		xafile = config.get(proj, 'xapian-dir')
		
		directory = os.path.join(os.path.dirname(__file__), "dbaccess/")
		dbsearch = apache.import_module('dbsearch', path=[directory])
		# xapian = apache.import_module('xapianSearch', path=[directory])
		DBS = dbsearch.DBSearch(dbfile)

		allTags = DBS.searchTag(search, '', allMatches=True)
		if allTags is not None:
			allTags.sort(key = lambda (a,b,c): (c,a,b))
			
		# allMatches = xapian.search(xafile, search)
		params = urllib.urlencode({'config':xafile, 'search':search})
		web_url = config.get('root', 'web-url')
		p = urllib.urlopen("%s/workaround.php?%s" % (web_url,params))
		allMatches = eval(p.read())
		if allMatches is not None:
			allMatches.sort()

		req.content_type = 'html'
		tmpl = psp.PSP(req, filename='templates/search.tmpl')
		tmpl.run( vars = {
				'proj':proj,
				'allTags':allTags,
				'allMatches':allMatches,
				'search':search,
				'web_url':web_url}
			  )
	except Exception, ex:
		return str(ex)
		index(req)

def do_projects(req, config):
	projects = []
	for i in config.get('root','projects').split(','):
		if i == 'root':
			continue
		projects.append( (i, config.get('root','web-url')+'index.py?proj='+i ) )

	req.content_type = 'html'
	tmpl = psp.PSP(req, filename='templates/projects.tmpl')
	tmpl.run( vars = {'projects':projects} )
				 

def newconfig(req):
	config = ConfigParser.ConfigParser()
	for (key, val) in req.form.items():
		if len(key.split('/')) < 2:
			continue
		section = key.split('/')[0]
		option = key.split('/')[1]
		if section not in config.sections():
			config.add_section(section)
		config.set(section, option, val)

	fullpath = os.path.join(os.path.dirname(__file__), 'pylxr.ini')
	filename = open(fullpath, 'wb')
	if filename is not None:
		config.write(filename)
	return admin(req)
	
def admin(req):
	# Let's guess the web-url.


	config = parse_config()
	try:
		web_url = config.get('root', 'web-url')
		if  web_url == '':
			raise Exception('woops')
		
	except Exception, ex:
		web_url = re.match("^(?P<id>.*)/index.py/(.*)$",
				   req.construct_url(req.unparsed_uri)).group('id') + '/'
		
	req.content_type = 'html'
	tmpl = psp.PSP(req, filename='templates/admin.tmpl')
	tmpl.run(vars = {
			'config':config,
			'web_url':web_url
			})
		
def index(req):
	""" Main entrypoint. """
	config = parse_config()
					   
	uri = req.unparsed_uri
	unparsedGET = uri.split('?')
	if len(unparsedGET) < 2:
		return do_projects(req, config)
	
	GET = unparsedGET[1].split('&')
	options = dict(default=None)
	for option in GET:
		a = option.split('=')[0]
		b = option.split('=')[1]
		options[a] = b

	if 'proj' in options:
		proj = options['proj']
	else:
		return do_projects(req, config)

	if 'r' in options:
		return do_file(req, config, proj, options['r'])
	
	if 'd' in options:
		return do_dir(req, config, proj, options['d'])
	return do_dir(req, config, proj, '')
