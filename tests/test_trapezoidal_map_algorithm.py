import unittest

from trapezoidal_map import TrapezoidalMap
from geometic_objects import Point, Segment, Trapezoid


class TestTrapezoidalMapAlgorithm(unittest.TestCase):
	def setUp(self) -> None:
		container_box = Trapezoid(Segment(Point(0, 0), Point(10, 0)), Segment(Point(0, 10), Point(10, 10)), Point(0, 0), Point(10, 0))
		self.trapezoidal_map = TrapezoidalMap(container_box=container_box)

	def test_searchDAG_structure(self):
		...

	def test_search(self):
		...

	def test_find_intersected_trapezoids(self):
		...

	def test_insert_segment(self):
		...

	def test_insert_segment_in_one_trapezoid(self):
		...

	def test_insert_segment_in_many_trapezoids(self):
		...



