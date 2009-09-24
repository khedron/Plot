from __future__ import division

import math
import itertools
from sys import float_info

from PyQt4.QtCore import QObject, QVariant
from PyQt4.QtGui import QDoubleSpinBox

from base.property import prop_sig

"""
== Axis classes
Axis classes are designed to abstract axis scaling for different
types. They work on one dimension of the data - the x-axis
_or_ the y-axis. They take lists of single values, not
lists of tuples.

Therefore for a normal, 2D graph it will be necessary to
instantiate two axis classes.

Data are carried around in QVariants.
Scalar values are floats.
Grid coordinates are floats, where 1 == a single grid unit.

== Type classes
Type classes are used to transform different types into a scalar
float type when no scaling is required.

Type classes need to be able to turn data into scalar values and back.

Scalar values should be suitable for creating trend lines from,
and fractions of a value should be dealt with properly
- i.e. the scalars are floats, not ints.

The structure of a type class should be as follows. Note that many
methods take a list, and do not allow a single value to be passed;
just do method([value])[0] for single values.
"""

type = {}
"""
QVariant.Type: Type class map
"""

class grid:
	"""
	Holds definitions for grid.major, grid.minor and grid.unit.
	"""
	major = 2
	minor = 1
	unit = 0

#===== Begin float Type classes

class float_type:

	@staticmethod
	def variant_to_scalar(data):
		"""
		Take a list of QVariants of the given type and transform it to
		a list of floats.

		For example, a date type could give the number of days since
		1900 for each date. A float type would just extract the float
		from the QVariant.
		"""
		# Could return map(QVariant.toDouble, data)
		# except that toDouble() returns a tuple (result, True)
		return zip(*map(QVariant.toDouble, data))[0]

	@staticmethod
	def scalar_to_variant(scalar):
		"""
		Take a list of floats and transform it to a list of QVariants
		of that type.

		This is the inverse of variant_to_scalar:
			scalar_to_data(data_to_scalar(data)) == data.
		"""
		return map(QVariant, scalar)

	@staticmethod
	def get_axis():
		"""
		Return an axis object of the relevant type.
		"""
		return float_axis()

	@staticmethod
	def get_editor_creator():
		"""
		Return a subclass of QItemEditorCreatorBase for the type.

		If the default creator should be used, store None.
		"""
		return float_editor_creator()

type[QVariant.Double] = float_type


class float_editor_creator(QItemEditorCreatorBase):
	"""
	A factory class that produces QWidgets that can edit the type.

	Subclasses QItemEditorCreatorBase so that it can be used for
	Qt Item Views.

	See also PyQt4.QtGui.QItemEditorCreatorBase
	and PyQt4.QtGui.QItemEditorFactory.
	In particular, the implementation of
		QDefaultItemEditorFactory::createEditor()
	(src/gui/itemviews/qitemeditorfactory.cpp in the Qt source)
	provides the default widgets created for the basic Qt types.
	"""

	def __init__(self):
		QItemEditorCreatorBase.__init__(self)

	def createWidget(self, qt_parent=None):
		"""
		Return an editor widget suitable for editing the data type.

		For example, for QDateTime return a QDateTimeEdit(parent)
		"""
		sb = QDoubleSpinBox(qt_parent)
		sb.setFrame(False)
		sb.setMinimum(-float_info.max)
		sb.setMaximum(float_info.max)
		return sb

	def valuePropertyName(self):
		"""
		Return the string of the main property name.

		For example, for QDateTime, return "dateTime".
		See the implementation of
			QDefaultItemEditorFactory::valuePropertyName()
		(src/gui/itemviews/qitemeditorfactory.cpp in the Qt source)
		for the property names of the basic Qt types.
		"""
		return "value"


