from PyQt4.QtCore import QObject, pyqtSignal

from base.property import prop_sig

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
