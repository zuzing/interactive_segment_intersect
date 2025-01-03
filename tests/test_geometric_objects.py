import unittest

from geometic_objects import Point, Segment, Trapezoid


class TestGeometricObjects(unittest.TestCase):
	def setUp(self) -> None:
		self.segment = Segment(Point(0, 0), Point(10, 10))

	def test_y_coordinate_at(self):
		self.assertEqual(self.segment.y_coordinate_at(5), 5)

	def test_is_above_point(self):
		point = Point(5, 5)
		self.assertTrue(self.segment.is_above_point(point))

	def test_is_above_segment(self):
		other = Segment(Point(0, 5), Point(10, 5))
		self.assertTrue(self.segment.is_above_segment(other))

	def test_intersects(self):
		other = Segment(Point(5, 0), Point(5, 10))
		self.assertTrue(self.segment.intersects(other))