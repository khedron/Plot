from PyQt4.QtGui import QFont, QColor
from PyQt4.QtCore import Qt

from base.property import prop_sig

# Note: the properties of text in Qt are specified by
# QFont and QPen. QPen is for colour, QFont for all else.
# However, QColor can be used in place of QPen.

class TextStyle(object):
	font, font_changed = prop_sig(QFont, "font")
	colour, colour_changed = prop_sig(QColor, "colour", Qt.black)
