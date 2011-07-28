from __future__ import division

from functools import partial

import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)

from PyQt4 import QtCore, QtGui

from settings import Settings
from settingsdialog import SettingsDialog
from utils import get_qicon

class MainUi(QtGui.QMainWindow):
    def __init__(self):
        super(QtGui.QMainWindow, self).__init__()
        
        self.setWindowTitle("SimpleShortcuts")
        
        central_widget = QtGui.QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QtGui.QVBoxLayout()
        
        self.shortcut_layout = QtGui.QGridLayout()
        
        bottom_layout = QtGui.QHBoxLayout()
        
        settings_button = QtGui.QPushButton("Settings")
        settings_button.clicked.connect(self.settings_button_clicked)
        
        kill_button = QtGui.QPushButton("Kill Application")
        kill_button.clicked.connect(partial(self.run, "xkill"))
        
        bottom_layout.addWidget(kill_button)
        bottom_layout.addStretch()
        bottom_layout.addWidget(settings_button)

        main_layout.addLayout(self.shortcut_layout)
        main_layout.addLayout(bottom_layout)
        
        central_widget.setLayout(main_layout)

        self.settings = Settings.read()

        self.refresh_shortcuts()

    def refresh_shortcuts(self):
        layout = self.shortcut_layout

        column_width = self.settings["options"]["column_width"]
        column_count = self.settings["options"]["column_count"]
        
        row, column = layout.rowCount(), layout.columnCount()
        
        for x in range(row):
            for y in range(column):
                item = layout.itemAtPosition(x, y)
                if item is not None:
                    item.widget().hide()
                    layout.removeItem(item)
          

        shortcuts = self.settings["shortcuts"]

        rows = self._chunks(shortcuts, column_count)
        
        for x, row in enumerate(rows):
            for y, shortcut in enumerate(row):
                button = QtGui.QPushButton()
                button.setMaximumWidth(column_width)
                button.setMinimumWidth(column_width)
                
                if self.settings["options"]["show_names"]:                
                    button.setText(shortcut["name"])

                button.setIcon(get_qicon(shortcut["icon"]))
                
                size = self.settings["options"]["icon_size"]
                
                button.setIconSize(QtCore.QSize(size, size))
                
                button.clicked.connect(partial(self.run, shortcut["command"]))
                
                layout.addWidget(button, x, y)
        
    def settings_button_clicked(self):
        s = SettingsDialog(self)
        
        ret = s.exec_()
    
        if ret == 1:
            Settings.save(s.settings)

            self.settings = Settings.read()
            
            self.refresh_shortcuts()
            
    def run(self, command):
        print(command)
        command = str(command)
        
        #for reducing startup time
        from shlex import split
        from subprocess import Popen
        from sys import exit
        
        splitted = split(command)
        
        try:
            Popen(splitted)
        except OSError as e:    
            box = QtGui.QMessageBox()
            
            box.setWindowTitle("Error - SimpleShortcuts")
            
            box.setText('Error when trying to run "{0}"'.format(command))
            box.setDetailedText(e.strerror)
            
            box.setStandardButtons(box.Close)
            box.setDefaultButton(box.Close)
            
            box.exec_()
        else:
            exit(0)
            
    def _chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]

if __name__ == "__main__":
    import sys
    
    app = QtGui.QApplication(sys.argv)
    rect = app.desktop().geometry()
    
    g = MainUi()
    g.show()
    
    g.move(rect.center() - g.rect().center())
    
    app.exec_()
