from PyQt4.QtGui import QPainter

from style.textstyle import TextStyle


class Plotter(object):
	def __init__(self, qpaintdevice):
		object.__init__(self)
		self.painter = QPainter(qpaintdevice)

	px_per_unit = 7

	l_margin = 20.0
	t_margin = 20.0
	r_margin = 20.0
	b_margin = 20.0

	grid_w = 120.0
	grid_h = 70.0

	# @property syntax seems to cloud the code; not using
	width = property(lambda self: self.l_margin + self.grid_w + self.r_margin)
	height = property(lambda self: self.t_margin + self.grid_h + self.b_margin)

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
		# TODO - set style
		self.painter.save()
		self.painter.setPen(style.colour)
		self.painter.setFont(style.font)
		self.painter.drawText(QRectF(0,0, self.width,self.t_margin),
				Qt.AlignCenter | Qt.TextWordWrap,
				text)
		self.painter.restore()

	def draw_x_title(self, text, style):
		pass

	def draw_y_title(self, text, style):
		pass

