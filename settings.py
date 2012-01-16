from __future__ import unicode_literals
from __future__ import print_function

import json
import os

class Settings(object):
    path = os.path.join(os.getenv("XDG_CONFIG_HOME"), "simpleshortcuts.conf")    
    print("Settings path:", path)
    
    @classmethod
    def save(cls, settings_dict):
        with open(cls.path, "w") as f:
            json.dump(settings_dict, f, indent=4)
            
    @classmethod
    def read(cls):
        try:
            f = open(cls.path)
            return json.load(f)
        except (IOError, ValueError):
            with open(cls.path, "w") as f:
                json.dump({}, f)
            return {}