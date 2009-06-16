
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

class Graph(QtCore.QObject):

	def dataline_to_graphline(self, line):
		return zip(self.x_axis.dataToUnit(line.x),
			        self.y_axis.dataToUnit(line.y))

	function_granularity = 0.1
	
	title = x_label = y_label = None

	lines = []
	trends = []
	functions = []

	def draw(self, plotter):
		plotter.setMargins() # TODO
		plotter.setGridHeight(self.y_axis.length)
		plotter.setGridWidth(self.x_axis.length)

		plotter.drawTitle(self.title.text, self.title.style)
		plotter.drawXTitle(self.x_label.text, self.x_label.style)
		plotter.drawYTitle(self.y_label.text, self.y_label.style)

		plotter.drawGrid(self.x_axis.labels, self.y_axis.labels)

		for line in self.lines:
			plotter.drawLine(self.dataline_to_graphline(line),	line.style)

		# Trend lines take a list of pairs of numbers and return functions
		# Functions take a list of numbers and return a corresponding list
		# Functions also have a style attribute ? Or separately?
		trend_fns = []
		for trend in self.trends:
			trend_fns.append(trend.function)

		for function in self.functions + trend_fns: # Includes trend lines
			plotter.drawLine([x, function(x) for x in float_range(self.x_axis.dataStart, self.x_axis.dataEnd, self.function_granularity)], function.style)
