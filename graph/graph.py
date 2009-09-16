from PyQt4.QtCore import QObject

from base.property import prop_sig, link
from plotter import Plotter
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

class Text(QObject):
	style, style_changed = prop_sig(TextStyle, "style")
	text, text_changed = prop_sig(str, "text")

	def __init__(self, text = None, parent = None):
		QObject.__init__(self, parent)
		if text is not None:
			self.text = text


# TODO: link Plotter properties to Graph properties as need be.
class Graph(QObject):

	def dataline_to_graphline(self, line):
		return zip(self.x_axis.data_to_unit(line.x),
			        self.y_axis.data_to_unit(line.y))

	margin_left, margin_left_changed = prop_sig(float, "margin_left", 20)
	margin_top, margin_top_changed = prop_sig(float, "margin_top", 20)
	margin_right, margin_right_changed = prop_sig(float, "margin_right", 20)
	margin_bottom, margin_bottom_changed = prop_sig(float, "margin_bottom", 20)

	function_granularity = 0.1
	
	def __init__(self):
		self.x_axis = Axis()
		self.y_axis = Axis()
		self.x_axis.length = 120
		self.y_axis.length = 70

		self.plotter = Plotter()

		self.title = Text("Title")
		self.x_label = Text("X Axis")
		self.y_label = Text("Y Axis")

		for mine, yours in [(self.title, self.plotter.main_title),
                                    (self.x_label, self.plotter.x_title),
		                    (self.y_label, self.plotter.y_title)]:
			yours.text = mine.text
			yours.style = mine.style
			link(mine, "text", yours, "text")
			link(mine, "style", yours, "style")

		self.lines = []
		self.trends = []
		self.functions = []


	def draw(self, plotter):
		plotter.set_margins(self.margin_left, self.margin_top,
				self.margin_right, self.margin_bottom)
		plotter.set_grid_size(self.x_axis.length, self.y_axis.length)

		for text, plotter_text in [(self.title, plotter.main_title),
				(self.x_label, plotter.x_title), (self.y_label, plotter.y_title)]:
			plotter_text.text = text.text
			plotter_text.style = text.style
#		plotter.set_main_title(self.title.text, self.title.style)
#		plotter.set_x_title(self.x_label.text, self.x_label.style)
#		plotter.set_y_title(self.y_label.text, self.y_label.style)

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
