
class CommentParser:
	''' CommentParser for C/C++ language '''
	def __init__(self):
		self.state = 0

	def ignoreComment(self, line):
		''' ignore words in strings and comments'''

		ret = ''
		l = len(line)
		crt = 0
		while l != crt:
			# plain text
			if self.state == 0:
				if line[crt] == '\"':
					if crt+1 != l and line[crt+1] == '\"':
						crt += 2
						ret += ' '
					else:
						self.state = 1
						crt += 1
						ret += ' '
				elif line[crt] == '/' and crt+1 != l and line[crt+1] == '/':
					ret += '\n'
					return ret
				elif line[crt] == '/' and crt+1 != l and line[crt+1] == '*':
					crt += 2
					self.state = 2
					ret += ' '
				else:
					ret += line[crt]
					crt += 1
			# in string
			elif self.state == 1:
				if line[crt] != '\\' and crt+1 != l and line[crt+1] == '\"':
					crt += 2
					self.state = 0
				else:
					crt += 1
			# in multiline comment
			elif self.state == 2:
				if line[crt] == '*' and crt+1 != l and line[crt+1] == '/':
					crt += 2
					self.state = 0
				else:
					crt += 1
		return ret
