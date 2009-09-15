from PyQt4.QtCore import pyqtSignal, pyqtProperty, QObject

def get_fget(mem, type, default):
	def fget(self):
		try:
			self.__getattribute__(mem)
		except AttributeError:
#			Need to have the behaviour that an unset default gives
#			no default value => don't special-case default==None.
			self.__setattr__(mem, default)
		return self.__getattribute__(mem)
	return fget

def get_fset(mem, type, sig):
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
		# Emit the filtered value, not the given value
		self.__getattribute__(sig).emit(self.__getattribute__(mem))
	return fset

def prop_sig(type, name, default=None, doc=None):
	"""
	Creates a pyqtProperty/pyqtSignal pair from the given name and type.

	The signal is assumed to have the name of the property plus a "_changed"
	suffix; the member variable is stored as the name of the property.

	Example:
		class cls(object):
			length, length_changed = prop_sig(int, "length", 20)
	
	The new method should take one argument, the object that is assigned
	to the property. It acts as a filter before the assigned object is
	actually set.

	The delete method should take one argument, the object that is
	to be deleted. It will be called on the property value when it is
	about to be replaced by another value.
	"""
	sig = name + "_changed"
	mem = "_" + name
	fget = get_fget(mem, type, default)
	fset = get_fset(mem, type, sig)
	return pyqtProperty(type, fget, fset, doc=doc), pyqtSignal(type)


def ro_prop(type, name, default=None, fget=None, doc=None):
	mem = "_" + name
	if fget is None:
		fget = get_fget(mem, type, default)
	return pyqtProperty(type, fget, doc=doc)

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
		def __init__(self):
			QObject.__init__(self)
		length, length_changed = prop(int, "length", 1)

		@staticmethod
		def p(x):
			print "Signal: ", x
	
	a = abject()
	print "length = 1"
	a.length = 1
	print "length = 2"
	a.length = 2

# TODO - automate initialisation somehow?
#      - make signal+property creation a single line?

# These next 2 might be useful.
# Import a class from a module name and a class name
def forname(modname, classname):
    module = __import__(modname)
    classobj = getattr(module, classname)
    return classobj

# Create an object from its class name
#class_object = eval(classname)()
