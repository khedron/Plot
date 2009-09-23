"http://lybniz2.sourceforge.net/safeeval.html"

from math import *
#make a list of safe functions 
safe_list = ['math','acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'degrees',
		'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log', 'log10',
		'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']
#use the list to filter the local namespace
safe_dict = dict([ (k, locals().get(k, None)) for k in safe_list ])
#add any needed builtins back in.
safe_dict['abs'] = abs 
eval("10*2", {"__builtins__":None}, safe_dict)


# For a complete (exploitable) REPL loop:

glo = {"__builtins__":__builtins__}
loc = { }

while True:
	line = rawinput('>>>')
	exec line in glo, loc

