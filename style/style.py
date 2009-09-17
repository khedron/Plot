from PyQt4.QtGui import QFont, QColor, QPen, QBrush
from PyQt4.QtCore import QObject, Qt, pyqtSignal, pyqtProperty

from base.property import prop_sig

# Note: the properties of text in Qt are specified by
# QFont and QPen. QPen is for colour, QFont for all else.
# However, QColor can be used in place of QPen.

class TextStyle(QObject):
	changed = pyqtSignal()

	font, font_changed = prop_sig(QFont, "font")
	colour, colour_changed = prop_sig(QColor, "colour", Qt.black)

	def __init__(self):
		QObject.__init__(self)
		for signal in self.font_changed, self.colour_changed:
			signal.connect(self.changed)

class LineStyle(QObject):
	changed = pyqtSignal()

	stroke_colour, stroke_colour_changed = prop_sig(QColor, "stroke_colour", Qt.black)
	# 0 width in a QGraphicsScene indicates a
	# cosmetic line that will always be visible
	stroke_width, stroke_width_changed = prop_sig(int, "stroke_width", 0)

	# Outline colour
	pen = pyqtProperty(QPen, lambda self: QPen(QBrush(self.stroke_colour),self.stroke_width))
	# Fill colour
	brush = pyqtProperty(QBrush, lambda self: QBrush(Qt.transparent))

	def __init__(self):
		QObject.__init__(self)
		for signal in self.stroke_colour_changed, self.stroke_width_changed:
			signal.connect(self.changed)

