#!/urs/bin/env python

from Tkinter import *
import re


class MyFrame:
	def __init__(self, root):
		self.frame = Frame(root)
		self.frame.pack()			
		Label(self.frame, text = "File").pack()
		self.file = Entry(self.frame)
		self.file.bind('<Return>', self.textHandler)
		self.file.pack()

		Label(self.frame, text = "Expr").pack()
		self.expr = Entry(self.frame)
		self.expr.bind('<Return>', self.textHandler)
		self.expr.pack()
		
		self.scroll = Scrollbar(self.frame)
		self.scroll.pack(side=RIGHT, fill=Y)
		
		self.list = Listbox(self.frame, yscrollcommand=self.scroll.set)
		self.list.pack(side=LEFT, fill=BOTH)
		
		self.scroll.config(command=self.list.yview)
		
	def textHandler(self, *unusedEvent):
		# test both textfiledls have values
		if self.expr.get() == '' or self.file.get() == '':
			return
			
		try:
			f = open(self.file.get())
			text = f.read()
			f.close()
		except:
			print 'File error'
			return
			
		try:
			prog = re.compile(self.expr.get())
			result = set(prog.findall(text))
		except:
			print 'Regular expresion error'
		else:
			self.list.delete(0, END)
			for s in result:
				self.list.insert(END, s)
			

if __name__ == '__main__':
	root = Tk()
	fr = MyFrame(root)
	root.mainloop()
