from __future__ import unicode_literals
from __future__ import print_function

import os.path

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)

from PyQt4 import QtCore, QtGui
from PyQt4 import uic

from settings import Settings
from utils import get_qicon

class DropZone(QtGui.QLabel):
    dropped = QtCore.pyqtSignal(str, str, str)
    
    def __init__(self):
        super(QtGui.QLabel, self).__init__()

        self.setAcceptDrops(True)

        self.setWordWrap(True)
        self.setFrameShape(QtGui.QFrame.Box)
        self.setAlignment(QtCore.Qt.AlignCenter)
    
    def dragEnterEvent(self, event):
        mime = event.mimeData().text()
        
        if not mime.endswith(".desktop"):
            event.ignore()
            return
        
        event.setDropAction(QtCore.Qt.CopyAction)
        event.accept()
        
    def dropEvent(self,event):
        path = event.mimeData().text().replace("file://", "")
        print("Dropped:", path)
        
        parser = configparser.ConfigParser()
        parser.read(path)
        
        try:
            name = parser.get("Desktop Entry", "GenericName")
        except configparser.NoOptionError:
            try:
                name = parser.get("Desktop Entry", "Name")
            except configparser.NoOptionError:
                name = ""
        
        try:
            command = parser.get("Desktop Entry", "Exec")
        except configparser.NoOptionError:
            command = ""
        
        try:
            icon = parser.get("Desktop Entry", "Icon")
        except configparser.NoOptionError:
            icon = ""
            
        self.dropped.emit(name, command, icon)
            

