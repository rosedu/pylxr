from mod_python import psp, apache
import pickle

def index(req):
    req.content_type = "html"
    tmpl = psp.PSP(req, filename='templates/main.tmpl')
    tmpl.run(vars = {'ln':10, 'code':'test<br/>'})
    

