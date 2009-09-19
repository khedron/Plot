from PyQt4.QtGui import QFont, QColor, QPen, QBrush
from PyQt4.QtCore import QObject, Qt, pyqtSignal, pyqtProperty

from base.property import prop_sig
"""
Classes that hold presentation styles for text, lines and areas
"""

"""
Note: the properties of text in Qt are specified by
QFont and QPen. QPen is for colour, QFont for all else.
However, QColor can be used in place of QPen.
"""

class TextStyle(QObject):
	changed = pyqtSignal()

	font, font_changed = prop_sig(QFont, "font")
	colour, colour_changed = prop_sig(QColor, "colour", Qt.black)

	def __init__(self):
		QObject.__init__(self)
		for signal in self.font_changed, self.colour_changed:
			signal.connect(self.changed)

"""
Note: the properties of lines and areas in Qt are specified
by QPen and QBrush.

For areas, QPen is for the outline and QBrush is the fill.

For lines, QPen is for the stroke and QBrush should be
transparent, since for some line types the start and end
points are joined and the resulting enclosed area(s) are
filled with QBrush.
"""

class LineStyle(QObject):
	changed = pyqtSignal()

	stroke_colour, stroke_colour_changed = prop_sig(QColor, "stroke_colour", Qt.black)
	# 0 width in a QGraphicsScene indicates a
	# cosmetic line that will always be visible
	stroke_width, stroke_width_changed = prop_sig(int, "stroke_width", 0)

	# Outline colour
	pen = pyqtProperty(QPen,
			lambda self: QPen(QBrush(self.stroke_colour),self.stroke_width))
	# Fill colour
	brush = pyqtProperty(QBrush, lambda self: QBrush(Qt.transparent))

	def __init__(self):
		QObject.__init__(self)
		for signal in self.stroke_colour_changed, self.stroke_width_changed:
			signal.connect(self.changed)

