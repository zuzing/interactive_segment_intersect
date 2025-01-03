import random

from geometic_objects import Point, Segment, Trapezoid
from search_structure import Node, Xnode, Ynode, Leafnode, SearchDAG


def check_for_intersection(segments):
	pass


class TrapezoidalMap:
	def __init__(self, *, container_box: Trapezoid = None, search_DAG: SearchDAG = None):
		self.trapezoids_to_nodes: dict[Trapezoid, Leafnode] = {}

		if container_box and search_DAG:
			raise ValueError("Only one of 'container_box' or 'search_DAG' should be provided, not both.")
		elif not container_box and not search_DAG:
			raise ValueError("One of 'container_box' or 'search_DAG' must be provided.")

		if container_box and not search_DAG:
			self.container_box = container_box
			root_node = self.create_leafnode(trapezoid=container_box)
			self.search_structure = SearchDAG(root_node)
		elif search_DAG and not container_box:
			self.search_structure = search_DAG
			self.container_box = search_DAG.root.trapezoid

	def add_segments(self, segments, shuffle_=True):
		self._build_searchDAG(segments, shuffle_)


	def create_leafnode(self, trapezoid: Trapezoid) -> Leafnode:
		leafnode = Leafnode(trapezoid)
		self.trapezoids_to_nodes[trapezoid] = leafnode
		return leafnode

	def _build_searchDAG(self, segments, shuffle_=True):
		"""
		Search DAG is updated with the new segments. This function loops through all segments and inserts them into the
		trapezoidal map by updating the search DAG.
		"""
		def update_left_neighbours(previous_trapezoid, new_trapezoid):
			if previous_trapezoid.top_left_neighbour is not None:
				if previous_trapezoid.top_left_neighbour.top_right_neighbour == previous_trapezoid:
					previous_trapezoid.top_left_neighbour.set_neighbours(top_right_neighbour=new_trapezoid)
				if previous_trapezoid.top_left_neighbour.bottom_right_neighbour == previous_trapezoid:
					previous_trapezoid.top_left_neighbour.set_neigbhbours(bottom_right_neighbour=new_trapezoid)
			if previous_trapezoid.bottom_left_neighbour is not None:
				if previous_trapezoid.bottom_left_neighbour.top_right_neighbour == previous_trapezoid:
					previous_trapezoid.bottom_left_neighbour.set_neighbours(top_right_neighbour=new_trapezoid)
				if previous_trapezoid.bottom_left_neighbour.bottom_right_neighbour == previous_trapezoid:
					previous_trapezoid.bottom_left_neighbour.set_neighbours(bottom_right_neighbour=new_trapezoid)

		def update_right_neighbours(previous_trapezoid, new_trapezoid):
			if previous_trapezoid.top_right_neighbour is not None:
				if previous_trapezoid.top_right_neighbour.top_left_neighbour == previous_trapezoid:
					previous_trapezoid.top_right_neighbour.set_neighbours(top_left_neighbour=new_trapezoid)
				if previous_trapezoid.top_right_neighbour.bottom_left_neighbour == previous_trapezoid:
					previous_trapezoid.top_right_neighbour.set_neighbours(bottom_left_neighbour=new_trapezoid)
			if previous_trapezoid.bottom_right_neighbour is not None:
				if previous_trapezoid.bottom_right_neighbour.top_left_neighbour == previous_trapezoid:
					previous_trapezoid.bottom_right_neighbour.set_neighbours(top_left_neighbour=new_trapezoid)
				if previous_trapezoid.bottom_right_neighbour.bottom_left_neighbour == previous_trapezoid:
					previous_trapezoid.bottom_right_neighbour.set_neighbours(bottom_left_neighbour=new_trapezoid)

		def insert_segment_in_one_trapezoid(trapezoid: Trapezoid, segment: Segment):
			left_trapezoid = Trapezoid(top_segment=trapezoid.top_segment, bottom_segment=trapezoid.bottom_segment,
									   left_point=trapezoid.left_point, right_point=segment.start)
			top_trapezoid = Trapezoid(top_segment=trapezoid.top_segment, bottom_segment=segment,
									  left_point=segment.start, right_point=segment.end)
			bottom_trapezoid = Trapezoid(top_segment=segment, bottom_segment=trapezoid.bottom_segment,
										 left_point=segment.start, right_point=segment.end)
			right_trapezoid = Trapezoid(top_segment=trapezoid.top_segment, bottom_segment=trapezoid.bottom_segment,
										left_point=segment.end, right_point=trapezoid.right_point)

			left_trapezoid.set_neighbours(
				top_left_neighbour=trapezoid.top_left_neighbour,
				bottom_left_neighbour=trapezoid.bottom_left_neighbour,
				top_right_neighbour=top_trapezoid,
				bottom_right_neighbour=bottom_trapezoid
			)

			top_trapezoid.set_neighbours(
				top_left_neighbour=left_trapezoid,
				bottom_left_neighbour=left_trapezoid,
				top_right_neighbour=right_trapezoid,
				bottom_right_neighbour=right_trapezoid
			)

			bottom_trapezoid.set_neighbours(
				top_left_neighbour=left_trapezoid,
				bottom_left_neighbour=left_trapezoid,
				top_right_neighbour=right_trapezoid,
				bottom_right_neighbour=right_trapezoid
			)

			right_trapezoid.set_neighbours(
				top_left_neighbour=top_trapezoid,
				bottom_left_neighbour=bottom_trapezoid,
				top_right_neighbour=trapezoid.top_right_neighbour,
				bottom_right_neighbour=trapezoid.bottom_right_neighbour
			)

			update_left_neighbours(trapezoid, left_trapezoid)
			update_right_neighbours(trapezoid, right_trapezoid)

			left_trapezoid_node = self.create_leafnode(trapezoid=left_trapezoid)
			top_trapezoid_node = self.create_leafnode(trapezoid=top_trapezoid)
			bottom_trapezoid_node = self.create_leafnode(trapezoid=bottom_trapezoid)
			right_trapezoid_node = self.create_leafnode(trapezoid=right_trapezoid)

			sNode = Ynode(right=top_trapezoid_node, left=bottom_trapezoid_node, segment=segment)
			qNode = Xnode(right=right_trapezoid_node, left=sNode, point=segment.end)
			pNode = Xnode(right=qNode, left=left_trapezoid_node, point=segment.start)

			self.search_structure.replace_leafnode(self.trapezoids_to_nodes[trapezoid], pNode)

		def insert_segment_in_multiple_trapezoids(trapezoids, segment):
			upperUNKNOWN: bool
			UNKNOWN = None  # keyword for unknown right point

			for trapezoid in trapezoids:

				if trapezoid == trapezoids[0]:
					left_trapezoid = Trapezoid(top_segment=trapezoid.top_segment, bottom_segment=trapezoid.bottom_segment, left_point=trapezoid.left_point, right_point=segment.start)

					if segment.is_above_point(trapezoid.right_point):
						mid_top_trapezoid = Trapezoid(top_segment=trapezoid.top_segment, bottom_segment=segment, left_point=segment.start, right_point=UNKNOWN)
						mid_bottom_trapezoid = Trapezoid(top_segment=segment, bottom_segment=trapezoid.bottom_segment, left_point=segment.start, right_point=trapezoid.right_point)
						upperUNKNOWN = True
					else:
						mid_top_trapezoid = Trapezoid(top_segment=trapezoid.top_segment, bottom_segment=segment, left_point=segment.start, right_point=trapezoid.right_point)
						mid_bottom_trapezoid = Trapezoid(top_segment=segment, bottom_segment=trapezoid.bottom_segment, left_point=segment.start, right_point=UNKNOWN)
						upperUNKNOWN = False

					left_trapezoid.set_neighbours(
						top_left_neighbour=trapezoid.top_left_neighbour,
						bottom_left_neighbour=trapezoid.bottom_left_neighbour,
						top_right_neighbour=mid_top_trapezoid,
						bottom_right_neighbour=mid_bottom_trapezoid
					)

					mid_top_trapezoid.set_neighbours(
						top_left_neighbour=left_trapezoid,
						bottom_left_neighbour=left_trapezoid,
						top_right_neighbour=trapezoid.top_right_neighbour if upperUNKNOWN else trapezoid.top_right_neighbour,
						bottom_right_neighbour=trapezoid.bottom_right_neighbour if upperUNKNOWN else trapezoid.bottom_right_neighbour
					)

					mid_bottom_trapezoid.set_neighbours(
						top_left_neighbour=left_trapezoid,
						bottom_left_neighbour=left_trapezoid,
						top_right_neighbour=trapezoid.top_right_neighbour if upperUNKNOWN else trapezoid.top_right_neighbour,
						bottom_right_neighbour=trapezoid.bottom_right_neighbour if upperUNKNOWN else trapezoid.bottom_right_neighbour
					)

					update_left_neighbours(trapezoid, left_trapezoid)

					if upperUNKNOWN:
						update_right_neighbours(trapezoid, mid_bottom_trapezoid)
					else:
						update_right_neighbours(trapezoid, mid_top_trapezoid)


					left_trapezoid_node = self.create_leafnode(trapezoid=left_trapezoid)
					mid_top_trapezoid_node = self.create_leafnode(trapezoid=mid_top_trapezoid)
					mid_bottom_trapezoid_node = self.create_leafnode(trapezoid=mid_bottom_trapezoid)

					sNode = Ynode(right=mid_top_trapezoid_node, left=mid_bottom_trapezoid_node, segment=segment)
					pNode = Xnode(right=sNode, left=left_trapezoid_node, point=segment.start)

					self.search_structure.replace_leafnode(self.trapezoids_to_nodes[trapezoid] ,pNode)

				elif trapezoid == trapezoids[-1]:

					right_trapezoid = Trapezoid(top_segment=trapezoid.top_segment, bottom_segment=trapezoid.bottom_segment, left_point=segment.end, right_point=trapezoid.right_point)
					if upperUNKNOWN:
						mid_top_trapezoid.right_point = segment.end  # ends upper trapezoid
						mid_bottom_trapezoid = Trapezoid(top_segment=segment, bottom_segment=trapezoid.bottom_segment, left_point=trapezoid.left_point, right_point=segment.end)
						self.create_leafnode(trapezoid=mid_bottom_trapezoid)
					else:
						mid_bottom_trapezoid.right_point = segment.end  # ends lower trapezoid
						mid_top_trapezoid = Trapezoid(top_segment=trapezoid.top_segment, bottom_segment=segment, left_point=trapezoid.left_point, right_point=segment.end)
						self.create_leafnode(trapezoid=mid_top_trapezoid)

					right_trapezoid.set_neighbours(
						top_left_neighbour=mid_top_trapezoid,
						bottom_left_neighbour=mid_bottom_trapezoid,
						top_right_neighbour=trapezoid.top_right_neighbour,
						bottom_right_neighbour=trapezoid.bottom_right_neighbour
					)

					mid_top_trapezoid.set_neighbours(
						top_left_neighbour=trapezoid.top_left_neighbour if not upperUNKNOWN else 'KEEP_THE_SAME',
						bottom_left_neighbour=trapezoid.bottom_left_neighbour if not upperUNKNOWN else 'KEEP_THE_SAME',
						top_right_neighbour=right_trapezoid,
						bottom_right_neighbour=right_trapezoid
					)

					mid_bottom_trapezoid.set_neighbours(
						top_left_neighbour=trapezoid.top_left_neighbour if upperUNKNOWN else 'KEEP_THE_SAME',
						bottom_left_neighbour=trapezoid.bottom_left_neighbour if upperUNKNOWN else 'KEEP_THE_SAME',
						top_right_neighbour=right_trapezoid,
						bottom_right_neighbour=right_trapezoid
					)

					update_right_neighbours(trapezoid, right_trapezoid)

					if upperUNKNOWN:
						update_left_neighbours(trapezoid, mid_bottom_trapezoid)
					else:
						update_left_neighbours(trapezoid, mid_top_trapezoid)


					mid_top_trapezoid_node = self.trapezoids_to_nodes[mid_top_trapezoid]
					mid_bottom_trapezoid_node = self.trapezoids_to_nodes[mid_bottom_trapezoid]

					right_trapezoid_node = self.create_leafnode(trapezoid=right_trapezoid)

					sNode = Ynode(right=mid_top_trapezoid_node, left=mid_bottom_trapezoid_node, segment=segment)
					qNode = Xnode(right=right_trapezoid_node, left=sNode, point=segment.end)

					self.search_structure.replace_leafnode(self.trapezoids_to_nodes[trapezoid], qNode)

				else:

					CHANGE = False

					if upperUNKNOWN:
						previous_mid_bottom_trapezoid = mid_bottom_trapezoid  # necessary to update neighbours
						mid_bottom_trapezoid = Trapezoid(top_segment=segment, bottom_segment=trapezoid.bottom_segment,left_point=trapezoid.left_point, right_point=UNKNOWN)
						self.create_leafnode(trapezoid=mid_bottom_trapezoid)
					else:
						previous_mid_top_trapezoid = mid_top_trapezoid  # necessary to update neighbours
						mid_top_trapezoid = Trapezoid(top_segment=trapezoid.top_segment,bottom_segment=segment,left_point=trapezoid.left_point,right_point=UNKNOWN)
						self.create_leafnode(trapezoid=mid_top_trapezoid)

					if segment.is_above_point(trapezoid.right_point):
						mid_bottom_trapezoid.right_point = trapezoid.right_point
						if not upperUNKNOWN:
							CHANGE = True
						upperUNKNOWN = True
					else:
						mid_top_trapezoid.right_point = trapezoid.right_point
						if upperUNKNOWN:
							CHANGE = True
						upperUNKNOWN = False


					if upperUNKNOWN:
						if CHANGE:
							mid_top_trapezoid.set_neighbours(
								top_left_neighbour=trapezoid.top_left_neighbour,
								bottom_left_neighbour=previous_mid_top_trapezoid,
								top_right_neighbour=trapezoid.top_right_neighbour,
								bottom_right_neighbour=trapezoid.top_right_neighbour
							)
							mid_bottom_trapezoid.set_neighbours(
								top_right_neighbour=trapezoid.top_right_neighbour,
								bottom_right_neighbour=trapezoid.bottom_right_neighbour
							)
							update_left_neighbours(trapezoid, mid_top_trapezoid)
							update_right_neighbours(trapezoid, mid_bottom_trapezoid)
						else:
							mid_top_trapezoid.set_neighbours(
								top_right_neighbour=trapezoid.top_right_neighbour,
								bottom_right_neighbour=trapezoid.top_right_neighbour
							)
							mid_bottom_trapezoid.set_neighbours(
								top_right_neighbour=trapezoid.top_right_neighbour,
								bottom_right_neighbour=trapezoid.bottom_right_neighbour,
								top_left_neighbour=previous_mid_bottom_trapezoid,
								bottom_left_neighbour=trapezoid.bottom_left_neighbour
							)
							update_left_neighbours(trapezoid, mid_bottom_trapezoid)
							update_right_neighbours(trapezoid, mid_bottom_trapezoid)
					else:
						if CHANGE:
							mid_top_trapezoid.set_neighbours(
								top_right_neighbour=trapezoid.top_right_neighbour,
								bottom_right_neighbour=trapezoid.bottom_right_neighbour
							)
							mid_bottom_trapezoid.set_neighbours(
								top_right_neighbour=trapezoid.bottom_right_neighbour,
								bottom_right_neighbour=trapezoid.bottom_right_neighbour,
								top_left_neighbour=previous_mid_bottom_trapezoid,
								bottom_left_neighbour=trapezoid.bottom_left_neighbour
							)
							update_left_neighbours(trapezoid, mid_bottom_trapezoid)
							update_right_neighbours(trapezoid, mid_top_trapezoid)
						else:
							mid_top_trapezoid.set_neighbours(
								top_left_neighbour=trapezoid.top_left_neighbour,
								bottom_left_neighbour=previous_mid_top_trapezoid,
								top_right_neighbour=trapezoid.top_right_neighbour,
								bottom_right_neighbour=trapezoid.bottom_right_neighbour
							)
							mid_bottom_trapezoid.set_neighbours(
								top_right_neighbour=trapezoid.bottom_right_neighbour,
								bottom_right_neighbour=trapezoid.bottom_right_neighbour
							)
							update_left_neighbours(trapezoid, mid_top_trapezoid)
							update_right_neighbours(trapezoid, mid_top_trapezoid)

					mid_top_trapezoid_node = self.trapezoids_to_nodes[mid_top_trapezoid]
					mid_bottom_trapezoid_node = self.trapezoids_to_nodes[mid_bottom_trapezoid]
					sNode = Ynode(right=mid_top_trapezoid_node, left=mid_bottom_trapezoid_node, segment=segment)

					self.search_structure.replace_leafnode(self.trapezoids_to_nodes[trapezoid], sNode)

		def insert_segment(segment: Segment):
			start_trapezoid = self.search_structure.search(segment.near_start())
			end_trapezoid = self.search_structure.search(segment.near_end())

			if start_trapezoid == end_trapezoid:
				insert_segment_in_one_trapezoid(start_trapezoid, segment)
			else:
				intersectingTrapezoids = find_intersected_trapezoids(segment, start_trapezoid)
				insert_segment_in_multiple_trapezoids(intersectingTrapezoids, segment)

		def find_intersected_trapezoids(segment: Segment, start_trapezoid: Trapezoid) -> list[Trapezoid]:
			intersected_trapezoids = [start_trapezoid]
			current_trapezoid = start_trapezoid
			while segment.end.x > current_trapezoid.right_point.x:  # segment doesn't end in current trapezoid
				if segment.is_above_point(current_trapezoid.right_point):
					current_trapezoid = current_trapezoid.top_right_neighbour
				else:
					current_trapezoid = current_trapezoid.bottom_right_neighbour
				intersected_trapezoids.append(current_trapezoid)
			return intersected_trapezoids


		if shuffle_:
			segments.shuffle()
		for _segment in segments:
			insert_segment(_segment)

		return self.search_structure



def FindBorder(segments):
	"""
    :param segments: Lista Segmentów [Segment]
    :return: Trapezoid
    Funkcja znajduje skrajne punkty i tworzy z nich ograniczający prostokąt powiększony o zmienną size.
    """
	global sought_point
	size = 0.1
	bleft = sought_point.x
	bright = sought_point.x
	blower = sought_point.y
	bupper = sought_point.y

	for segment in segments:
		if segment.start.x < bleft:
			bleft = segment.start.x
		if segment.end.x > bright:
			bright = segment.end.x
		if segment.start.y < blower:
			blower = segment.start.y
		if segment.end.y < blower:
			blower = segment.end.y
		if segment.start.y > bupper:
			bupper = segment.start.y
		if segment.end.y > bupper:
			bupper = segment.end.y

	bleft -= size
	bright += size
	blower -= size
	bupper += size

	upperLeft = Point(bleft, bupper)
	upperRight = Point(bright, bupper)
	lowerLeft = Point(bleft, blower)
	lowerRight = Point(bright, blower)
	top = Segment(upperLeft, upperRight)
	bottom = Segment(lowerLeft, lowerRight)
	border = Trapezoid(top, bottom, upperLeft, upperRight)

	return border
