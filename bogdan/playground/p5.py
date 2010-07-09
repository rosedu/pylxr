import sys
import re

# could be more
reserved = ['continue', 'default', 'while', 'struct', 'switch', 'typedef', \
		'union', 'if', 'sizeof', 'return', 'break', 'case', 'asm', \
		'do', 'else', 'enum', 'for', 'fortran', 'goto']
types = ['auto', 'char', 'const', 'double', 'extern', 'float', 'int', \
		'long', 'register', 'short', 'signed', 'static', \
		'unsigned', 'void', 'volatile']
#prep =  ['define', 'else', 'endif', 'if', 'ifdef', 'ifndef', \
#		'include', 'undef']
special_chars = ['\n', '\t', '{', '}', '(', ')', '[', ']', '.', ',', ';', '*', \
		'/', '+', '-', '%', '=', '<', '>', '!', '^', '~']
operators2 = ['==', '!=' , '<=', '>=', '||', '&&', '+=', '-=', '*=', '/=', '++', \
		'--', '<<', '>>', '->', '|=', '&=', '^=']

class Data:
	def __init__(self):
		self.extern_var = []
		self.func = []
		self.local_var = {}
		self.comment = []
	
	def add_extern(self, var):
		if var not in self.extern_var: # ?? don't think I need this
			self.extern_var.append(var)
	def add_func(self, fun):
		if fun not in self.func:
			self.func.append(fun)
			self.local_var.update({fun:[]})
			
	def add_local(self, fun, var):
		self.local_var[fun].append(var)

	def add_comment(self, comment):
		print 'dsa'

out = None
data = None

def tokenize(text):
	global special_chars

	crt = 0
	toks = []
	l = len(text)
	while l != crt:
		tok = ''
		
		# string
		if text[crt] == '\"':
			tok += '\"'
			crt += 1
			while not (text[crt] == '\"' and text[crt-1] != '\\'):
				tok += text[crt]
				crt += 1
			crt += 1
			tok += '\"'
			toks.append(tok)
			continue
			
		# one line comment
		if text[crt] == '/' and text[crt+1] == '/':
			while text[crt] != '\n':
				tok += text[crt]
				crt += 1
			toks.append(tok)
			continue
		
		# multi line comment
		if text[crt] == '/' and text[crt+1] == '*':
			while not (text[crt] == '/' and text[crt-1] == '*'):
				tok += text[crt]
				crt += 1
			crt += 1
			tok += '/'
			toks.append(tok)
			continue
		
		# 2 char operators
		if text[crt:crt+2] in operators2:
			toks.append(text[crt:crt+2])
			crt += 2
			continue
			
		# single chars 
		if text[crt] in special_chars:
			toks.append(text[crt]) 
			crt += 1
			continue
		
		# white spaces
		if text[crt] == ' ':
			toks.append(' ')
			while text[crt] == ' ':
				crt += 1
			continue
		
		# preporcesor
		if text[crt] == '#':
			crt += 1
			tok += '#'
			while text[crt] in [' ', '\t']:
				crt += 1
			while text[crt] not in [' ', '\t', '<', '\"']:
				tok += text[crt]
				crt += 1
			toks.append(tok)
			if tok == '#include':
				tok = ''
				while text[crt] in [' ', '\t']:
					crt += 1
				if text[crt] == '<':
					while text[crt] != '>':
						tok += text[crt]
						crt += 1
					crt += 1
					tok += '>'
					toks.append(tok)
				# no need to check here for #include "someting.h"	
			continue

		# others
		while text[crt] not in special_chars and text[crt] not in [' ', '\t']:
			tok += text[crt]
			crt += 1
		toks.append(tok)
	return toks		
	
def color(toks, fname):
	out.write('<html>\n')
	out.write('<title> %s </title>\n' % fname)
	out.write('<body>\n')
	it = iter(toks)
	level = 0
	crt = 0
	l = len(toks)
	while l != crt:
		# each line
		if level != 0:
			for i in range(level):
				out.write('&nbsp;')
		if toks[crt] == ' ':
			crt += 1
		# prepoc
		if toks[crt][0] == '#':
			out.write('<span style=\"color:blue\">')
			out.write(toks[crt])
			if toks[crt] == '#include':
				out.write('<span style=\"color:#FA58AC\">')
				if toks[crt+1][0] == '\"':
					out.write(' '+toks[crt+1])
				else:
					out.write(' &lt;'+toks[crt+1][1:])
				out.write('</span>')
				crt += 2
			else:
				crt += 1
			while toks[crt] != '\n':
				if toks[crt][0:2] == '/*':
					elem = toks[crt]
					out.write('<span style=\"color:green\">')
					for char in elem:
						if char == '\n':
							out.write('<br />')
						elif char == '\t':
							for i in range(8):
								out.write('&nbsp;');
						else:
							out.write(char)
					out.write('</span>')
				elif  toks[crt][0:2] == '//':
					out.write('<span style=\"color:green\">')
					out.write(toks[crt])
					out.write('</span>')
				else:
					out.write(toks[crt])
				crt += 1
			out.write('</span><br />\n')
			crt += 1
			continue
			
		# nothing special
		while toks[crt] != '\n':
			if toks[crt][0:2] == '/*':
				elem = toks[crt]
				out.write('<span style=\"color:green\">')
				for char in elem:
					if char == '\n':
						out.write('<br />')
					elif char == '\t':
							for i in range(8):
								out.write('&nbsp;');
					else:
						out.write(char)
				out.write('</span>')
			elif toks[crt][0:2] == '//':
				out.write('<span style=\"color:green\">')
				out.write(toks[crt])
				out.write('</span>')
			elif toks[crt] in reserved:
				out.write('<span style=\"color:red\">')
				out.write(toks[crt])
				out.write('</span>')
			elif toks[crt] in types:
				out.write('<span style=\"color:blue\">')
				out.write(toks[crt])
				out.write('</span>')
			elif toks[crt][0] == '\"' or toks[crt][0] == '\'' \
					or toks[crt].isdigit() or toks[crt][0:2] == '0x':
				out.write('<span style=\"color:#FA58AC\">')
				out.write(toks[crt])
				out.write('</span>')
			elif toks[crt] == '\t':
				for i in range(8):
					out.write('&nbsp;')
			else:
				out.write(toks[crt])
			crt += 1
			
		out.write('</span><br />\n')
		crt += 1
	out.write('</body>\n</html>\n')
	out.close()
		
	
def main():
	global out
	global tokens

	if len(sys.argv) != 2:
		print "Usage: python p5.py <C_source_file>"
		sys.exit(1)
	lines = []
	# try read file
	try:
		f = open(sys.argv[1])
		text = f.read();
		f.close()
		out = open(sys.argv[1]+'.html', 'w')
	except :
		print "File error"
		sys.exit(1)
	tokens = tokenize(text)
	print 'The tokens are, good luck!'
	print tokens
	color(tokens, sys.argv[1])

if __name__ == '__main__':
	main()

