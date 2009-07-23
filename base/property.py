from PyQt4.QtCore import pyqtSignal, pyqtProperty, QObject

def get_fget(mem, type, default):
	def fget(self):
		try:
			self.__getattribute__(mem)
		except AttributeError:
			if default is None:
				self.__setattr__(mem, type())
			else:
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
		self.__setattr__(mem, value)
		self.__getattribute__(sig).emit(value)
	return fset

def prop_sig(type, name, default=None, doc=None):
	"""
	Creates a pyqtProperty/pyqtSignal pair from the given name and type.

	The signal is assumed to have the name of the property plus a "_changed"
	suffix; the member variable is stored as the name of the property.

	Example:
		class cls(object):
			length, length_changed = prop_sig(int, "length", 20)
	"""
	sig = name + "_changed"
	mem = "_" + name
	if default is None:
		default = type()
	fget = get_fget(mem, type, default)
	fset = get_fset(mem, type, sig)
# These make no sense as parameters
#	if fget is None:
#		fget = get_fget(mem, type, default)
#	if fset is None:
#		fset = get_fset(mem, type, sig)
#	def fdel(self):
#		self.__delattr__(mem)
	return pyqtProperty(type, fget, fset, doc=doc), pyqtSignal(type)


def ro_prop(type, name, default=None, fget=None, doc=None):
	mem = "_" + name
	if fget is None:
		fget = get_fget(mem, type, default)
	return pyqtProperty(type, fget, doc=doc)

def link(obj1, name1, obj2, name2):
	"""
	Links two pyqtProperty/pyqtSignal pairs together.

	Note that each object's setter must not emit the changed signal
	when set to its current value, or link() will cause infinite recursion.
	"""
	# Connect each other's change signals
	obj1.__getattr__(name1 + "_changed").connect(lambda x: obj2.__setattr__(name2, x))
	obj2.__getattr__(name2 + "_changed").connect(lambda x: obj1.__setattr__(name1, x))
	# Give both the value of the first
	obj2.__setattr__(name2, obj1.__getattr__(name1))

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
