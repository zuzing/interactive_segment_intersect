from geometic_objects import Point, Segment, Trapezoid


class Node:
    def __init__(self, right: 'Node' | None, left: 'Node' | None):
        self.left = left
        self.right = right

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, node):
        self._left = node
        if isinstance(node, Leafnode) and self not in node.parents:
            node.parents.append(self)

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, node):
        self._right = node
        if isinstance(node, Leafnode) and self not in node.parents:
            node.parents.append(self)


class Xnode(Node):
    def __init__(self, right: Node, left: Node, point: Point):
        super().__init__(right, left, point)
        self.point = point


class Ynode(Node):
    def __init__(self, right: Node, left: Node, segment: Segment):
        super().__init__(right, left)
        self.segment = segment


class Leafnode(Node):
    def __init__(self, trapezoid: Trapezoid):
        super().__init__(None, None)
        self.trapezoid = trapezoid
        self.parents = []


class SearchDAG:
    def __init__(self, root):
        self.root = root

    def replace_leafnode(self, leafnode: Leafnode, node: Node):
        if not leafnode.parents:
            self.root = node
            return
        for parent in leafnode.parents:
            if parent.left == self:
                parent.left = node
            else:
                parent.right = node

    def search(self, point: Point, node: Node = None) -> Trapezoid:
        if not node:
            node = self.root
        if isinstance(node, Xnode):
            if point.x < node.point.x:
                return self.search(point, node.left)
            else:
                return self.search(point, node.right)
        elif isinstance(node, Ynode):
            if point.y < node.segment.y_coordinate_at(point.x):
                return self.search(point, node.left)
            else:
                return self.search(point, node.right)
        else:
            return node.trapezoid