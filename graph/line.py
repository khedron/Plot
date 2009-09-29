from PyQt4.QtCore import QObject, pyqtSignal

from base.property import prop_sig
from style.style import LineStyle

class Series(QObject):
	def __init__(self, type, data):
		object.__init__(self)
		self.type = type
		self.data = data

class Line(QObject):

	point_styles = ["cross"]

	changed = pyqtSignal()

	style, style_changed = prop_sig(LineStyle, "style")
	point_style, point_style_changed = prop_sig(str, "point_style", point_styles[0])
	point_size, point_size_changed = prop_sig(float, "point_size", 1)

	data_changed = pyqtSignal()
	x_data_changed = pyqtSignal(int, "QList<QVariant>")
	"""x_data_changed(int id, QVariant-list data)"""
	y_data_changed = pyqtSignal(int, "QList<QVariant>")
	"""y_data_changed(int id, QVariant-list data)"""

	def __init__(self, type_x, data_x, type_y, data_y):
		QObject.__init__(self)
		self.x = Series(type_x, data_x)
		self.y = Series(type_y, data_y)

		for signal in (self.style_changed, self.point_style_changed,
				self.point_size_changed, self.data_changed):
			signal.connect(self.changed)

	def set_data(self, x_data, y_data):
		self.x.data = x_data
		self.y.data = y_data
		self.x_data_changed.emit(id(self), x_data)
		self.y_data_changed.emit(id(self), y_data)
		self.data_changed.emit()

# Data change signalling possibilities:
#		- line has data_changed(QVariantList)
#		- line container must handle adding/removing/changing lines
#			and keep a copy of the axes around to notify them of changes.

# How to handle accessing and changing the data?
# In GUI it will be a table view exposing a custom editor;
# maybe see spreadsheet example for details.
