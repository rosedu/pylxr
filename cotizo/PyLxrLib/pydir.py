import os
import sys
from datetime import datetime
from stat import *

# TODO : recursive calls ? :)
def listDir(path, maxd = 1):
    """List directory contents, recursively.
    path = path to directory to list
    maxd = if 0, method returns; decreased at each recursive call"""

    if maxd == 0:
        return None

    try:
        content = os.listdir(path)
    except Exception as err:
        return None

    ret = []
    for item in content:
        fullpath = os.path.join(path, item)
        to_add = ()
        try:
            stat = os.stat(fullpath)
            mode = stat[ST_MODE]
            if S_ISDIR(mode):
                to_add = (item, 'dir',[])
            elif S_ISREG(mode):
                to_add = (item, 'reg', {
                        'size': stat[ST_SIZE],
                        'date': datetime.fromtimestamp(stat[ST_MTIME])
                        })
            else:
                to_add = (item, None, None)
        except:
            continue
        ret.append(to_add)
    return ret
