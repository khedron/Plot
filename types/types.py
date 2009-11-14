
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

class Type:
	pass

types = {}
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

