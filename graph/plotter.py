from PyQt4.QtGui import QGraphicsScene, QGraphicsTextItem
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

def set_text_alignment(text_item, alignment):
	cursor = text_item.textCursor()
	cursor.select(QTextCursor.Document)
	bfmt = cursor.blockFormat()
	bfmt.setAlignment(alignment)
	cursor.setBlockFormat(bfmt)
	text_item.setTextCursor(cursor)

class Plotter(object):
	def __init__(self):
		object.__init__(self)

	px_per_unit = 7

	l_margin = 20.0
	t_margin = 20.0
	r_margin = 20.0
	b_margin = 20.0

	grid_w = 120.0
	grid_h = 70.0

	# @property syntax seems to cloud the code; not using it
	width = property(lambda self: self.l_margin + self.grid_w + self.r_margin)
	height = property(lambda self: self.t_margin + self.grid_h + self.b_margin)

	scene = ro_prop(QGraphicsScene, "scene")

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

	def draw_main_title(self, text, style):
		text_item = QGraphicsTextItem(text, None, self.scene)
		text_item.setPos(self.width/2, self.t_margin/2)
		# text_item.rotate(degrees)
		text_item.setDefaultTextColor(style.colour)
		text_item.setFont(style.font)
		set_text_alignment(text_item, Qt.AlignCenter)
		text_item.setTextWidth(self.width * 2/3.0)

	def draw_x_title(self, text, style):
		pass

	def draw_y_title(self, text, style):
		pass

