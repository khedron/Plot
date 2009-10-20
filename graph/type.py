from __future__ import division

import math
import itertools
from sys import float_info

from PyQt4.QtCore import QObject, QVariant, pyqtSignal
from PyQt4.QtGui import QDoubleSpinBox, QItemEditorCreatorBase

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
	def variants_to_scalars(data):
		"""
		Take a list of QVariants of the given type and transform it to
		a list of floats.

		For example, a date type could give the number of days since
		1900 for each date. A float type would just extract the float
		from the QVariant.

		>>> a = map(QVariant, map(float, range(20)))
		>>> float_type.variants_to_scalars(a) #doctest: +ELLIPSIS
		(0.0, 1.0, 2.0, ..., 17.0, 18.0, 19.0)
		""" #+NORMALISE_WHITESPACE, - may be needed for doctest
		return map(float_type._variant_to_scalar, data)

	@staticmethod
	def scalars_to_variants(scalar):
		"""
		Take a list of floats and transform it to a list of QVariants
		of that type.

		This is the inverse of variants_to_scalars:
			scalar_to_data(data_to_scalar(data)) == data.

		>>> b = float_type.scalars_to_variants(map(float, range(30)))
		>>> float_type.variants_to_scalars(b) #doctest: +ELLIPSIS
		(0.0, 1.0, 2.0, 3.0, ..., 27.0, 28.0, 29.0)
		"""
		# Construct the QVariants from guaranteed floats
		return map(QVariant, map(float, scalar))

	@staticmethod
	def get_axis():
		"""
		Return an axis object of the relevant type.

		>>> float_type.get_axis() #doctest: +ELLIPSIS
		<graph.type.float_axis object at 0x...>
		"""
		return float_axis()

	@staticmethod
	def get_editor_creator():
		"""
		Return a subclass of QItemEditorCreatorBase for the type.

		If the default creator should be used, store None.

		>>> float_type.get_editor_creator() #doctest: +ELLIPSIS
		<graph.type.float_editor_creator object at 0x...>
		"""
		return float_editor_creator()

	@staticmethod
	def _variant_to_scalar(data):
		result, valid = QVariant.toDouble(data)
		if not valid:
			raise TypeError, "float_type.variant_to_scalar: QVariant expected"
		else:
			return result

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


