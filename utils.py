import os.path
from PyQt4.QtGui import QIcon

def get_qicon(name):
    if os.path.isabs(name):
        return QIcon(name)
    
    icon = QIcon.fromTheme(name)
    if not icon.isNull():
        return icon
        
    for i in os.listdir("/usr/share/pixmaps")[::-1]:
        if i.startswith(name):
            path = os.path.join("/usr/share/pixmaps", i)
            return QIcon(path)
    
    return QIcon()
        
            
        