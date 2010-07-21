
class CommentParser:
	''' CommentParser for Python language '''
	
	def __init__(self):
		self.state = 0

	def ignoreComment(self, line):		
		ret = ''
		l = len(line)
		crt = 0
		while l != crt:
			# plain text
			if self.state == 0:
				if line[crt] == '\"':
					ret += ' '
					if l != crt+1 and line[crt+1] == '\"':
						crt += 2
					else:
						self.state = 1
						crt += 1
				elif line[crt] == '\'':
					ret += ' '
					if crt+1 != l and line[crt+1] == '\'':
						crt += 2
						state = 0
					else:
						self.state = 2
						crt += 1
				elif line[crt] == '#':
					return ret
				else:
					ret += line[crt]
					crt += 1
			# in " string
			elif self.state == 1:
				if line[crt] != '\\' and crt+1 != l and line[crt+1] == '\"':
					crt += 2
					self.state = 0
				else:
					crt += 1
			# in ' string
			elif self.state == 2:
				if line[crt] != '\\' and crt+1 != l and line[crt+1] == '\'':
					crt += 2
					self.state = 0
				else:
					crt += 1
		return ret
