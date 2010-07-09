import myrandom
import sys
import re
from Tkinter import *

def makeFile(name, length=None):
    f = open(name, 'w')
    if length==None:
        f.write(myrandom.Text(length))
    else:
        f.write(myrandom.Text(length))

class App:
    def __init__(self):
        self.root = Tk()
        
        self.frame = Frame(self.root)
        self.frame.pack()
        
        self.text_re = Entry(self.frame)
        self.text_re.pack()
        
        self.text_file = Entry(self.frame)
        self.text_file.pack()
        
        self.button = Button(self.frame, text="Run!", command=self.run)
        self.button.pack()
        
        self.listbox = Listbox(self.frame)
        self.listbox.pack()
        
        self.root.mainloop()

    def run(self):
        pattern = self.text_re.get()
        filename = self.text_file.get()
        self.listbox.delete(0, self.listbox.size())

        f = open(filename, "r")
        content = f.read()

        d = {}
        for match in re.findall(pattern, content):
            self.listbox.insert(END, match)
            d[match] = re.finditer(match, content).begin()
        
        
def main():
    myapp = App()

if __name__=='__main__':
    sys.exit(main())
