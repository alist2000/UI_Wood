from abc import ABC, abstractmethod
from PySide6.QtCore import QPointF
import numpy as np
import unittest


class Snap(ABC):
    def __init__(self):
        self.snap_distance = 20
        self.status = True

    @abstractmethod
    def snap(self, point):
        pass

    @abstractmethod
    def snap_status(self, status):
        pass

    @abstractmethod
    def set_snap_distance(self, distance):
        pass


class SnapPoint(Snap):
    def __init__(self):
        super().__init__()
        self.points = []

    def set_snap_distance(self, distance):
        self.snap_distance = distance

    def add_point(self, x, y):
        self.points.append((x, y))

    def remove_point(self, point):
        self.points.remove(point)

    def snap(self, point):
        if self.status:
            # Implement snapping logic for points
            # Hint user for later drawing and snap to the points if the cursor is close enough
            for snap_point in self.points:
                if (abs(point.x() - snap_point[0]) <= self.snap_distance and
                        abs(point.y() - snap_point[1]) <= self.snap_distance):
                    return QPointF(snap_point[0], snap_point[1])
        return point

    # Snap point on/off
    def snap_status(self, status):
        # snap on
        if status:
            self.status = True
        # snap off
        else:
            self.status = False


class SnapLine(Snap):
    def __init__(self):
        super().__init__()
        self.lines = []

    def set_snap_distance(self, distance):
        self.snap_distance = distance

    def add_line(self, start, end):
        self.lines.append((start, end))

    def remove_line(self, line):
        # line: (start, ene)
        self.lines.remove(line)

    def snap(self, point):
        if self.status:
            for snap_line in self.lines:
                start = snap_line[0]
                end = snap_line[1]
                num_points = int(((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5) + 1
                x_values = np.linspace(start[0], end[0], num_points)[1:-1]
                x_values = np.concatenate(([start[0]], x_values[1:]))
                x_values = np.concatenate((x_values[:-1], [end[0]]))
                y_values = np.linspace(start[1], end[1], num_points)[1:-1]
                y_values = np.concatenate(([start[1]], y_values[1:]))
                y_values = np.concatenate((y_values[:-1], [end[1]]))
                line_points = list(zip(x_values, y_values))
                for snap_point in line_points:
                    if (abs(point.x() - snap_point[0]) <= self.snap_distance and
                            abs(point.y() - snap_point[1]) <= self.snap_distance):
                        return QPointF(snap_point[0], snap_point[1])
        return point

    # Snap line on/off
    def snap_status(self, status):
        # snap on
        if status:
            self.status = True
        # snap off
        else:
            self.status = False

# TEST
# class TestSnapPoint(unittest.TestCase):
#     def setUp(self):
#         self.snap_point = SnapPoint()
#         self.snap_point.add_point(10, 20)
#         self.snap_point.add_point(30, 40)
#         self.snap_point.set_snap_distance(5)
#
#     def test_snap_point_inside_snap_distance(self):
#         result = self.snap_point.snap(QPointF(15, 25))
#         self.assertEqual(result, QPointF(10, 20))
#
#     def test_snap_point_outside_snap_distance(self):
#         result = self.snap_point.snap(QPointF(40, 50))
#         self.assertEqual(result, QPointF(40, 50))
#
#     def test_snap_status(self):
#         self.snap_point.snap_status(False)
#         self.assertFalse(self.snap_point.status)
#
#
# class TestSnapLine(unittest.TestCase):
#     def setUp(self):
#         self.snap_line = SnapLine()
#         self.snap_line.add_line((50, 60), (70, 80))
#         self.snap_line.add_line((90, 100), (110, 120))
#         self.snap_line.set_snap_distance(5)
#
#     def test_snap_line_projection_inside_snap_distance(self):
#         result = self.snap_line.snap(QPointF(60, 70))
#         self.assertEqual(result, QPointF(55, 65))
#
#     def test_snap_line_projection_outside_snap_distance(self):
#         result = self.snap_line.snap(QPointF(80, 90))
#         self.assertEqual(result, QPointF(80, 90))
#
#     def test_snap_line_endpoint_inside_snap_distance(self):
#         result = self.snap_line.snap(QPointF(49, 59))
#         self.assertEqual(result, QPointF(50, 60))
#
#     def test_snap_line_endpoint_outside_snap_distance(self):
#         result = self.snap_line.snap(QPointF(45, 55))
#         self.assertEqual(result, QPointF(50, 60))
#
#     def test_snap_status(self):
#         self.snap_line.snap_status(False)
#         self.assertFalse(self.snap_line.status)
#
#
# if __name__ == '__main__':
#     unittest.main()
