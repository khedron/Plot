import sys, __builtin__

roll = []

class RollbackImporter:
	def __init__(self):
		"Creates an instance and installs as the global importer"
		self.previousModules = sys.modules.copy()
		self.realImport = __builtin__.__import__
		__builtin__.__import__ = self._import
		self.newModules = {}
		
#	def _import(self, name, globals=None, locals=None, fromlist=[], *args, **kwargs):
#		result = apply(self.realImport, (name, globals, locals, fromlist, *args, **kwargs))

	def _import(self, name, *args, **kwargs):
		result = self.realImport(name, *args, **kwargs)
		self.newModules[name] = 1
		return result
		
	def uninstall(self):
		for modname in self.newModules.keys():
			if not self.previousModules.has_key(modname):
				# Force reload when modname next imported
				del(sys.modules[modname])
		__builtin__.__import__ = self.realImport

def save_env():
	"""Save current module state (can be stacked)"""
	# Push importer onto stack
	roll.append(RollbackImporter())

def restore_env():
	"""Restore current module state (one-time - for stacked use)"""
	roll.pop().uninstall()

def reset_env():
	"""Restore current module state (multi-use - for non-stacked use)"""
	restore_env()
	save_env()

