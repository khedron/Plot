# Proper division, even for integers
from __future__ import division

from PyQt4.QtGui import QGraphicsScene, QGraphicsTextItem, QTextCursor, QColor
from PyQt4.QtCore import Qt, QObject

from style.textstyle import TextStyle
from base.property import ro_prop, prop_sig

# == Text ==
# QGraphicsSimpleTextItem supports colour (setPen) and font (setFont).
# However, it doesn't seem to support alignment.
#
# QGraphicsTextItem supports colour (setDefaultTextColor) and font (setFont).
# It doesn't seem to directly support alignment, but it uses QTextDocument, which does.
#
# Fragment for setting text alignment taken from
# http://www.qtcentre.org/forum/f-qt-programming-2/t-qgraphicstextitem-sethtml-4420.html
# NOTE THAT THIS DOESN'T WORK AS IT STANDS.
#
# void setTextAlignment(Qt::Alignment alignment)
# {
#   QTextCursor cursor = m_gtextItem->textCursor();
#   // Added by John to select whole document, not just current paragraph
#   cursor.select(QTextCursor::Document);
#   QTextBlockFormat bfmt = cursor.blockFormat();
#   bfmt.setAlignment(Qt::AlignCenter);
#   cursor.setBlockFormat(bfmt);
#   m_gtextItem->setTextCursor(cursor); 
# }

# This doesn't work!
def set_text_alignment(text_item, alignment):
	cursor = text_item.textCursor()
	cursor.select(QTextCursor.Document)
	bfmt = cursor.blockFormat()
	bfmt.setAlignment(alignment)
	cursor.setBlockFormat(bfmt)
	text_item.setTextCursor(cursor)

class Plotter(QObject):
	px_per_unit = 7

	left_margin, left_margin_changed = prop_sig(float, "left_margin", 20)
	top_margin, top_margin_changed = prop_sig(float, "top_margin", 20)
	right_margin, right_margin_changed = prop_sig(float, "right_margin", 20)
	bottom_margin, bottom_margin_changed = prop_sig(float, "bottom_margin", 20)

	grid_width, grid_width_changed = prop_sig(float, "grid_width", 120)
	grid_height, grid_height_changed = prop_sig(float, "grid_height", 70)

	main_title, main_title_changed = prop_sig(tuple, "main_title")
	x_title, x_title_changed = prop_sig(tuple, "x_title")
	y_title, y_title_changed = prop_sig(tuple, "y_title")

	# @property syntax seems to cloud the code; not using it
	width = property(lambda self: self.left_margin + self.grid_width + self.right_margin)
	height = property(lambda self: self.top_margin + self.grid_height + self.bottom_margin)

	scene = ro_prop(QGraphicsScene, "scene")

	def __init__(self):
		QObject.__init__(self)
		self.scene.addRect(0,0, self.left_margin, self.height,
				QColor(255,0,0,255), QColor(255,0,0,128))
		self.scene.addRect(0,0, self.width, self.top_margin,
				QColor(0,255,0,255), QColor(0,255,0,128))
		self.scene.addRect(0, self.top_margin + self.grid_height,
				self.width, self.bottom_margin,
				QColor(0,0,255,255), QColor(0,0,255,128))
		self.scene.addRect(self.width, self.height,
				-self.right_margin, -self.height,
				QColor(0,255,255,255), QColor(0,255,255,128))

	# TODO make these text objects with their own internal state?
	def set_main_title(self, text, style):
		text_item, w, h = self._add_text(text, style)

		# Sigh... have to align text manually.
		text_item.setPos(self.width/2 - w/2, self.top_margin/2 + h/2)
		text_item.setTextWidth(self.width * 2/3)

	def set_x_title(self, text, style):
		text_item, w, h = self._add_text(text, style)

		# Place in middle of bottom margin, at centre of the grid.
		text_item.setPos(self.left_margin + self.grid_width/2 - w/2,
				self.height - self.bottom_margin/2 + h/2)
		text_item.setTextWidth(self.grid_width)

	def set_y_title(self, text, style):
		text_item, w, h = self._add_text(text, style)

		# Place in middle of left margin, at centre of the grid
		# and rotated 90 degrees anticlockwise
		text_item.setPos(self.left_margin/2 - w/2,
				self.top_margin + self.grid_height/2 + h/2)
		#text_item.rotate(270)
		text_item.setTextWidth(self.grid_height)

	def set_px_per_unit(self, ppu):
		self.px_per_unit = ppu

	def set_margins(self, l,t,r,b):
		self.left_margin = l
		self.top_margin = t
		self.right_margin = r
		self.bottom_margin = b

	def set_grid_size(self, w, h):
		self.grid_width = w
		self.grid_height = h

	def _add_text(self, text, style):
		text_item = QGraphicsTextItem(text, None, self.scene)
		text_item.setDefaultTextColor(style.colour)
		text_item.setFont(style.font)
		w = text_item.textWidth()
		if style.font.pixelSize() != -1:
			# -1 means invalid; use point size
			h = style.font.pixelSize()  
		else:
			# Approximate conversion; a point is 1/72"; pixels these
			# days are 1/96"
			h = style.font.pointSize() * 96/72
		return text_item, w, h

