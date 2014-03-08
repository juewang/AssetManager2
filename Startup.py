'''
Created on Dec 15, 2013

@author: juewa_000
'''
# Functions need to be run during startup, including read config file and setting up environment variables.
import collections as _collections
import json as _json
import os as _os


_CONFIG_FILE_PATH = _os.path.join(_os.path.dirname(__file__), 'config.json')

_SETTING_KEY = ('AM_USERNAME', 'AM_PASSWORD', 'AM_DBNAME', 'AM_SERVER_IP', 'AM_BACK_UP_DIR')

'''def writeConfigFile():
    setting = _collections.OrderedDict()
    setting['AM_USERNAME'] = "testuser"
    setting['AM_PASSWORD'] = "test"
    setting['AM_DBNAME'] = "assetdb"
    setting['AM_SERVER_IP'] = "localhost"
    setting['AM_BACK_UP_DIR'] = "C:\\Users\\juewa_000\\Google Drive\\AssetManager\\backup"
    with open(_CONFIG_FILE_PATH, "w") as f:
        _json.dump(setting, f, indent=4)'''

def readConfigFile():
    with open(_CONFIG_FILE_PATH, "r") as f:
        setting = _json.load(f)
        for key, item in setting.iteritems():
            _os.environ[key] = item
            
    # Check if all the environment variables are created successfully.
    for key in _SETTING_KEY[:-1]:
        if key in _os.environ:
            continue
        raise RuntimeError('Failed to create key {0} in environment variables.'.format(key))
        
readConfigFile()
    