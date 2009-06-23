from PyQt4.QtCore import pyqtSignal, QObject

def prop_sig(type, name, default=None, fget=None, fset=None, doc=None):
	sig = name + "_changed"
	mem = "_" + name
	if default is None:
		default = type()
	if fget is None:
		def fget(self):
			try:
				self.__getattribute__(mem)
			except:
				self.__setattr__(mem, type(default))
			return self.__getattribute__(mem)
	if fset is None:
		def fset(self, value):
			if self.__getattribute__(mem) != value:
				self.__setattr__(mem, type(value))
				self.__getattribute__(sig).emit(value)
#	def fdel(self):
#		self.__delattr__(mem)
	return pyqtProperty(fget, fset, doc=doc), pyqtSignal(type)


def ro_prop(type, name, default, fget=None, doc=None):
	mem = "_" + name
	if fget is None:
		def fget(self):
			try:
				self.__getattribute__(mem)
			except:
				self.__setattr__(mem, default)
			return self.__getattribute__(mem)
	return pyqtProperty(fget, doc=doc)

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
