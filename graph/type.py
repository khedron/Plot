from PyQt4.QtCore import QObject

from base.property import prop_sig

# TODO - create working code

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

Scalar values should be suitable for creating trend
lines from, and fractions of a value should be dealt with properly
- i.e. the scalars are floats, not ints.

The structure of a type class should be as follows. Note that many
methods take a list, and do not allow a single value to be passed;
just do method([value])[0] for single values.
"""

type = {}
"""
QVariant.Type: Type class map
"""
editor_creator = {}
"""
QVariant.Type: TypeEditorCreator class map

If the default creator should be used, store None.
"""

class grid:
	"""
	Holds definitions for grid.major, grid.minor and grid.unit.
	"""
	major = 2
	minor = 1
	unit = 0

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
	"""
	length, length_changed = prop_sig(int, 'length')

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
	scale_auto, scale_auto_changed = prop_sig(bool, "scale_auto")
	scale_start, scale_start_changed = prop_sig(QVariant, "scale_start")
	scale_end, scale_end_changed = prop_sig(QVariant, "scale_end")

	changed = pyqtSignal()

	type = float_type
	"axis.type should always point back to the type class."

	def __init__(self):
		QObject.__init__(self)
		self.lines = {}
		self.max = None
		self.min = None
		for signal in (self.length_changed, self.scale_auto_changed,
				self.scale_start_changed, self.scale_end_changed):
			signal.connect(self._update_scale)

	def add_line(self, id, data):
		"""
		Update the axis about line addition.

		id should be a unique, immutable identifier of the line.
		I suggest id(line).
		"""
		self.lines[id] = self.type.variant_to_scalar(data)
		self._update(id)

	def change_line(self, id, data):
		"""
		Update the axis about line data change.

		See add_line for notes.
		"""
		self.lines[id] = self.type.variant_to_scalar(data)
		self._update(id)

	def remove_line(self, id):
		"""
		Update the axis about line removal.

		See add_line for notes.
		"""
		del self.lines[id]
		self._update(id)

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

	def _update(self, id):
		oldmax = self.max
		oldmin = self.min

		self._update_max()
		self._update_min()
		if oldmax != self.max or oldmin != self.min:
			self._update_scale()
			self.changed.emit()

#		Note: prematurely optimisation possible:
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

	def _update_max(self):
		max = None
		for line in self.lines.itervalue():
			for value in line:
				if max is None or value > max:
					max = value
		self.max = max

	def _update_min(self):
		min = None
		for line in self.lines.itervalues():
			for value in line:
				if min is None or value < min:
					min = value
		self.min = min

	def _update_scale(self):
		# TODO
		# cache values at end of function;
		# then we can see which have changed.


class TypeEditorCreator(QItemEditorCreatorBase):
	def __init__(self):
		QItemEditorCreatorBase.__init__(self)

	def createWidget(self, parent=None):
		Returns an editor widget suitable for editing a data type.
		For example, for QDateTime return a QDateTimeEdit(parent)

	def valuePropertyName(self):
		Return the string of the main property name.
		For example, for QDateTime, return "dateTime"