class float_axis(QObject):
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
	
	>>> data = float_type.scalars_to_variants(map(float, range(20)))
	>>> axis = float_type.get_axis()
	>>> axis.scale_start.toDouble() # Scales are invalid as length == 0
	(0.0, False)
	>>> axis.scale_end.toDouble()
	(0.0, False)
	>>> axis.add_line(id(data), data)
	>>> axis.scale_start.toDouble() # Check scales are still invalid
	(0.0, False)
	>>> axis.scale_end.toDouble()
	(0.0, False)
	>>> axis.length = 20
	>>> axis.scale_start.toDouble() # Check scales are appropriate to length
	(0.0, True)
	>>> axis.scale_end.toDouble()
	(20.0, True)
	>>> axis.length = 120
	>>> axis.scale_start.toDouble()
	(0.0, True)
	>>> axis.scale_end.toDouble()
	(24.0, True)
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

	scale_auto, scale_auto_changed = prop_sig(bool, "scale_auto", True)
	"Automatically calculate scale_start and scale_end"

	# Next two written by _update_scales if scale_auto == True.
	scale_start, scale_start_changed = prop_sig(QVariant, "scale_start")
	"""Value at start of axis
	
	This can be set if scale_auto is set to False.
	Otherwise, a changed value will be changed back.
	"""
	scale_end, scale_end_changed = prop_sig(QVariant, "scale_end")
	"""Value at end of axis
	
	This can be set if scale_auto is set to False.
	Otherwise, a changed value will be changed back.
	"""

	changed = pyqtSignal()
	"""Emitted when the axis has changed.

	Note that changing a property of the axis might not cause the
	changed signal to be emitted; it is emitted only when the
	scale (or appearance) of the axis has changed.
	"""

	type = float_type
	"axis.type should always point back to the type class."

	def __init__(self):
		QObject.__init__(self)

		# Stores the line data
		self.lines = {}

		# Written by _update_data, read by _update_scales
		# None indicates no points (or no lines): in combination
		# with scale_auto == True, this causes an invalid scale.
		self.max = None
		self.min = None
		# Used by _update_scales to detect change
		self.old_start = None
		self.old_end = None
		# Used by _update_scale to ignore changes in scale it did itself
		self.calculating_scale = False
		# Written by _update_scales, read by variant_to_coordinate,
		# scalar_to_coordinate and tick_info.
		# None indicates an invalid scale: that scale_auto==True
		# and we have no points.
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
		self.lines[id] = self.__variants_to_floats(data)
		self._update_data(id)

	def change_line(self, id, data):
		"""
		Update the axis about line data change.

		See add_line for notes.
		"""
		self.lines[id] = self.__variants_to_floats(data)
		self._update_data(id)

	def remove_line(self, id):
		"""
		Update the axis about line removal.

		See add_line for notes.
		"""
		del self.lines[id]
		self._update_data(id)

	def line_to_coordinates(self, id):
		"""
		Take a line id and return a list of axis coordinates.

		The line must have previously been added to the axis.
		"""
		return _floats_to_coordinates(self, self.lines[id])

	def variants_to_coordinates(self, data):
		"""
		Take a list of QVariants and return a list of axis
		coordinates.

		If the scales are invalid, then this function returns
		an empty list.

		Scales are invalid if scale_auto is True (default) and
		there are no points (either because no lines have been
		added, or because all the lines have no points).
		"""
		# If scales are invalid, this call returns an empty list.
		return _floats_to_coordinates(self, self.__variants_to_floats(data))

	def scalars_to_coordinates(self, scalar):
		"""
		Take a list of scalar floats and return a list of axis
		coordinates.

		If the scales are invalid, then this function returns
		an empty list.

		Scales are invalid if scale_auto is True (default) and
		there are no points (either because no lines have been
		added, or because all the lines have no points).
		"""
		# To be type-correct, instead of scalar, say
		# self.__variants_to_floats(self.type.scalars_to_variants(scalar))

		# If scales are invalid, this call returns an empty list.
		return _floats_to_coordinates(self, scalar)

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

		If the scales are invalid, the tick type will always be filled in,
		but the value string may be an empty string.
		"""
		base = 10
		minor_base = 5
		for i in range(self.length + 1):
			if i % base == 0:
				tick = grid.major
			elif i % minor_base == 0:
				tick = grid.minor
			else:
				tick = grid.unit
			# floats = units * floats/unit
			#        = units * scale
			# ...and adjust for start
			string = str(self.__coordinate_to_float(i))
			yield tick, string

	#### Start private functions
	# Some parameter checking is to be expected.

	def _update_data(self, id):
		# Sanity check: if no lines, or there are lines, but none with
		# data points, then the __update_* functions will store max/min
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

	def _update_scale(self):

		base = 10

		# Ignore signal if we set scale_start or scale_end ourselves
		if self.calculating_scale:
			return

		# Check if we have to calculate scale_start and scale_end
		if self.scale_auto:
			# Sets scale_start, scale_end and scale
			self._autocalc_scale(base)
		else:
			# Calculate scale from assigned start and end values
			self.scale = (self.scale_end - self.scale_start) / self.length

		# Check if the start/end have changed during this calc
		if (self.scale_start != self.old_start or
			 self.scale_end != self.old_end):
			self.old_start = self.scale_start
			self.old_end = self.scale_end
			self.changed.emit()

	def _autocalc_scale(self, base):
		"""
		Scaling requirements:
		- The graph should use round units. By this I mean that a power
			of 10 multiplied by a factor of 10 should be used as the unit.
		- For each axis:
			- The lowest value should be as close to the origin as possible.
			- The highest value should be as high as possible; preferably
				in the top half of the axis.

		Solution:
		start with power of 10 below range/axis_length
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
		# Sanity checks

		# Check we have any lines.
		# Set scale to None to imply an invalid scale.
		if len(self.lines) == 0:
			self.scale = None
			return

		# If there are lines but no data points,
		# self.max and self.min will be None.
		if self.max is None:
			self.scale = None
			return

		# If axis length is unset, we can't calculate scales.
		if self.length < 1:
			self.scale = None
			return

		# We're gonna have problems if we only have one point!
		# We could return an invalid scale, but we can
		# work out start and fudge scale instead.
		if self.max == self.min:
			# Set one of them to 0 or, failing that, 1.
			if self.min == 0:
				self.max = 1
			elif self.min > 0:
				self.min = 0
			else:
				self.max = 0

		# Start with power of 10 below range/length
		range = self.max - self.min
		unit_range = range/self.length
		magnitude = base ** math.floor(math.log(unit_range, base))

		multipliers = self.__get_scale_multipliers(base)

		# Heh heh pun
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
					self.scale_start = QVariant(start)
					self.scale_end = QVariant(end)
					self.scale = unit_scale
					return
			# Increase magnitude
			magnitude = magnitude * base

	def _floats_to_coordinates(self, floats):
		"""Returns a list, not an iterator."""
		# If scale is invalid, return an empty list
		if self.scale is None:
			return []
		return [self.__float_to_coordinate(x) for x in floats]

	##### Start private, unchecked functions.
	# We assume that the parameters are correct.

	def __update_max(self):
		max = None
		for line in self.lines.itervalues():
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

	def __variants_to_floats(self, variants):
		# Due to definition of scalar for float type
		return self.type.variants_to_scalars(variants)

	def __coordinate_to_float(self, coord):
		# floats = units * floats/unit + start
		#        = units * scale       + start
		return self.scale_start + (coord * self.scale)

	def __float_to_coordinate(self, value):
		# Inverse of __cooordinate_to_float
		return (value - self.scale_start) / self.scale

if __name__ == "__main__":
	import doctest
	doctest.testmod()