class SettingsDialog(QtGui.QDialog):
    def __init__(self, *args):
        super(QtGui.QDialog, self).__init__(*args)
        
        ui_path = os.path.join(
                               os.path.dirname(__file__), 
                               "settingsdialogui.ui"
                               )
        
        uic.loadUi(ui_path, self)
        
        self.name_edit.setDisabled(True)
        self.command_edit.setDisabled(True)
        self.icon_button.setDisabled(True)

        self.move_up_button.setIcon(get_qicon("go-up"))
        self.move_down_button.setIcon(get_qicon("go-down"))
        self.add_button.setIcon(get_qicon("list-add"))
        self.delete_button.setIcon(get_qicon("list-remove"))

        self.drop_zone = DropZone()
        self.drop_zone.setMinimumHeight(100)
        self.drop_zone.setText("Drag and drop your desktop shortcut here to use it in this application.")
        self.options_layout.addWidget(self.drop_zone)
        
        self.settings = Settings.read()

        try:
            self.options = self.settings["options"]
        except KeyError:
            self.options = {}
            self.settings["options"] = self.options
        
        try:
            self.shortcuts = self.settings["shortcuts"]
        except KeyError:
            self.shortcuts = []
            self.settings["shortcuts"] = self.shortcuts
        
        self.icon_size_spinbox.setValue(self.options.get("icon_size", 48))
        self.column_count_spinbox.setValue(self.options.get("column_count", 3))
        self.column_width_spinbox.setValue(self.options.get("column_width", 230))
        self.show_names_checkbox.setChecked(self.options.get("show_names", True))
        
        self.value_edited()
        
        self.refresh_shortcuts()
        
        self.shortcuts_listwidget.currentRowChanged.connect(self.selected_shortcut_changed)
        
        self.add_button.clicked.connect(self.add_button_clicked)
        self.delete_button.clicked.connect(self.delete_button_clicked)
        self.move_up_button.clicked.connect(self.move_up_button_clicked)
        self.move_down_button.clicked.connect(self.move_down_button_clicked)
    
        self.icon_size_spinbox.valueChanged.connect(self.value_edited)
        self.column_count_spinbox.valueChanged.connect(self.value_edited)
        self.column_width_spinbox.valueChanged.connect(self.value_edited)
        self.show_names_checkbox.stateChanged.connect(self.value_edited)
        self.name_edit.textEdited.connect(self.value_edited)
        self.command_edit.textEdited.connect(self.value_edited)
        
        self.drop_zone.dropped.connect(self.shortcut_dropped)
        
        self.icon_button.clicked.connect(self.icon_button_clicked)
    
    def refresh_shortcuts(self):
        while self.shortcuts_listwidget.count(): 
            self.shortcuts_listwidget.takeItem(0)
        
        for shortcut in self.shortcuts:
            item = QtGui.QListWidgetItem()
            
            item.setText(shortcut["name"])
            item.setIcon(get_qicon(shortcut["icon"]))

            self.shortcuts_listwidget.addItem(item)
    
    def add_button_clicked(self):
        shortcuts = self.shortcuts
        
        new_shortcut = {"name": "Shortcut{0}".format(len(shortcuts)),
                        "command": "command",
                        "icon": "application-x-executable"}
        
        shortcuts.append(new_shortcut)
        
        self.refresh_shortcuts()
        
        self.shortcuts_listwidget.setCurrentRow(
                                    self.shortcuts_listwidget.count()-1
                                                )
    
    def delete_button_clicked(self):
        current = self.shortcuts_listwidget.currentRow()
        
        if current == -1:
            return
        self.shortcuts_listwidget.setCurrentRow(-1)

        del self.shortcuts[current]

        self.refresh_shortcuts()

        self.shortcuts_listwidget.setCurrentRow(current)
    
    def move_up_button_clicked(self):
        current = self.shortcuts_listwidget.currentRow()
        
        if current == -1:
            return 
        
        shortcuts = self.shortcuts
        
        item = shortcuts.pop(current)
        self.shortcuts.insert(current-1, item)
        
        self.refresh_shortcuts()
        
        self.shortcuts_listwidget.setCurrentRow(current - 1)
    
    def move_down_button_clicked(self):
        current = self.shortcuts_listwidget.currentRow()
        
        if current == -1:
            return 
        
        shortcuts = self.shortcuts
        
        item = shortcuts.pop(current)
        self.shortcuts.insert(current+1, item)
        
        self.refresh_shortcuts()
        
        self.shortcuts_listwidget.setCurrentRow(current + 1)
    
    def selected_shortcut_changed(self):
        self.name_edit.setEnabled(True)
        self.command_edit.setEnabled(True)
        self.icon_button.setEnabled(True)
                       

        current = self.shortcuts_listwidget.currentRow()

        self.move_up_button.setEnabled(True)
        self.move_down_button.setEnabled(True)
 
        if current == -1:
            self.name_edit.setText("")
            self.command_edit.setText("")
            self.icon_button.setIcon(QtGui.QIcon(""))
            
            self.name_edit.setDisabled(True)
            self.command_edit.setDisabled(True)
            self.icon_button.setDisabled(True)
            
            return
        
        if current == 0:
            self.move_up_button.setEnabled(False)
        if current == self.shortcuts_listwidget.count()-1:
            self.move_down_button.setEnabled(False)

        shortcut = self.shortcuts[current]
        
        self.name_edit.setText(shortcut["name"])
        self.command_edit.setText(shortcut["command"])
        self.icon_button.setIcon(get_qicon(shortcut["icon"]))

        if self.icon_button.icon().isNull():
            self.icon_button.setText("Select\nIcon")
        else:
            self.icon_button.setText("")
        
    def value_edited(self):
        options = self.options
        shortcuts = self.shortcuts

        #options
        options["icon_size"] = self.icon_size_spinbox.value()
        options["column_count"] = self.column_count_spinbox.value()
        options["column_width"] = self.column_width_spinbox.value()
        options["show_names"] = self.show_names_checkbox.isChecked()
        
        #shortcuts
        current = self.shortcuts_listwidget.currentRow()

        if not current == -1:
            shortcuts[current]["name"] = self.name_edit.text()
            shortcuts[current]["command"] = self.command_edit.text()
            
            self.shortcuts_listwidget.currentItem().setText(self.name_edit.text())
            
    def icon_button_clicked(self):
        current = self.shortcuts_listwidget.currentRow()
        
        if current == -1:
            return

        icon=QtGui.QFileDialog.getOpenFileName(caption="Select Icon", directory="/usr/share/icons")
        
        if icon:
            self.shortcuts[current]["icon"] = icon
            self.icon_button.setIcon(QtGui.QIcon(icon))
        
        if self.icon_button.icon().isNull():
            self.icon_button.setText("Select\nIcon")
        else:
            self.icon_button.setText("")
        
        self.value_edited()
    
    def shortcut_dropped(self, name, command, icon):

        command = " ".join(i for i in command.split() if not i.startswith("%"))
        
        self.shortcuts.append({
                          "name": name,
                          "command": command,
                          "icon": icon
                          })
    
        self.refresh_shortcuts()
        
        self.shortcuts_listwidget.setCurrentRow(
                                    self.shortcuts_listwidget.count()-1
                                                )

if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    
    s = SettingsDialog()
    ret = s.exec_()
    
    if ret == 1:
        Settings.save(s.settings)
    
    app.exec_()