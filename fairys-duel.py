#!/usr/bin/python

from PyQt4 import QtCore, QtGui

pink = QtCore.QString("#FF66CC")
blue = QtCore.QString("#00CCFF")

class TheBox (QtGui.QWidget):
	def make_blue(self):
		self.setStyleSheet("TheBox { background-color: " + blue + "; }")

	def make_pink(self):
		self.setStyleSheet("TheBox { background-color: " + pink + "; }")

	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self)

		layout = QtGui.QHBoxLayout(self)
		layout.addSpacing(10)

		b = QtGui.QPushButton("Make it blue")
		QtCore.QObject.connect(b, QtCore.SIGNAL("clicked()"), self.make_blue)
		# Only in PyQt 4.5 (here on Ubuntu it's 4.4)
		#b.clicked.connect(self.make_blue)
		layout.addWidget(b)

		r = QtGui.QPushButton("Make it pink")
		QtCore.QObject.connect(r, QtCore.SIGNAL("clicked()"), self.make_pink)
		#r.clicked.connect(self.make_pink)
		layout.addWidget(r)

if __name__ == "__main__":
	import sys
	app = QtGui.QApplication(sys.argv)
	widget = TheBox()
	widget.show()
	sys.exit(app.exec_())

