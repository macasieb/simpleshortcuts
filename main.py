#! /usr/bin/env python

import sys

import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)

from PyQt4.QtGui import QApplication

from mainui import MainUi

app = QApplication(sys.argv)
rect = app.desktop().geometry()

g = MainUi()
g.show()

g.move(rect.center() - g.rect().center())

app.exec_()
