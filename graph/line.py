from PyQt4.QtCore import QObject, pyqtSignal, QVariant

from base.property import prop_sig
from style.style import LineStyle
from graph.type import Type

class Column(QObject):
	name, name_changed = prop_sig(str, "name")
	type, type_changed = prop_sig(QVariant.Type, "type")
	data, data_changed = prop_sig(list, "data")

	changed = pyqtSignal()

	def __init__(self, name, type, data):
		object.__init__(self)
		self.name = name
		self.type = type
		self.data = data

		for signal in (self.name_changed,
				self.type_changed, self.data_changed):
			signal.connect(self.changed)

class Line(QObject):

	point_styles = ["cross"]

	changed = pyqtSignal()

	style, style_changed = prop_sig(LineStyle, "style")
	point_style, point_style_changed = prop_sig(str, "point_style", point_styles[0])
	point_size, point_size_changed = prop_sig(float, "point_size", 1)

	x_data_changed = pyqtSignal(int, "QList<QVariant>")
	y_data_changed = pyqtSignal(int, "QList<QVariant>")

	def __init__(self, column_x, column_y):
		QObject.__init__(self)

		self.x = column_x
		self.x.changed.connect(self.emit_x)

		self.y = column_y
		self.y.changed.connect(self.emit_y)

		for signal in (self.style_changed, self.point_style_changed,
				self.point_size_changed, self.x.changed, self.y.changed):
			signal.connect(self.changed)
	
	def emit_x(self):
		self.x_data_changed.emit(id(self), self.x.data)

	def emit_y(self):
		self.y_data_changed.emit(id(self), self.y.data)

# Data change signalling possibilities:
#		- line has data_changed(QVariantList)
#		- line container must handle adding/removing/changing lines
#			and keep a copy of the axes around to notify them of changes.

# How to handle accessing and changing the data?
# In GUI it will be a table view exposing a custom editor;
# maybe see spreadsheet example for details.
