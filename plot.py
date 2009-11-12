import pdb
#pdb.set_trace()

import sys

from PyQt4.QtGui import QApplication, QGraphicsScene, QGraphicsTextItem, QGraphicsView
from PyQt4.QtCore import QPointF
from PyQt4.QtCore import Qt

import config

# from graph.plotter import Plotter
from graph.graph import Graph

# More imports below

config.debug.plotter.show_margin_boxes = False
config.debug.plotter.show_text_boxes = False

app = QApplication(sys.argv)

def main():
	graph = Graph()
	view = QGraphicsView(graph.plotter.scene)
	view.scale(3,3)
	view.show()

	sys.exit(app.exec_())

def qt_test():
	"""
	Test that Qt actually works
	"""
	scene = QGraphicsScene()
	text = QGraphicsTextItem(None, scene)
	text.setHtml("<h2 align=\"center\">hello</h2><h2 align=\"center\">world 12334345354444444444444444444444444</h2>123");
	text.setPos(QPointF(25,25))
	view = QGraphicsView(scene)
	view.show()
	sys.exit(app.exec_())



def table_test():
	"""
	Messing around with QTableWidgets

	This successfully creates a table of DateTimes and allows you to edit them.
	"""

	from PyQt4.QtGui import QTableWidget, QTableWidgetItem, QItemEditorCreatorBase, QDateTimeEdit, QItemEditorFactory, QStyledItemDelegate
	from PyQt4.QtCore import QVariant, QDateTime, QObject

	class DateTimeEditorCreator(QItemEditorCreatorBase):
		"""
		See gui/itemviews/qitemeditorfactory.cpp for implementations of
		createEditor() and valuePropertyName()
		"""
		def __init__(self):
			QItemEditorCreatorBase.__init__(self)

		def createWidget(self, parent):
			wid = QDateTimeEdit(parent)
			wid.setCalendarPopup(True)
			wid.setFrame(False)
			return wid

		def valuePropertyName(self):
			return "dateTime"

	def die():
		raise MyError("Oops")

	class MyError(Exception):
		def __init__(self, value):
			self.value = value
		def __str__(self):
			return repr(self.value)

	tableWidget = QTableWidget(12, 3)
	tableWidget.setItemDelegate(QStyledItemDelegate())
	tableWidget.itemDelegate().setItemEditorFactory(QItemEditorFactory())
	tableWidget.itemDelegate().itemEditorFactory().registerEditor(QVariant.DateTime, DateTimeEditorCreator())
	for row in range(10):
		for col in range(3):
			date = QDateTime.currentDateTime()
			string = str(row) + ',' + str(col)
			item = QTableWidgetItem()
			item.setData(Qt.DisplayRole, QVariant(date))
			tableWidget.setItem(row, col, item)
	tableWidget.show()
	sys.exit(app.exec_())

def interpret():
	"""
	Embedding a Python interpreter!
	"""
	import sys
	import code
	from StringIO import StringIO

	from PyQt4.QtCore import QObject, QString, pyqtSignal
	from PyQt4.QtGui import QWidget, QGridLayout, QTextEdit, QLineEdit, QLabel

	# TODO: colour text based on stderr/stdout
	#       print input text alongside output (different colour?)
	class Interpreter(QObject, code.InteractiveConsole):
		output = pyqtSignal(QString)

		def __init__(self):
			QObject.__init__(self)
			self.l = {}
			code.InteractiveConsole.__init__(self, self.l)
			self.out = StringIO()

		def write(self, data):
			self.output.emit(data)

		def runcode(self, codez):
			"""
			Reimplementation to capture stdout and stderr
			"""
			sys.stdout = self.out
			sys.stderr = self.out
			result = code.InteractiveConsole.runcode(self, codez)
			sys.stdout = sys.__stdout__
			sys.stderr = sys.__stderr__
			self.output.emit(self.out.getvalue())
			return result


	wid = QWidget()
	layout = QGridLayout(wid)

	display = QTextEdit()
	display.setReadOnly(True)
	layout.addWidget(display, 0,0, 1,2)

	prompt = QLabel(">>>")
	layout.addWidget(prompt, 1,0)

	input = QLineEdit()
	layout.addWidget(input, 1,1)

	interp = Interpreter()

	def text_input():
		text = input.text()
		input.clear()

		if interp.push(str(text)):
			# More input required
			# Use sys.ps1 and sys.ps2
			prompt.setText("...")
		else:
			prompt.setText(">>>")

	input.returnPressed.connect(text_input)
	
	def text_output(text):
		display.setPlainText(text)
		#display.append(text)
	
	interp.output.connect(text_output)

	wid.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	import sys
	if "--help" in sys.argv:
		print("Usage: %s [ --table-test | --qt-test | --interpret ]" % sys.argv[0])
	elif "--table-test" in sys.argv:
		table_test()
	elif "--qt-test" in sys.argv:
		qt_test()
	elif "--interpret" in sys.argv:
		interpret()
	else:
		main()
