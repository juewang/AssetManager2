'''
Created on Mar 2, 2014

@author: juewa_000
'''
import json as _json
import os as _os
import sys as _sys
import traceback as _traceback

_ERROR_FILE = _os.path.join(_os.getenv("AM_BACK_UP_DIR"), "errorLog.txt")
def writeToJson(outputFilePath, func, *args, **kwargs):
    if not outputFilePath or not func:
        return
    try:
        result = func(*args, **kwargs)
    except Exception:
        with open(_ERROR_FILE, "w+") as f:
            functionCall = func.__name__ + '(' + ','.join(args) + ',' + ','.join([key+'='+value for key, value in kwargs.iteritems()]) + ')'
            f.write('\n'.join((functionCall, repr(_sys.exc_info()[0]), repr(_sys.exc_info()[1]), _traceback.format_exc(_sys.exc_info()[2]))))
    else:
        print outputFilePath
        with open(outputFilePath, "w+") as f:
            _json.dump(result, f)
            
        

