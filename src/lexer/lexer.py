import pygments
import pygments.lexers
import pygments.token as tokens

class Lexer():
    def __init__(self, filename, dbpath):
        self.__content = open(filename, 'r').read()
        self.__lexer = pygments.lexers.get_lexer_for_filename(filename)

    def escape(self, text):
        escape = [("&","&amp;"), ("<","&lt;"), (">","&gt;"),(" ","&nbsp;"),\
                      ("\"","&quot;"), ("\t","&nbsp;"*8)]
        for (l,t) in escape:
            text = text.replace(l,t)
        return text

    def get(self):
        line = None
        result = []
        for (typ,val) in self.__lexer.get_tokens(self.__content):
            if val=='\n':
                if line is None:
                    line = None
                result.append(line)
                line = None
                continue
            vals = val.split('\n')
            i = 0
            for oneval in vals:
                oneval = self.escape(oneval)
                if line is None:
                    line = []
                if typ in tokens.Text:
                    line.append(('print',oneval))
                elif typ in tokens.Comment.Preproc:
                    line.append(('preprocessor', oneval))
                elif typ in tokens.Keyword:
                    line.append(('keyword',oneval))
                elif typ in tokens.Name:
                    line.append(('identifier', oneval))
                elif typ in tokens.Comment:
                    line.append(('comment', oneval))
                elif typ in tokens.String:
                    line.append(('string', oneval))
                else:
                    line.append(('print', oneval))

                i = i+1
                if i != len(vals) and len(vals)>1:
                    result.append(line)
                    line = None
        if line is not None:
            result.append(line)
        return result
