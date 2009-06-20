
# 0. Property syntax
class MyClass(object):
    def __init__(self):
        self._foo = "foo"
        self._bar = "bar"

    def foo():
        doc = "property foo's doc string"
        def fget(self):
            return self._foo
        def fset(self, value):
            self._foo = value
        def fdel(self):
            del self._foo
        return locals()  # credit: David Niergarth
    foo = property(**foo())

    def bar():
        doc = "bar is readonly"
        def fget(self):
            return self._bar
        return locals()    
    bar = property(**bar())

class Child(object):
	hello="hi"

c = MyClass()
c.foo = Child()
print c.foo.hello
# Prints "hi"

add_property(self, "style", "style_changed", default=Style())
"""Creates a python property with a PyQt changed signal"""
# Ideas: the only mutable thing is the self._foo property;
#        maybe use self.__getattr__("_" + str(id(doc))) instead?
#        Just has to be a unique string.
#        Problem is that identical strings have the same id,
#        so using doc="" (common!) will overwrite properties

# 1. Change code to emit a signal on change
def foo():
	doc = "property foo's doc string"
	def fget(self):
		return self._foo
	def fset(self, value):
		if self._foo != value:
			self._foo = value
			self._foo_changed.emit(value) #TODO
	def fdel(self):
		del self._foo
	return locals()
foo = property(**foo())

# 2. Parameters
# Member variable name is based off of name. It _should_ be unique-ish...
class sig(object): # Compatability class as Ubuntu uses PyQt 4.4. I'll move to Windows/PyQt4.5 soon.
	def emit(self, val):
		print "Signal reached (%s)" %val

def foo(name, doc=None):
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

class abject(object):
	def __init__(self):
		self._length = 1
	length_changed = sig()
	length = foo("length_changed")

class abject(object):
	length_changed = QtCore.pyqtSignal(int)
	length = foo("length_changed")

# TODO - automate initialisation somehow?
#      - make signal+property creation a single line?

# These next 2 might be useful.
# Import a class from a module name and a class name
def forname(modname, classname):
    module = __import__(modname)
    classobj = getattr(module, classname)
    return classobj

# Create an object from its class name
class_object = eval(classname)()
