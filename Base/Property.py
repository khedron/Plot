from PyQt4.QtCore import pyqtSignal, QObject

def prop(name, doc=None):
	sig = name + "_changed"
	mem = "_" + name
	def fget(self):
		return self.__getattribute__(mem)
	def fset(self, value):
		if self.__getattribute__(mem) != value:
			self.__setattr__(mem, value)
			self.__getattribute__(sig).emit(value)
	def fdel(self):
		self.__delattr__(mem)
	return property(fget, fset, fdel, doc=doc)

class abject(QObject):
	def __init__(self):
		QObject.__init__(self)
		self._length = 1
	length_changed = pyqtSignal(int)
	length = prop("length")

	@staticmethod
	def p(x):
		print "Signal: ", x

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
