from mod_python import apache
import os

def index(req):
	directory = os.path.dirname(__file__) + "/playground/pycolorc/"
	pycolorc = apache.import_module('pycolorc', path=[directory])
	return pycolorc.main(["%s/index/ping.c" % os.path.dirname(__file__)])
	
