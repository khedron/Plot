# Proper division, even for integers
from __future__ import division

from PyQt4.QtGui import QGraphicsScene, QGraphicsTextItem, QTextCursor, QColor
from PyQt4.QtCore import Qt

from style.textstyle import TextStyle
from base.property import ro_prop

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

class Plotter(object):
	px_per_unit = 7

	l_margin = 20
	t_margin = 20
	r_margin = 20
	b_margin = 20

	grid_w = 120
	grid_h = 70

	# @property syntax seems to cloud the code; not using it
	width = property(lambda self: self.l_margin + self.grid_w + self.r_margin)
	height = property(lambda self: self.t_margin + self.grid_h + self.b_margin)

	scene = ro_prop(QGraphicsScene, "scene")

	def __init__(self):
		object.__init__(self)
		self.scene.addRect(0,0, self.l_margin, self.height,
				QColor(255,0,0,255), QColor(255,0,0,128))
		self.scene.addRect(0,0, self.width, self.t_margin,
				QColor(0,255,0,255), QColor(0,255,0,128))
		self.scene.addRect(0, self.t_margin + self.grid_h,
				self.width, self.b_margin,
				QColor(0,0,255,255), QColor(0,0,255,128))
		self.scene.addRect(self.width, self.height,
				-self.r_margin, -self.height,
				QColor(0,255,255,255), QColor(0,255,255,128))

	def set_main_title(self, text, style):
		text_item, w, h = self._get_text(text, style)

		# Sigh... have to align text manually.
		text_item.setPos(self.width/2 - w/2, self.t_margin/2 + h/2)
		text_item.setTextWidth(self.width * 2/3)

	def set_x_title(self, text, style):
		text_item, w, h = self._get_text(text, style)

		# Place in middle of bottom margin, at centre of the grid.
		text_item.setPos(self.l_margin + self.grid_w/2 - w/2,
				self.height - self.b_margin/2 + h/2)
		text_item.setTextWidth(self.grid_w)

	def set_y_title(self, text, style):
		text_item, w, h = self._get_text(text, style)

		# Place in middle of left margin, at centre of the grid
		# and rotated 90 degrees anticlockwise
		text_item.setPos(self.l_margin/2 - w/2,
				self.t_margin + self.grid_h/2 + h/2)
		#text_item.rotate(270)
		text_item.setTextWidth(self.grid_h)

	def set_px_per_unit(self, ppu):
		self.px_per_unit = ppu

	def set_margins(self, l,t,r,b):
		self.l_margin = l
		self.t_margin = t
		self.r_margin = r
		self.b_margin = b

	def set_grid_size(self, w, h):
		self.grid_w = w
		self.grid_h = h

	def _get_text(self, text, style):
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

