from QtCore import QObject

from base.property import prop_sig
from graph.plotter import Plotter
from style.textstyle import TextStyle
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

class Text(object):
	style, style_changed = prop_sig(TextStyle, "style")
	text, text_changed = prop_sig(str, "text")

class Graph(QObject):

	def dataline_to_graphline(self, line):
		return zip(self.x_axis.data_to_unit(line.x),
			        self.y_axis.data_to_unit(line.y))

	margin_left, margin_left_changed = prop_sig(float, "margin_left", 10)
	margin_top, margin_top_changed = prop_sig(float, "margin_top", 10)
	margin_right, margin_right_changed = prop_sig(float, "margin_right", 10)
	margin_bottom, margin_bottom_changed = prop_sig(float, "margin_bottom", 10)

	function_granularity = 0.1
	
	title = Text()
	x_label = Text()
	y_label = Text()

	lines = []
	trends = []
	functions = []

	x_axis = Axis()
	y_axis = Axis()

	def __init__(self):
		self.x_axis.length = 120
		self.y_axis.length = 70
		self.title.text = "Title"
		self.x_label.text = "X Axis"
		self.y_label.text = "Y Axis"

	def draw(self, plotter):
		plotter.set_margins(self.margin_left, self.margin_top,
				self.margin_right, self.margin_bottom)
		plotter.set_grid_size(self.x_axis.length, self.y_axis.length)

		plotter.draw_title(self.title.text, self.title.style)
		plotter.draw_x_title(self.x_label.text, self.x_label.style)
		plotter.draw_y_title(self.y_label.text, self.y_label.style)

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
