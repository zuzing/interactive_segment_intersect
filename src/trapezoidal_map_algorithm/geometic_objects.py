from dataclasses import dataclass, field
import numpy as np


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass
class Segment:
    start: Point
    end: Point
    a: float = field(init=False)
    b: float = field(init=False)


    def __post_init__(self):
        if self.start.x > self.end.x:
            self.start, self.end = self.end, self.start
        self.a = (self.end.y - self.start.y) / (self.end.x - self.start.x)
        self.b = self.start.y - (self.a * self.start.x)

    def y_coordinate_at(self, x: float) -> float:
        return self.a * x + self.b

    def is_above_point(self, point: Point) -> bool:
        return self.y_coordinate_at(point.x) > point.y

    def is_above_segment(self, other: 'Segment') -> bool:  # self and other have to share start point
        if self.start != other.start:
            raise ValueError("Segments do not share the same start point.")
        else:
            return self.a > other.a

    def intersects(self, other: 'Segment') -> bool:
        if self.a == other.a and self.b == other.b:
            return False

        if self.a == float('inf') and other.a == float('inf'):
            return self.start.x == other.start.x

        if self.a == float('inf'):
            x_intersect = self.start.x
            y_intersect = other.a * x_intersect + other.b
        elif other.a == float('inf'):
            x_intersect = other.start.x
            y_intersect = self.a * x_intersect + self.b
        else:
            if self.a == other.a:
                return False
            x_intersect = (other.b - self.b) / (self.a - other.a)
            y_intersect = self.a * x_intersect + self.b

        return (min(self.start.x, self.end.x) <= x_intersect <= max(self.start.x, self.end.x)) and \
               (min(self.start.y, self.end.y) <= y_intersect <= max(self.start.y, self.end.y)) and \
               (min(other.start.x, other.end.x) <= x_intersect <= max(other.start.x, other.end.x)) and \
               (min(other.start.y, other.end.y) <= y_intersect <= max(other.start.y, other.end.y))

    def near_start(self) -> Point:
        length = distance(self.start, self.end)
        multiplier = 10 ** -6
        vector_x, vector_y = (self.end.x - self.start.x, self.end.y - self.start.y)
        return Point(self.start.x + multiplier * length * vector_x, self.start.y + multiplier * length * vector_y)

    def near_end(self) -> Point:
        length = distance(self.start, self.end)
        multiplier = 10 ** -6
        vector_x, vector_y = (self.end.x - self.start.x, self.end.y - self.start.y)
        return Point(self.end.x - multiplier * length * vector_x, self.end.y - multiplier * length * vector_y)



class Trapezoid:
    def __init__(self, top_segment: Segment, bottom_segment: Segment, left_point: Point, right_point: Point | None):
        self.top_segment = top_segment
        self.bottom_segment = bottom_segment
        self.left_point = left_point
        self.right_point = right_point

        self.top_left_neighbour: Trapezoid | None = None
        self.bottom_left_neighbour: Trapezoid | None = None
        self.top_right_neighbour: Trapezoid | None = None
        self.bottom_right_neighbour: Trapezoid | None = None

    valid_keys = ['top_left_neighbour', 'bottom_left_neighbour', 'top_right_neighbour', 'bottom_right_neighbour',]

    def set_neighbours(self, **kwargs):
        for key, item in kwargs.items():
            if key in self.valid_keys:
                setattr(self, key, item)
            elif key == 'KEEP_THE_SAME':
                continue
            else:
                raise ValueError(f"Invalid neighbour key: {key}. Valid keys are: {self.valid_keys}")

    def __eq__(self, other):
        if not isinstance(other, Trapezoid):
            return False
        return self.top_segment == other.top_segment and self.bottom_segment == other.bottom_segment and \
               self.left_point == other.left_point and self.right_point == other.right_point

    def __hash__(self):
        return hash((self.top_segment, self.bottom_segment, self.left_point, self.right_point))




def distance(a: Point, b: Point) -> float:
    return np.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)
