from __future__ import unicode_literals
from __future__ import print_function

import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)

from PyQt4.QtCore import QSettings

class Settings(object):
    
    settings = QSettings("simpleshortcuts")
    print("Settings path:",settings.fileName())
    
    @classmethod
    def save(cls, settings_dict):
        settings = cls.settings
        settings.clear()
        
        settings.setValue("settings", settings_dict)
        
        settings.sync()
    
    @classmethod
    def read(cls):
        settings = cls.settings
        settings.sync()
                
        settings_dict = settings.value("settings", {})
        
        return settings_dict 
        
        