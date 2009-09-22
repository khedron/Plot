import pdb
#pdb.set_trace()

import sys

from PyQt4.QtGui import QApplication, QGraphicsScene, QGraphicsTextItem, QGraphicsView
from PyQt4.QtCore import QPointF
from PyQt4.QtCore import Qt

import config

from graph.plotter import Plotter
from graph.graph import Graph

# More imports below

config.debug.plotter.show_margin_boxes = True
config.debug.plotter.show_text_boxes = True

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


def table_test():
	"""
	Messing around with QTableWidgets

	This successfully creates a table of DateTimes and allows you to edit them.
	"""
	
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

if __name__ == "__main__":
	import sys
	if "--help" in sys.argv:
		print("Usage: %s [--table-test | --qt-test]" % sys.argv[0])
	elif "--table-test" in sys.argv:
		table_test()
	elif "--qt-test" in sys.argv:
		qt_test()
	else:
		main()
