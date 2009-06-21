from PyQt4.QtCore import pyqtSignal, QObject

def prop(type, name, default, doc=None):
	sig = name + "_changed"
	mem = "_" + name
	def fget(self):
		try:
			self.__getattribute__(mem)
		except:
			self.__setattr__(mem, default)
		return self.__getattribute__(mem)
	def fset(self, value):
		if self.__getattribute__(mem) != value:
			self.__setattr__(mem, value)
			self.__getattribute__(sig).emit(value)
#	def fdel(self):
#		self.__delattr__(mem)
	return pyqtProperty(fget, fset, doc=doc), pyqtSignal(type)

def ro_prop(type, name, default, doc=None):
	mem = "_" + name
	def fget(self):
		try:
			self.__getattribute__(mem)
		except:
			self.__setattr__(mem, default)
		return self.__getattribute__(mem)
	return pyqtProperty(fget, doc=doc)

class abject(QObject):
	def __init__(self):
		QObject.__init__(self)
	length, length_changed = prop(int, "length", 1)

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
