from PyQt4.QtCore import QObject

from base.property import prop_sig, link
from plotter import Plotter
from dimensions import Dimensions
from base.text import Text

# Current issues:
#   Should style attributes be passed in separately from the
#   data parts of each object?
#   It makes some things more convenient, but cf lines.
#   Maybe have a separate function that takes a data line and
#   returns a series suitable for Plotter

def float_range(start, stop, step):
	x = start
	while (x < stop):
		yield x
		x = x + step

class Axis():
	pass

# TODO: link Plotter properties to Graph properties as need be.
class Graph(QObject):

	def __init__(self):
		QObject.__init__(self)

		self.main_title = Text("Title")
		self.x_title = Text("X Axis")
		self.y_title = Text("Y Axis")

		self.dimensions = Dimensions()
		self.plotter = Plotter(dimensions=self.dimensions, main_title=self.main_title,
				x_title=self.x_title, y_title=self.y_title,)

		self.x_axis = Axis()
		self.y_axis = Axis()
		self.x_axis.length = 120
		self.y_axis.length = 70

		self.lines = []
		self.trends = []
		self.functions = []

	def dataline_to_graphline(self, line):
		return zip(self.x_axis.data_to_unit(line.x),
			        self.y_axis.data_to_unit(line.y))

	function_granularity = 0.1


#	def draw(self, plotter):
#		plotter.set_margins(self.margin_left, self.margin_top,
#				self.margin_right, self.margin_bottom)
#		plotter.set_grid_size(self.x_axis.length, self.y_axis.length)
#
#		for text, plotter_text in [(self.main_title, plotter.main_title),
#				(self.x_title, plotter.x_title), (self.y_title, plotter.y_title)]:
#			plotter_text.text = text.text
#			plotter_text.style = text.style
#		plotter.set_main_title(self.main_title.text, self.main_title.style)
#		plotter.set_x_title(self.x_title.text, self.x_title.style)
#		plotter.set_y_title(self.y_title.text, self.y_title.style)

#		plotter.draw_grid(self.x_axis.labels, self.y_axis.labels)
#
#		for line in self.lines:
#			plotter.draw_line(self.dataline_to_graphline(line),	line.style)
#
#		# Trend lines take a list of pairs of numbers and return functions
#		# Functions take a list of numbers and return a corresponding list
#		# Functions also have a style attribute ? Or separately?
#		trend_fns = []
#		for trend in self.trends:
#			trend_fns.append(trend.function)
#
#		x_vals = float_range(self.x_axis.data_start, self.x_axis.data_end,
#				self.function_granularity)
#		for function in self.functions + trend_fns: # Includes trend lines
#			f_vals = map(function, x_vals)
#			plotter.draw_line(zip(x_vals, f_vals), function.style)
#
