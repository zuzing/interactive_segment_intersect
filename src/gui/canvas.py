from IPython.external.qt_for_kernel import QtGui, QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QPainter, QPen, QColor, QPainterPath, QPolygonF
from PyQt6.QtWidgets import (
	QMainWindow,
	QApplication,
	QGraphicsEllipseItem,
	QGraphicsItem,
	QGraphicsRectItem,
	QGraphicsScene,
	QGraphicsView,
	QHBoxLayout,
	QPushButton,
	QSlider,
	QVBoxLayout,
	QWidget, QGraphicsProxyWidget, QLabel, QSizePolicy,
)


class Segment(QWidget):
	def __init__(self, canvas, start, end):
		super().__init__(canvas)
		self.canvas = canvas
		self.start = start
		self.end = end

		self.show()

	def move_end(self, x, y):
		self.end.move(x, y)
		#self.update()

	def paintEvent(self, e):
		if self.start != self.end:
			print("paint event finished")


class Point(QWidget):
	def __init__(self, canvas, x, y):
		super().__init__(canvas)
		self.canvas = canvas
		self.x = x
		self.y = y

		self.show()
		self.setGeometry(x, y, 10, 10)

	def __eq__(self, other):
		return self.x == other.x and self.y == other.y

	def move(self, x, y):
		self.x = x
		self.y = y
		super().move(x, y)

	def paintEvent(self, e):
		painter = QtGui.QPainter(self)
		brush = QtGui.QBrush(QtGui.QColor('blue'))
		painter.setBrush(brush)
		painter.drawEllipse(0, 0, 10, 10)

	def mousePressEvent(self, e):
		print("point clicked")
		self.canvas.start_segment(self)

	def copy(self):
		return Point(self.canvas, self.x, self.y)

	def mouseReleaseEvent(self, e):
		print("point released")
		self.canvas.finish_segment()

	def enterEvent(self, e):
		pass


class Canvas(QWidget):
	def __init__(self, window=None):
		super().__init__(window)
		self.setGeometry(0, 0, 400, 400)
		self.iter = 0
		self.unfinished_segment = None

	def add_point(self, x, y):
		return Point(self, x, y)

	def mousePressEvent(self, e):
		x, y = e.pos().x(), e.pos().y()
		self.add_point(x, y)
		print(f"Point {self.iter} created")
		self.iter += 1

	def start_segment(self, start_point):
		print("segment started")
		end_point = start_point.copy()
		self.unfinished_segment = Segment(self, start_point, end_point)

	def mouseMoveEvent(self, e):
		if self.unfinished_segment:
			x, y = e.pos().x(), e.pos().y()
			self.unfinished_segment.move_end(x, y)

	def finish_segment(self):
		print("segment finished")
		if self.unfinished_segment.start != self.unfinished_segment.end:
			self.unfinished_segment.update()
			self.unfinished_segment = None


app = QApplication([])
d = Canvas()
d.show()
app.exec()