class float_axis(axis_base):
	"""
	Handles the scales of an axis for a particular data type.

	Parameters:
		- length of the axis
		- values of all the lines
		- possible override of scale

	The changed() signal should be emitted whenever the
	axis is rescaled or the labels change,
	i.e. when the outside view of the axis changes, not
	the internal data.

	Scaling code should be able to handle:
		- no lines
		- lines with no data points
			- corollary: lines, but no points in any
	"""

	"""
	Handling possible scale override:

	if scale_auto == True:
		In the update_scales method, scale_start and scale_end are
		changed to their actual values.

		Trying to change scale_start or scale_end should therefore
		reset the values back to the automatic ones.
		Therefore the appropriate variable changed signal should be
		emitted to get the modifying editor widget to reset its value
		back to what it should be.
		However, the axis.changed signal should not be emitted, as the
		axis hasn't actually changed.
	
	if scale_auto == False:
		scale_start, scale_end are not modified by data updates
		or length updates.

		Setting scale_start or scale_end changes the axis:
		emit axis.changed in the update_scales method.

	Therefore:
		Don't directly connect the scale_*_changed signals to the
		axis.changed signal: emit it in the update_scales method
		and only if the scale have changed.
	"""

	length, length_changed = prop_sig(int, 'length')
	"Length of the axis in grid units (the small squares)"

	scale_auto, scale_auto_changed = prop_sig(bool, "scale_auto")
	"Automatically calculate scale_start and scale_end"
	# Next two written by _update_scales if scale_auto == True.
	scale_start, scale_start_changed = prop_sig(QVariant, "scale_start")
	"Value at start of axis"
	scale_end, scale_end_changed = prop_sig(QVariant, "scale_end")
	"Value at end of axis"

	changed = pyqtSignal()
	"""Emitted when the axis has changed.

	Note that changing a property of the axis might not cause the
	changed signal to be emitted; it is emitted only when the
	scale (or appearance) of the axis has changed.
	"""

	type = float_type
	"axis.type should always point back to the type class."
	editor_creator = 

	def __init__(self):
		QObject.__init__(self)

		# Stores the line data
		self.lines = {}

		# Written by _update_data, read by _update_scales
		self.max = None
		self.min = None
		# Used by _update_scales to detect change
		self.old_start = None
		self.old_end = None
		# Used by _update_scale to ignore changes in scale it did itself
		self.calculating_scale = False
		# Written by _update_scales, read by variant_to_coordinate,
		# scalar_to_coordinate and tick_info.
		self.scale = None

		for signal in (self.length_changed, self.scale_auto_changed,
				self.scale_start_changed, self.scale_end_changed):
			signal.connect(self._update_scale)

	def add_line(self, id, data):
		"""
		Update the axis about line addition.

		id should be a unique, immutable identifier of the line.
		I suggest id(line).
		"""
		self.lines[id] = map(QVariant.toDouble, data)
		self._update_data(id)

	def change_line(self, id, data):
		"""
		Update the axis about line data change.

		See add_line for notes.
		"""
		self.lines[id] = map(QVariant.toDouble, data)
		self._update_data(id)

	def remove_line(self, id):
		"""
		Update the axis about line removal.

		See add_line for notes.
		"""
		del self.lines[id]
		self._update_data(id)

	def variant_to_coordinates(self, data):
		"""
		Take a list of QVariants and return a list of axis
		coordinates.
		"""
	def scalar_to_coordinates(self, scalar):
		"""
		Take a list of scalar floats and return a list of axis
		coordinates.
		"""
	def tick_info(self):
		"""
		Returns an iterator or list of tuples describing each grid unit's
		ticks and text.

		The first item of the tuple describes the type of tick: either
		grid.major, grid.minor or grid.unit.

		The second item of the tuple is a string giving a representation
		of the value at that point. It should always be filled in;
		however, I will probably only print the string for major grid
		units.
		"""

	def _update_data(self, id):
		# Sanity check: if no lines, keep scale as-is until
		# one is added.
		if len(self.lines) == 0:
			return
		# Sanity check: if there are lines, but none with data
		# points, then the __update_* functions will store max/min
		# as None.

		oldmax = self.max
		oldmin = self.min

		self.__update_max()
		self.__update_min()

		# See if max/min has changed and update if so
		if oldmax != self.max or oldmin != self.min:
			self._update_scale()
			self.changed.emit()

