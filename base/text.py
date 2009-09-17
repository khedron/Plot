from PyQt4.QtCore import QObject, pyqtSignal

from base.property import prop_sig
from style.textstyle import TextStyle

class Text(QObject):
	changed = pyqtSignal()
	text, text_changed = prop_sig(str, "text")
	style, style_changed = prop_sig(TextStyle, "style")

	def __init__(self, text = None, parent = None):
		QObject.__init__(self, parent)
		if text is not None:
			self.text = text
		for signal in self.style_changed, self.text_changed:
			signal.connect(self.changed)

