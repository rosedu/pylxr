import ctags
import sys

def main():
    try:
        tagFile = ctags.CTags('tags')
    except:
        print 'No file named "tags".'
        sys.exit(1)

    entry = ctags.TagEntry()
    while tagFile.next(entry):
        print "%s: %s(%s) // %s | %s" % (
            entry['name'],
            entry['file'],
            entry['lineNumber'],
            entry['kind'],
            entry['pattern']
            )

def searchTags(tagList):
    try:
        tagFile = ctags.CTags('tags')
    except:
        print 'No file named "tags".'
        sys.exit(1)

    entry = ctags.TagEntry()
    for aTag in tagList:
        print "="*20
        print "Matches for tag %s" % aTag
        if tagFile.find(entry, aTag, ctags.TAG_PARTIALMATCH | ctags.TAG_IGNORECASE):
            print "%s: %s(%s)" % (entry['name'], entry['file'], entry['lineNumber'])
            while tagFile.findNext(entry):
                print "%s: %s(%s)" % (entry['name'], entry['file'], entry['lineNumber'])
        
if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args)>0:
        print "Printing tags that start with each of the supplied patterns..."
        searchTags(args)
    else:
        print "Printing all tags..."
        print "="*20
        main()
	
