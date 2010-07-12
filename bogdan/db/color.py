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
			if crt == l:
				toks.append(tok) 
				break
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
		if crt == l:
			break
		# others
		while text[crt] not in special_chars and text[crt] not in [' ', '\t']:
			tok += text[crt]
			crt += 1
		toks.append(tok)
	return toks		
	
def color(toks, fname):
	string = ''
	string += ('<html>\n')
	string += ('<title> %s </title>\n' % fname)
	string += ('<body>\n')
	it = iter(toks)
	level = 0
	crt = 0
	l = len(toks)
	while l != crt:
		# each line
		if level != 0:
			for i in range(level):
				string += ('&nbsp;')
		if toks[crt] == ' ':
			crt += 1
		# prepoc
		if toks[crt][0] == '#':
			string += ('<span style=\"color:blue\">')
			string += (toks[crt])
			if toks[crt] == '#include':
				string += ('<span style=\"color:#FA58AC\">')
				if toks[crt+1][0] == '\"':
					string += (' '+toks[crt+1])
				else:
					string += (' &lt;'+toks[crt+1][1:])
				string += ('</span>')
				crt += 2
			else:
				crt += 1
			while toks[crt] != '\n':
				if toks[crt][0:2] == '/*':
					elem = toks[crt]
					string += ('<span style=\"color:green\">')
					for char in elem:
						if char == '\n':
							string += ('<br />')
						elif char == '\t':
							for i in range(8):
								string += ('&nbsp;');
						else:
							string += (char)
					string += ('</span>')
				elif  toks[crt][0:2] == '//':
					string += ('<span style=\"color:green\">')
					string += (toks[crt])
					string += ('</span>')
				else:
					string += (toks[crt])
				crt += 1
			string += ('</span><br />\n')
			crt += 1
			continue
			
		# nothing special
		while toks[crt] != '\n':
			if toks[crt][0:2] == '/*':
				elem = toks[crt]
				string += ('<span style=\"color:green\">')
				for char in elem:
					if char == '\n':
						string += ('<br />')
					elif char == '\t':
							for i in range(8):
								string += ('&nbsp;');
					else:
						string += (char)
				string += ('</span>')
			elif toks[crt][0:2] == '//':
				string += ('<span style=\"color:green\">')
				string += (toks[crt])
				string += ('</span>')
			elif toks[crt] in reserved:
				string += ('<span style=\"color:red\">')
				string += (toks[crt])
				string += ('</span>')
			elif toks[crt] in types:
				string += ('<span style=\"color:blue\">')
				string += (toks[crt])
				string += ('</span>')
			elif toks[crt][0] == '\"' or toks[crt][0] == '\'' \
					or toks[crt].isdigit() or toks[crt][0:2] == '0x':
				string += ('<span style=\"color:#FA58AC\">')
				string += (toks[crt])
				string += ('</span>')
			elif toks[crt] == '\t':
				for i in range(8):
					string += ('&nbsp;')
			else:
				string += (toks[crt])
			crt += 1
			
		string += ('</span><br />\n')
		crt += 1
	string += ('</body>\n</html>\n')
	return string
		
	
def main(fname):

	# try read file
	f = open(fname, 'r')
	text = f.read();
	f.close()

	tokens = tokenize(text)
	return color(tokens, fname)
	
if __name__ == '__main__':
	main(fname)

