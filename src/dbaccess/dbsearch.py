import sqlite3


class DBSearch:
	''' Use for database query'''
	
	def __init__(self, dbpath):
		self.db = sqlite3.connect(dbpath)
		self.cursor = self.db.cursor()
	
	def searchTag(self, tag):
		'''
		Use for tag search
		++ (file, lineNumber, kind)
		'''
		
		command = 'SELECT file, lineNumber, kind FROM Tags ' + \
			'WHERE name=\'%s\'' % tag
		self.cursor.execute(command)
		select = self.cursor.fetchall()
		if len(select) == 0:
			return None
		else:
			return (select[0][0].encode(), select[0][1], \
				select[0][2].encode())
			
	def searchFile(self, fname):
		'''
		Use for file search
		++ (size, mtime)
		'''
		
		command = 'SELECT * FROM Files ' + \
			'WHERE name LIKE "%s"' % fname
		self.cursor.execute(command)
		select = self.cursor.fetchall()
		if len(select) == 0:
			return	None
		else:
			return select
	
	def close(self):
		self.cursor.close()