#		Note: premature optimisation possible:
#		if the changed line is not the owner of max, then just
#		check that line for maxes rather than doing a full _update_max.
#		Same for min.
#		i.e.
#			if self.max is None or self.max_owner == id:
#				self._update_max()
#			else:
#				for value in self.lines[id]:
#					if value > self.max:
#						self.max = value
#						self.max_owner = id
#		rather than just _update_max().
#		Also need to add max_owner and min_owner to __init__
#		and _update_*.

	def __update_max(self):
		# Two-underscore prefix to signify not sanity-checked.
		max = None
		for line in self.lines.itervalue():
			for value in line:
				if max is None or value > max:
					max = value
		self.max = max

	def __update_min(self):
		min = None
		for line in self.lines.itervalues():
			for value in line:
				if min is None or value < min:
					min = value
		self.min = min

	def _update_scale(self):

		base = 10

		# Ignore signal if we set scale_start or scale_end ourselves
		if self.calculating_scale:
			return

		# Sanity check: check we have any lines
		if len(self.lines) == 0:
			return

		# Sanity check: if there are lines but no data points,
		# self.max and self.min will be None
		if self.max is None or self.min is None:
			return

		# Check if we have to calculate scale_start and scale_end
		if self.scale_auto:
			# Sets scale_start, scale_end and scale
			self.__autocalc_scale(base)
		else:
			# Calculate scale from assigned start and end values
			self.scale = (self.scale_end - self.scale_start) / self.length

		# Check if the start/end have changed during this calc
		if (self.scale_start != self.old_start or
			 self.scale_end != self.old_end):
			self.old_start = self.scale_start
			self.old_end = self.scale_end
			self.changed.emit()

	def __autocalc_scale(self, base):
		"""
		Scaling requirements:
		- The graph should use round units. By this I mean that a power
			of 10 multiplied by a factor of 10 should be used as the unit.
		- For each axis:
			- The lowest value should be as close to the origin as possible.
			- The highest value should be as high as possible; preferably
				in the top half of the axis.

		Solution:
		for increasing powers of 10:
			for multiplier = 1, 2, 2.5, 4, 5:
				axis start is min rounded down to
					nearest 10^(power+1) * multiplier
				scale is 10^power * multiplier
					(for small squares => *10 for big squares)
				find half of axis and top of axis
				if max is in top half of axis, stop
				else continue.
		
		Note that since our aim is the top _half_ of the axis, the
		multipliers need to be at most double the previous one.
		Also experiment with more multipliers than less for a better fit.

		If the multipliers are not all at most double the previous,
		nothing catastrophic will happen: the scale might be a bit
		too accommodating, though.

		Given scale/start:
			Use that as the temporary value for scale/start.
			It will be reassigned to itself each iteration.
			No guarantee that my algorithm will get the max value in
				the top half of the axis, so
				if we overshoot (max is above top of axis) then use
				the results from the previous iteration.
		
		C++ version of the algorithm worked backwards:
		for decreasing powers of 10:
			for multiplier = 5, 2, 1:
		"""
		# Start with same magnitude as the range.
		range = self.max - self.min
		power = math.floor(math.log(range, base))
		magnitude = base ** power

		multipliers = self.__get_scale_multipliers(base))

		# Heh heh
		ever = itertools.count()
		for ever in ever:
			for multiplier in multipliers:
				unit_scale = magnitude * multiplier
				start = self.__get_scale_start(unit_scale, base)
				halfway = start + (unit_scale * self.length / 2)
				end = start + (unit_scale * self.length)

				# See if scale contains the largest value
				if end > self.max:
					# Write scale_start, scale_end and scale
					self.scale_start = start
					self.scale_end = end
					self.scale = unit_scale
					return
			# Increase magnitude
			magnitude = magnitude * base

	def __get_scale_start(self, unit_scale, base):
		# Round self.min down to the nearest multiple of major_scale.
		major_scale = base * unit_scale
		return math.floor(self.min/major_scale) * major_scale

	def __get_scale_multipliers(self, base):
		"""
		Gets the factors of a number and adds extra numbers so that
		each number is no more than double the previous.
		
		If this doesn't work out, remove base argument and go back
		to using 10 as base and [1,2,5] as multipliers.
		"""
		multipliers = []
		for fact in self.__factor_positive_integer(base):
			if len(multipliers) == 0:
				# Initialise list
				multipliers.append(fact)
				continue
			while multipliers[-1]*2 < fact:
				multipliers.append(multipliers[-1]*2)
			multipliers.append(fact)
		return multipliers

	def __factor_positive_integer(self, number):
		"""
		Factorises a positive integer
		"""
		# Halfway needs to be a float as rounding may
		# introduce errors for small numbers.
		# Therefore can't use range() for iterating as that takes ints.
		halfway = number ** 0.5
		big_factors = []
		for factor in itertools.count(1):
			if factor > halfway:
				break
			if number % factor == 0:
				yield factor
				big_factor = number // factor
				if big_factor != factor:
					big_factors.insert(0, big_factor)
		for factor in big_factors:
			yield factor

