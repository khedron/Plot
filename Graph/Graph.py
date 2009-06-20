from QtCore import QObject
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

class Graph(QObject):

	def dataline_to_graphline(self, line):
		return zip(self.x_axis.data_to_unit(line.x),
			        self.y_axis.data_to_unit(line.y))

	function_granularity = 0.1
	
	title = x_label = y_label = None

	lines = []
	trends = []
	functions = []

	x_axis = Axis()
	y_axis = Axis()
	def __init__(self):
		x_axis.length = 120
		y_axis.length = 70

	def draw(self, plotter):
		plotter.set_margins() # TODO
		plotter.set_grid_height(self.y_axis.length)
		plotter.set_grid_width(self.x_axis.length)

		plotter.draw_title(self.title.text, self.title.style)
		plotter.draw_x_title(self.x_label.text, self.x_label.style)
		plotter.draw_y_title(self.y_label.text, self.y_label.style)

		plotter.draw_grid(self.x_axis.labels, self.y_axis.labels)

		for line in self.lines:
			plotter.draw_line(self.dataline_to_graphline(line),	line.style)

		# Trend lines take a list of pairs of numbers and return functions
		# Functions take a list of numbers and return a corresponding list
		# Functions also have a style attribute ? Or separately?
		trend_fns = []
		for trend in self.trends:
			trend_fns.append(trend.function)

		for function in self.functions + trend_fns: # Includes trend lines
			plotter.draw_line([(x, function(x)) for x in float_range(self.x_axis.data_start, self.x_axis.data_end, self.function_granularity)], function.style)
