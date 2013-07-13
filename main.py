#! /usr/bin/env python2

import os
import sys
import argparse

import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)

from PyQt4.QtGui import QApplication

from mainui import MainUi
from settings import Settings

try:
    use_lock = Settings.read()["options"]["use_lock"]
except KeyError:
    use_lock = False

if(use_lock):
    import fcntl

    LOCK_FILE = os.path.join(settings.settings_path, "simpleshortcuts.lock")
    print("Using lock file:", LOCK_FILE)

    f = open(LOCK_FILE, "w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError as err:
        if(err.errno == 11):
            print("There is another instance running. Exiting...")
            sys.exit(1)

parser = argparse.ArgumentParser(description="SimpleShortcuts")
parser.add_argument("-s", "--settings",
                    help="Show the settings dialog",
                    action="store_true")
parser.add_argument("-i", "--imitate",
                    help="Show and immediately close the main window.",
                    action="store_true")

args = parser.parse_args()

app = QApplication(sys.argv)

if args.settings:
    from settingsdialog import SettingsDialog
    g = SettingsDialog()
else:
    try:
        g = MainUi()
    except Exception as err:
        print("An exception has occured!")
        print("Try opening the settings dialog with -s parameter and resaving the settings.",
              "You may have to delete your settings file as last resort."
            )
        raise err

g.show()

if args.imitate: sys.exit()

rect = app.desktop().screenGeometry()
g.move(rect.center() - g.rect().center())

app.exec_()
