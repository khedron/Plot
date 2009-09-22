from PyQt4.QtCore import QObject, pyqtSignal

from base.property import prop_sig
from style.style import LineStyle

class Series(QObject):
	def __init__(self, type, data):
		object.__init__(self)
		self.type = type
		self.data = data

class Line(QObject):
	changed = pyqtSignal()

	style, style_changed = prop_sig(LineStyle, "style")
	point_style, point_style_changed = prop_sig(str, "point_style", "cross")
	point_size, point_size_changed = prop_sig(int, "point_size", 1)

	data_changed = pyqtSignal()

	def __init__(self, type_x, data_x, type_y, data_y):
		self.x = Series(type_x, data_x)
		self.y = Series(type_y, data_y)

		for signal in (self.style_changed, self.point_style_changed,
				self.point_size_changed, self.data_changed):
			signal.connect(self.changed)

# Data changing can't be a signal, as the type is arbitrary.
# So LineContainer must handle adding/removing/changing lines
# and keep a copy of the axes around to notify them of changes.

# How to handle accessing and changing the data?
# In GUI it will be a table view exposing a custom editor;
# maybe see spreadsheet example for details.

class LineContainer(QObject):
	e
