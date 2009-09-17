# Proper division, even for integers
from __future__ import division

from PyQt4.QtGui import QGraphicsScene, QGraphicsTextItem, QGraphicsSimpleTextItem, QTextCursor, QColor, QPen, QTransform, QGraphicsRectItem
from PyQt4.QtCore import Qt, QObject, pyqtSignal, QString

from base.property import ro_prop, prop_sig
import config

# Text objects:
# parameters: scene, text, style, scene & grid dimensions
# scene at construction
# text, style at update method
# dimensions: another update method

red       = QColor(255,0,0,255)
red_t     = QColor(255,0,0,127)
green     = QColor(0,255,0,255)
green_t   = QColor(0,255,0,127)
blue      = QColor(0,0,255,255)
blue_t    = QColor(0,0,255,127)
cyan      = QColor(0,255,255,255)
cyan_t    = QColor(0,255,255,127)
magenta   = QColor(255,0,255,255)
magenta_t = QColor(255,0,255,127)
yellow    = QColor(255,255,0,255)
yellow_t  = QColor(255,255,0,127)
black     = QColor(0,0,0,255)
black_t   = QColor(0,0,0,127)

class TextItem(QObject):

	def __init__(self, text, scene, dimensions, transform_fn):
		"""\
		transform_fn(dimensions, w, h): returns a QTransform

		 * dimensions: plotter dimension object
		 * w: text width in pixels
		 * h: text height in pixels
		"""
		QObject.__init__(self)

		self.text = text
		self.scene = scene
		self.dimensions = dimensions
		self.transform = transform_fn

		self.text_item = None
		self.rect = None
		for signal in text.changed, dimensions.changed:
			signal.connect(self.update)

		self.update()

	def update(self):
		# Delete previous text item
		if self.text_item != None:
			self.scene.removeItem(self.text_item)
			# Line below not for QGraphicsSimpleTextItem
			self.text_item.deleteLater()
			self.scene.removeItem(self.rect)

		# Exit if any parameters unset
		if self.text.text == None or self.text.style == None:
			return

		self.text_item = self.get_text_item()
		size = self.text_item.boundingRect()
		w = size.width()
		h = size.height()
		transform = self.transform(self.dimensions, w, h)
		self.text_item.setTransform(transform)
		self.scene.addItem(self.text_item)

		self.rect = QGraphicsRectItem(0,0, w,h)
		self.rect.setTransform(transform)
		if config.debug.plotter.show_text_boxes:
			self.scene.addItem(self.rect)

	def get_text_item(self):
		text_item = QGraphicsTextItem(self.text.text, None)
		text_item.setDefaultTextColor(self.text.style.colour) # QGraphicsTextItem
		#text_item.setPen(self.text.style.colour) # QGraphicsSimpleTextItem
		text_item.setFont(self.text.style.font)
		text_item.setPos(0,0)
		return text_item

def main_title_transform(dimensions, w, h):
	# Place in middle of top margin, at centre of whole graph
	# or should I centre it on the grid?
	return QTransform().translate(
			dimensions.left_margin + dimensions.grid_width/2,
			dimensions.top_margin/2
			).translate(-w/2, -h/2)

def x_title_transform(dimensions, w, h):
	# Place in middle of bottom margin, at centre of the grid.
	return QTransform().translate(
			dimensions.left_margin + dimensions.grid_width/2,
			dimensions.height - dimensions.bottom_margin/2
			).translate(-w/2, -h/2)

def y_title_transform(dimensions, w, h):
	# Place in middle of left margin, at centre of the grid
	# and rotated 90 degrees anticlockwise
	return QTransform().translate(
			dimensions.left_margin/2,
			dimensions.top_margin + dimensions.grid_height/2
			).rotate(270).translate(-w/2, -h/2)

class Plotter(QObject):

	def __init__(self, dimensions, main_title, x_title, y_title):
		QObject.__init__(self)

		self.dimensions = dimensions
		self.scene = QGraphicsScene()

		self.main_title = TextItem(main_title, self.scene, self.dimensions, main_title_transform)
		self.x_title = TextItem(x_title, self.scene, self.dimensions, x_title_transform)
		self.y_title = TextItem(y_title, self.scene, self.dimensions, y_title_transform)

		if config.debug.plotter.show_margin_boxes:
			self.debug_margin_boxes = []
			dimensions.changed.connect(self.show_margin_boxes)
			self.show_margin_boxes()

	def show_margin_boxes(self):
		for rect in self.debug_margin_boxes:
			self.scene.removeItem(rect)
		r = []
		r.append(self.scene.addRect(0,0, self.dimensions.left_margin, self.dimensions.height,
				red, red_t))
		r.append(self.scene.addRect(0,0, self.dimensions.width, self.dimensions.top_margin,
				green, green_t))
		r.append(self.scene.addRect(0, self.dimensions.top_margin + self.dimensions.grid_height,
				self.dimensions.width, self.dimensions.bottom_margin,
				blue, blue_t))
		r.append(self.scene.addRect(self.dimensions.width, self.dimensions.height,
				-self.dimensions.right_margin, -self.dimensions.height,
				cyan, cyan_t))
		halfway_height = self.dimensions.top_margin + self.dimensions.grid_height/2
		r.append(self.scene.addLine(0, halfway_height,
				self.dimensions.width, halfway_height,
				QPen(black, 0)))
		halfway_width = self.dimensions.left_margin + self.dimensions.grid_width/2
		r.append(self.scene.addLine(halfway_width, 0,
				halfway_width, self.dimensions.height,
				QPen(black, 0)))
		self.debug_margin_boxes = r

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

