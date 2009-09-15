# Proper division, even for integers
from __future__ import division

from PyQt4.QtGui import QGraphicsScene, QGraphicsTextItem, QTextCursor, QColor, QTransform
from PyQt4.QtCore import Qt, QObject, pyqtSignal, QString

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
#def set_text_alignment(text_item, alignment):
#	cursor = text_item.textCursor()
#	cursor.select(QTextCursor.Document)
#	bfmt = cursor.blockFormat()
#	bfmt.setAlignment(alignment)
#	cursor.setBlockFormat(bfmt)
#	text_item.setTextCursor(cursor)

# Text objects:
# parameters: scene, text, style, scene & grid dimensions
# scene at construction
# text, style at update method
# dimensions: another update method


# TODO: setting defaults for Dimensions helps simplify the GraphicsItem code
# as we don't have to check whether the dimensions have been set yet before
# accessing them.
#
# However, this causes duplication of default values in Graph and Plotter.
# The properties should be linked anyhow.
class Dimensions(QObject):
	changed = pyqtSignal()

	left_margin, left_margin_changed = prop_sig(float, "left_margin", 20)
	top_margin, top_margin_changed = prop_sig(float, "top_margin", 20)
	right_margin, right_margin_changed = prop_sig(float, "right_margin", 20)
	bottom_margin, bottom_margin_changed = prop_sig(float, "bottom_margin", 20)

	grid_width, grid_width_changed = prop_sig(float, "grid_width", 120)
	grid_height, grid_height_changed = prop_sig(float, "grid_height", 70)

	# @property syntax seems to cloud the code; not using it
	width = property(lambda self: self.left_margin + self.grid_width + self.right_margin)
	height = property(lambda self: self.top_margin + self.grid_height + self.bottom_margin)

	def __init__(self):
		QObject.__init__(self)
		# Connect all signals to changed() signal
		for signal in [ self.left_margin_changed, self.top_margin_changed,
				self.right_margin_changed, self.bottom_margin_changed,
				self.grid_width_changed, self.grid_height_changed ]:
			signal.connect(self.changed)

class TextItem(QObject):
	text, text_changed = prop_sig(QString, "text", None)
	style, style_changed = prop_sig(TextStyle, "style", None)

	def __init__(self, scene, dimensions, transform_fn):
		"""
		transform_fn(dimensions): returns a QTransform
		"""
		QObject.__init__(self)
		self.scene = scene
		self.dimensions = dimensions
		self.transform = transform_fn
		self.text_item = None
		for signal in [self.text_changed, self.style_changed, dimensions.changed]:
			signal.connect(self.update)

	def update(self):
		# Delete previous text item
		if self.text_item is not None:
			self.scene.removeItem(self.text_item)
			self.text_item.deleteLater()

		# Exit if any parameters unset
		if self.text is None or self.style is None:
			return

		self.text_item = self.get_text_item(self.text, self.style)
		self.text_item.setTransform(self.transform(self.dimensions))
		self.scene.addItem(self.text_item)

	def get_text_item(text, style):
		text_item = QGraphicsTextItem(text, None)
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

def main_title_transform(dimensions):
	# Place in middle of top margin, at centre of whole graph
	# or should I centre it on the grid?
	return QTransform().translate(
			dimensions.width/2, dimensions.top_margin/2)

def x_title_transform(dimensions):
	# Place in middle of bottom margin, at centre of the grid.
	return QTransform().translate(
			dimensions.left_margin + dimensions.grid_width/2,
			dimensions.height - dimensions.bottom_margin/2)

def y_title_transform(dimensions):
	# Place in middle of left margin, at centre of the grid
	# and rotated 90 degrees anticlockwise
	return QTransform().translate(
			dimensions.left_margin/2,
			dimensions.top_margin + dimensions.grid_height/2
			)#.rotate(270)

class Plotter(QObject):
	px_per_unit = 7

	def __init__(self):
		QObject.__init__(self)

		self.dimensions = Dimensions()
		self.scene = QGraphicsScene()

		self.main_title = TextItem(self.scene, self.dimensions, main_title_transform)
		self.x_title = TextItem(self.scene, self.dimensions, x_title_transform)
		self.y_title = TextItem(self.scene, self.dimensions, y_title_transform)

		self.scene.addRect(0,0, self.dimensions.left_margin, self.dimensions.height,
				QColor(255,0,0,255), QColor(255,0,0,128))
		self.scene.addRect(0,0, self.dimensions.width, self.dimensions.top_margin,
				QColor(0,255,0,255), QColor(0,255,0,128))
		self.scene.addRect(0, self.dimensions.top_margin + self.dimensions.grid_height,
				self.dimensions.width, self.dimensions.bottom_margin,
				QColor(0,0,255,255), QColor(0,0,255,128))
		self.scene.addRect(self.dimensions.width, self.dimensions.height,
				-self.dimensions.right_margin, -self.dimensions.height,
				QColor(0,255,255,255), QColor(0,255,255,128))

		self.main_title.text_changed.connect(self.doit)
		self.main_title.style_changed.connect(self.doit)


	def doit():
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
		a = __add_text(self, self.main_title.text, self.main_title.style)
		a.setPos(0,0)
		QMessageBox.critical(None, "Text changed", "Main title stuff changed.")



	def set_px_per_unit(self, ppu):
		self.px_per_unit = ppu

	def set_margins(self, l,t,r,b):
		self.dimensions.left_margin = l
		self.dimensions.top_margin = t
		self.dimensions.right_margin = r
		self.dimensions.bottom_margin = b

	def set_grid_size(self, w, h):
		self.dimensions.grid_width = w
		self.dimensions.grid_height = h

