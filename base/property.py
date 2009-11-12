from exceptions import Exception

from PyQt4.QtCore import pyqtSignal, pyqtProperty, QObject, QString

"""
pyqtSignal and pyqtProperty convenience functions.

These functions try to simplify signal/property pair creation and linking.
They are intended to be used like so:

	class Person(QObject):
		changed = pyqtSignal()

		# name defaults to "Joe Bloggs"
		name, name_changed = prop_sig(str, "name", "Joe Bloggs")
		# age defaults to int(), i.e. 0
		age, age_changed = prop_sig(int, "age")
		# <var>, <var>_changed = prop_sig(<type>, <var-as-string>,[<default>])

		def __init__(self):
			QObject.__init__(self)
			for signal in self.name_changed, self.age_changed, self.<var>_changed:
				signal.connect(self.changed)

This code creates a Person class with two properties: name and age. When these
properties are changed, they emit the name_changed and age_changed signals,
respectively.

These signals need to be manually connected up to the class's changed() signal.
This is because if a containing class defines a Person property/signal pair
with prop_sig(), then prop_sig() will try to connect this changed() signal to
the relevant <var>_changed property of the containing class.

For example:

	class Car(QObject):
		changed= pyqtSignal()

		driver, driver_changed = prop_sig(Person, "driver")

		def __init__(self):
			QObject.__init__(self)
			driver_changed.connect(self.changed)
	
	car = Car()
	car.driver.age = 20

The following signals will be emitted after the last line:
	car.driver.age_changed(20)
	car.driver.changed()
	car.driver_changed(driver)
	car.changed()
"""

def try_connect_signals(self, mem, sig):
	"""Private!!"""
	"""
	Try to connect the changed() signal of an inner class to the *_changed() signal of the outer class.

	BUG: we don't store the lambda function, so there's no way of disconnecting the signal
	when the object is replaced. A change to the previous object would then trigger the *_changed()
	signal of the outer class.

	This bug is not too bad, since overemitting *_changed() shouldn't change behaviour.
	"""
	try:
		self.__getattribute__(mem).changed.connect(
				lambda: self.__getattribute__(sig).emit(self.__getattribute__(mem)))
	except AttributeError:
		# Ignore if member doesn't have a changed() signal
		pass

def get_fget(mem, type, sig, default):
	"""Private!!"""
	def fget(self):
		try:
			self.__getattribute__(mem)
		except AttributeError:
			# Need to have the behaviour that an unset default gives
			# a default value => special-case default==None.
			if default is None:
				self.__setattr__(mem, type())
			else:
				self.__setattr__(mem, default)
			try_connect_signals(self, mem, sig)
		return self.__getattribute__(mem)
	return fget

def get_fset(mem, type, sig):
	"""Private!!"""
	def fset(self, value):
		try:
			if self.__getattribute__(mem) == value:
				return
		except AttributeError:
			# First time, set the value
			pass
		# delete() equivalent here if needed
		# Filter value through new() here if needed
		self.__setattr__(mem, value)
		try_connect_signals(self, mem, sig)
		# Emit the filtered value, not the given value
		self.__getattribute__(sig).emit(self.__getattribute__(mem))
	return fset

class PropertyException(Exception):
	pass

def prop_sig(type, name, default=None, doc=None):
	"""
	Creates a pyqtProperty/pyqtSignal pair from the given name and type.

	The signal is assumed to have the name of the property plus a "_changed"
	suffix; the member variable is stored as the name of the property.

	Example:
		class cls(object):
			length, length_changed = prop_sig(int, "length", 20)
	"""
#	"""
#	The new method should take one argument, the object that is assigned
#	to the property. It acts as a filter before the assigned object is
#	actually set.
#
#	The delete method should take one argument, the object that is
#	to be deleted. It will be called on the property value when it is
#	about to be replaced by another value.
#	"""
	sig = name + "_changed"
	mem = "_" + name
	# Make sure that the type passed in was a python class, not
	# a C++ type-string.
	if (isinstance(type, basestring) or isinstance(type, QString)
			) and default is None:
		raise PropertyException, "must give a default when type is a C++ type-string"

	fget = get_fget(mem, type, sig, default)
	fset = get_fset(mem, type, sig)
	return pyqtProperty(type, fget, fset, doc=doc), pyqtSignal(type)


def get_property_value(obj, prop_name):
	return type(obj).__dict__[prop_name].__get__(obj, type(obj))

def set_property_value(obj, prop_name, value):
	type(obj).__dict__[prop_name].__set__(obj, value)
	return None

def link(obj1, name1, obj2, name2):
	"""
	Links two pyqtProperty/pyqtSignal pairs together.

	Note that each object's setter must not emit the changed signal
	when set to its current value, or link() will cause infinite recursion.
	"""
	# Connect each other's change signals
	obj1.__getattribute__(name1 + "_changed").connect(lambda x: set_property_value(obj2, name2, x))
	obj2.__getattribute__(name2 + "_changed").connect(lambda x: set_property_value(obj1, name1, x))
	# Give both the value of the first
	set_property_value(obj2, name2, get_property_value(obj1, name1))

if __name__ == "__main__":
	class abject(QObject):

		length, length_changed = prop(int, "length", 1)

		def __init__(self):
			QObject.__init__(self)
			self.length_changed.connect(self.p)

		@staticmethod
		def p(x):
			print "Signal: ", x
	
	a = abject()
	print "length = 1"
	a.length = 1
	print "length = 2"
	a.length = 2

# These next 2 might be useful.
# Import a class from a module name and a class name
def forname(modname, classname):
    module = __import__(modname)
    classobj = getattr(module, classname)
    return classobj

# Create an object from its class name
#class_object = eval(classname)()
