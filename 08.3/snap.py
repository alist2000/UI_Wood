from abc import ABC, abstractmethod
from PySide6.QtCore import QPointF
import numpy as np
import math
import unittest


class Snap(ABC):
    def __init__(self):
        self.snap_distance = 30
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
        self.points.append((round(x, 2), round(y, 2)))

    def remove_point(self, point):
        self.points.remove(point)

    def snap(self, point):
        point1 = round(point.x())
        point2 = round(point.y())
        if self.status:
            # Implement snapping logic for points
            # Hint user for later drawing and snap to the points if the cursor is close enough
            for snap_point in self.points:
                if (abs(point1 - snap_point[0]) <= self.snap_distance and
                        abs(point2 - snap_point[1]) <= self.snap_distance):
                    return QPointF(snap_point[0], snap_point[1])
                # if (abs(point.x() - snap_point[0]) <= self.snap_distance and
                #         abs(point.y() - snap_point[1]) <= self.snap_distance):

        return QPointF(point1, point2)

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
        point = point.toTuple()
        for snap_line in self.lines:
            start = snap_line[0]
            end = snap_line[1]
            Ax, Ay = start
            Bx, By = end
            Cx, Cy = point

            distance = self.calculate_distance(start, end, point)
            print(distance)
            if distance < self.snap_distance:

                ## Calculating the slope of the line AB
                if Bx == Ax:  # AB is a vertical line
                    return QPointF(Ax, Cy)  # D is directly above or below C on the line AB
                else:
                    slope_AB = (By - Ay) / (Bx - Ax)

                    # If AB is a horizontal line
                    if slope_AB == 0:
                        return QPointF(Cx, Ay)  # D is directly to the left or right of C on the line AB
                    else:
                        # Calculating the slope of the line perpendicular to AB
                        slope_perpendicular = -1 / slope_AB

                        # Calculating the y-intercept of the line CD
                        intercept_CD = Cy - slope_perpendicular * Cx

                        # Calculating the y-intercept of the line AB
                        intercept_AB = Ay - slope_AB * Ax

                        # Calculating the x-coordinate of point D
                        Dx = (intercept_CD - intercept_AB) / (slope_AB - slope_perpendicular)

                        # Calculating the y-coordinate of point D
                        Dy = slope_AB * Dx + intercept_AB

                        return QPointF(Dx, Dy)

        return QPointF(point[0], point[1])

    @staticmethod
    def calculate_distance(start, end, point):
        x1, y1 = start
        x2, y2 = end
        x3, y3 = point

        numerator = abs((x2 - x1) * (y1 - y3) - (x1 - x3) * (y2 - y1))
        denominator = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if denominator == 0:
            return 0

        return numerator / denominator

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
