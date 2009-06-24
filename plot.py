import pdb
#pdb.set_trace()
from PyQt4.QtGui import QApplication, QGraphicsScene, QGraphicsTextItem, QGraphicsView
from PyQt4.QtCore import QPointF

from graph.plotter import Plotter
from graph.graph import Graph

def main1():
	import sys
	app = QApplication(sys.argv)
	graph = Graph()
	plot = Plotter()
	graph.draw(plot)
	view = QGraphicsView(plot.scene)
	view.scale(3,3)
	view.show()

	sys.exit(app.exec_())

def main2():
	import sys
	app = QApplication(sys.argv)
	scene = QGraphicsScene()
	text = QGraphicsTextItem(None, scene)
	text.setHtml("<h2 align=\"center\">hello</h2><h2 align=\"center\">world 12334345354444444444444444444444444</h2>123");
	text.setPos(QPointF(25,25))
	view = QGraphicsView(scene)
	view.show()

#    QTextEdit te;
#    te.setHtml("<h2 align=\"center\">hello</h2><h2 align=\"center\">world 12334345354444444444444444444444444</h2>123");
#    te.show();
	sys.exit(app.exec_())

if __name__ == "__main__":
	main1()
