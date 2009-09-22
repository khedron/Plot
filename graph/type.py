from PyQt4.QtCore import QObject

from base.property import prop_sig

# TODO - create working code

"""
Data are carried around in QVariants.
The type class needs to be able to turn data into scalar values,
which are represented as floats. Scalar values should be suitable
for creating trend lines from, and fractions of a value should
be dealt with properly.

The structure of a type class should be as follows. Note that all
methods should allow both a value and a list as a valid argument,
and test for each with isinstance().

class Type(QObject):

	def variant_to_scalar(data):
		Take a list of objects of the given type and transform it to a list of ints.
		For example, a date type could give the number of days since 1900 for each date.

	def scalar_to_variant(scalar):
		Take a list of ints and transform it to a list of objects of that type.
		This is the inverse of variant_to_scalar:
			scalar_to_data(data_to_scalar(data)) == data.

	def get_axis():
		Return an axis object of the relevant type.

class Axis(QObject):
	Handles the scales of an axis for a particular data type.
	Parameters:
		- length of the axs
		- values of all the lines
	The lines' data may be cached in a dictionary.

	length, length_changed = prop_sig(int, 'length')

	def add_line(

	def variant_to_coordinates(data):
		return coordinate_list
	def scalar_to_coordinates(scalar):
		return coordinate_list
	def labels():
		return [(major/minor/unit, str),...]
	type=Type()

"""
