import math

from PySide6.QtCore import Qt, QPointF, QTimer
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QGraphicsRectItem, QWidget, QPushButton, QGraphicsProxyWidget

from DeActivate import deActive
from beam_prop import BeamProperties
from dimension import DimensionLabel
from pointer_control import control_post_range, range_post, range_post_shearWall, beam_end_point, selectable_beam_range, \
    control_selectable_beam_range
from post_new import magnification_factor


class BeamButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.beam = QPushButton("BEAM")


class beamDrawing(QGraphicsRectItem):
    def __init__(self, beamButton, scene, post_instance, shearWall_instance, snapPoint, snapLine):
        super().__init__()
        self.beam = beamButton
        self.scene = scene
        self.post_instance = post_instance
        self.shearWall_instance = shearWall_instance
        self.snapPoint = snapPoint
        self.snapLine = snapLine
        self.current_rect = None
        self.start_pos = None
        self.beam_select_status = 0  # 0: neutral, 1: select beam, 2: delete beam
        self.other_button = None
        # self.beam_width = min(min(x), min(y)) / 25  # Set beam width
        self.beam_width = magnification_factor / 2  # Set beam width
        # self.post_dimension = min(min(x), min(y)) / 8  # Set post dimension
        self.post_dimension = magnification_factor  # Set post dimension
        self.dimension = None

        # BEAM PROPERTIES
        # START / END
        self.beam_rect_prop = {}
        self.beam_number = 1
        self.beam_loc = []  # for every single beam

    def draw_beam_mousePress(self, main_self, event, properties=None):
        if properties:  # for copy/load
            coordinate = properties["coordinate"]
            x1, y1 = coordinate[0]
            x2, y2 = coordinate[1]
            self.finalize_rectangle_copy((x1, y1), (x2, y2), properties)
        else:
            if event.button() == Qt.LeftButton:

                pos = main_self.mapToScene(event.position().toPoint())
                # snapped_pos = self.snap_to_grid(pos)
                snapped_pos = self.snapPoint.snap(pos)
                # if snap to some point we don't need to check with snap line
                if pos == snapped_pos:
                    snapped_pos = self.snapLine.snap(pos)
                if self.beam_select_status == 2:
                    item = main_self.itemAt(event.position().toPoint())
                    if isinstance(item, Rectangle):  # Finding beam
                        # Delete the coordinates of the rectangle
                        if item in self.beam_rect_prop:
                            # delete snap points (start & end)
                            self.snapPoint.remove_point(self.beam_rect_prop[item]["coordinate"][0])
                            self.snapPoint.remove_point(self.beam_rect_prop[item]["coordinate"][1])
                            self.snapLine.remove_line(tuple(self.beam_rect_prop[item]["coordinate"]))
                            # delete item
                            del self.beam_rect_prop[item]
                        self.scene.removeItem(item)


                else:
                    if self.current_rect:
                        if self.dimension:
                            self.scene.removeItem(self.dimension)
                        snapped_pos = self.snapPoint.snap(pos)
                        # if snap to some point we don't need to check with snap line
                        if pos == snapped_pos:
                            snapped_pos = self.snapLine.snap(pos)
                        self.finalize_rectangle(pos, main_self.shift_pressed)
                        # Create a new rectangle instance
                        self.start_pos = snapped_pos
                        if self.beam_loc:  # Add this condition
                            end_point = snapped_pos.toTuple()
                            start_point = self.beam_loc[0]
                            if main_self.shift_pressed:
                                final_end_point = end_point
                            else:
                                final_end_point = beam_end_point(start_point, end_point)

                            self.beam_loc.append(final_end_point)

                            self.beam_rect_prop[self.current_rect] = {"label": f"B{self.beam_number}",
                                                                      "coordinate": [
                                                                          start_point, final_end_point],
                                                                      "load": {"point": [], "line": [], "reaction": []},
                                                                      "floor": True,
                                                                      "material": "All",
                                                                      "kll": "2"}
                            self.add_length(self.beam_rect_prop[self.current_rect])

                            print(self.beam_rect_prop)
                            self.beam_number += 1
                            self.current_rect = None

                            # Add Snap Line
                            self.snapLine.add_line(self.beam_loc[0], self.beam_loc[1])

                            # Add Start and End beam point to Snap Point
                            self.snapPoint.add_point(self.beam_loc[0][0], self.beam_loc[0][1])
                            self.snapPoint.add_point(self.beam_loc[1][0], self.beam_loc[1][1])

                            self.beam_loc.clear()

                    else:
                        print("shift button: ", main_self.shift_pressed)
                        self.dimension = QGraphicsProxyWidget()
                        snapped_pos = self.snapPoint.snap(pos)
                        # Start point just snap to point not line.
                        point = snapped_pos.toTuple()
                        print("point", point)
                        post_ranges = range_post(self.post_instance.post_prop, self.post_dimension)
                        print("post_ranges", post_ranges)
                        beam_ranges = selectable_beam_range(self.beam_rect_prop, self.beam_width)
                        post_shearWall_ranges = range_post_shearWall(self.shearWall_instance.shearWall_rect_prop,
                                                                     self.post_dimension)

                        status_post, x_post, y_post = control_post_range(post_ranges, point[0], point[1])
                        status_post_shearWall, x_post_shearWall, y_post_shearWall = control_post_range(
                            post_shearWall_ranges, point[0], point[1])
                        status_beam, x_beam, y_beam = control_selectable_beam_range(beam_ranges, point[0], point[1])
                        print(post_ranges)
                        print(status_post, x_post, y_post)
                        print("kjsdhfjasd")
                        print(self.post_instance.post_prop)
                        # shearWall_posts_start = [i["post"]["start_center"] for i in
                        #                          self.shearWall_instance.shearWall_rect_prop.values()]
                        # shearWall_posts_end = [i["post"]["end_center"] for i in
                        #                        self.shearWall_instance.shearWall_rect_prop.values()]
                        # shearWall_posts = shearWall_posts_start + shearWall_posts_end
                        # if point in shearWall_posts:
                        #     status_shearWall_post = True
                        # else:
                        #     status_shearWall_post = False
                        if status_post or status_beam or status_post_shearWall:
                            if status_post:
                                x, y = x_post, y_post
                            elif status_beam:
                                x, y = x_beam, y_beam
                            else:
                                x, y = x_post_shearWall, y_post_shearWall

                            self.start_pos = QPointF(x, y)

                            self.beam_loc.append(self.start_pos.toTuple())

                            self.current_rect = Rectangle(x - self.beam_width / 2,
                                                          y - self.beam_width / 2, self.beam_rect_prop)
                            self.scene.addItem(self.current_rect)

    def draw_beam_mouseMove(self, main_self, event):

        if self.current_rect and (self.start_pos or self.start_pos == QPointF(0.000000, 0.000000)):
            if self.dimension:
                self.scene.removeItem(self.dimension)

            pos = main_self.mapToScene(event.pos())
            # snapped_pos = self.snap_to_grid(pos)
            snapped_pos = self.snapPoint.snap(pos)
            # if snap to some point we don't need to check with snap line
            if pos == snapped_pos:
                snapped_pos = self.snapLine.snap(pos)

            length = (((snapped_pos.x() - self.start_pos.x()) ** 2) + (
                    (snapped_pos.y() - self.start_pos.y()) ** 2)) ** 0.5
            width = snapped_pos.x() - self.start_pos.x()
            height = snapped_pos.y() - self.start_pos.y()
            if main_self.shift_pressed:
                if width == 0:
                    if height >= 0:
                        teta = 90
                    else:
                        teta = -90
                else:
                    teta = math.atan((snapped_pos.y() - self.start_pos.y()) / (
                            snapped_pos.x() - self.start_pos.x())) * 180 / math.pi  # degree\
                    if width < 0:
                        teta = 180 + teta

                self.current_rect.setRect(self.start_pos.x(),
                                          self.start_pos.y() - self.beam_width / 2, length, self.beam_width)
                dimension = DimensionLabel(length, magnification_factor)

                self.dimension.setWidget(dimension)

                self.dimension.setPos((self.start_pos.x() + snapped_pos.x()) / 2,
                                      self.start_pos.y() - 2 * self.beam_width)

                # Set the transformation origin to the start point
                self.current_rect.setTransformOriginPoint(self.start_pos)
                # self.dimension.setTransformOriginPoint(snapped_pos)
                self.dimension.setRotation(teta)
                # Rotate the rectangle
                self.current_rect.setRotation(teta)  # rotate by teta degrees
            else:
                self.current_rect.setRotation(0)  # rotate by teta degrees
                if abs(width) > abs(height):
                    # Move horizontally, keep vertical dimension constant
                    self.current_rect.setRect(min(self.start_pos.x(), snapped_pos.x()),
                                              self.start_pos.y() - self.beam_width / 2, abs(width), self.beam_width)
                    dimension = DimensionLabel(width, magnification_factor)

                    self.dimension.setWidget(dimension)

                    self.dimension.setPos((self.start_pos.x() + snapped_pos.x()) / 2,
                                          self.start_pos.y() - 2 * self.beam_width)
                    self.dimension.setRotation(0)
                else:
                    # Move vertically, keep horizontal dimension constant
                    self.current_rect.setRect(self.start_pos.x() - self.beam_width / 2,
                                              min(self.start_pos.y(), snapped_pos.y()), self.beam_width,
                                              abs(height))
                    dimension = DimensionLabel(height, magnification_factor)

                    self.dimension.setWidget(dimension)

                    self.dimension.setPos(self.start_pos.x() - 2 * self.beam_width,
                                          (self.start_pos.y() + snapped_pos.y()) / 2)
                    self.dimension.setRotation(-90)

            self.scene.addItem(self.dimension)

    def finalize_rectangle(self, pos, shiftPressed):
        snapped_pos = self.snapPoint.snap(pos)
        # if snap to some point we don't need to check with snap line
        if pos == snapped_pos:
            snapped_pos = self.snapLine.snap(pos)
        if shiftPressed:
            length = (((snapped_pos.x() - self.start_pos.x()) ** 2) + (
                    (snapped_pos.y() - self.start_pos.y()) ** 2)) ** 0.5

            self.current_rect.setRect(self.start_pos.x(),
                                      self.start_pos.y() - self.beam_width / 2, length, self.beam_width)
        else:
            width = snapped_pos.x() - self.start_pos.x()
            height = snapped_pos.y() - self.start_pos.y()

            if abs(width) > abs(height):
                self.current_rect.setRect(min(self.start_pos.x(), snapped_pos.x()),
                                          self.start_pos.y() - self.beam_width / 2, abs(width), self.beam_width)
            else:
                self.current_rect.setRect(self.start_pos.x() - self.beam_width / 2,
                                          min(self.start_pos.y(), snapped_pos.y()), self.beam_width,
                                          abs(height))
        self.current_rect.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
        self.current_rect.setBrush(QBrush(QColor.fromRgb(245, 80, 80, 100), Qt.SolidPattern))
        # self.current_rect = None
        self.start_pos = None

    def finalize_rectangle_copy(self, start, end, properties):
        self.beam_loc.append(start)

        x1, y1 = start
        x2, y2 = end
        self.current_rect = Rectangle(x1 - self.beam_width / 2,
                                      y1 - self.beam_width / 2, self.beam_rect_prop)
        self.scene.addItem(self.current_rect)

        width = x2 - x1
        height = y2 - y1
        length = (((x2 - x1) ** 2) + (
                (y2 - y1) ** 2)) ** 0.5
        if width == 0:
            if height >= 0:
                teta = 90
            else:
                teta = -90
        else:
            teta = math.atan((y2 - y1) / (
                    x2 - x1)) * 180 / math.pi  # degree\
            if width < 0:
                teta = 180 + teta

        self.current_rect.setRect(x1,
                                  y1 - self.beam_width / 2, length, self.beam_width)

        startPoint = QPointF(x1, y1)
        self.current_rect.setTransformOriginPoint(startPoint)

        self.current_rect.setRotation(teta)  # rotate by teta degrees

        self.current_rect.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
        self.current_rect.setBrush(QBrush(QColor.fromRgb(245, 80, 80, 100), Qt.SolidPattern))
        # final_end_point = beam_end_point(start, end)
        final_end_point = end
        self.beam_loc.append(final_end_point)
        try:
            floor = properties["floor"]
        except:
            floor = True
        try:
            material = properties["material"]
        except:
            material = "All"
        try:
            Kll = properties["kll"]
        except:
            Kll = "2"

        self.beam_rect_prop[self.current_rect] = {"label": f"B{self.beam_number}",
                                                  "coordinate": [
                                                      start, final_end_point],
                                                  "load": {"point": properties["load"]["point"],
                                                           "line": properties["load"]["line"],
                                                           "reaction": []},
                                                  "floor": floor,
                                                  "material": material,
                                                  "kll": Kll}
        self.add_length(self.beam_rect_prop[self.current_rect])

        print(self.beam_rect_prop)
        self.beam_number += 1

        # Add Snap Line
        self.snapLine.add_line(self.beam_loc[0], self.beam_loc[1])

        # Add Start and End beam point to Snap Point
        self.snapPoint.add_point(self.beam_loc[0][0], self.beam_loc[0][1])
        self.snapPoint.add_point(self.beam_loc[1][0], self.beam_loc[1][1])

        self.current_rect = None
        self.start_pos = None

        self.beam_loc.clear()

    # SLOT
    def beam_selector(self):
        if self.other_button:
            post, joist, shearWall, studWall, load = self.other_button
        if self.beam_select_status == 0:
            self.beam_select_status = 1
            self.beam.beam.setText("Draw Beam")
            self.setCursor(Qt.CursorShape.UpArrowCursor)

            # DE ACTIVE OTHER BUTTONS
            if self.other_button:
                deActive(self, post, self, joist, shearWall, studWall, load)
        elif self.beam_select_status == 1:
            self.beam_select_status = 2
            self.beam.beam.setText("Delete Beam")
            self.setCursor(Qt.CursorShape.ArrowCursor)

            # DE ACTIVE OTHER BUTTONS
            if self.other_button:
                deActive(self, post, self, joist, shearWall, studWall, load)
        elif self.beam_select_status == 2:
            self.beam_select_status = 0
            self.beam.beam.setText("BEAM")
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def add_length(self, beamProp):
        start = beamProp["coordinate"][0]
        end = beamProp["coordinate"][1]
        l = self.length(start, end)
        beamProp["length"] = l

    @staticmethod
    def length(start, end):
        x1 = start[0]
        x2 = end[0]
        y1 = start[1]
        y2 = end[1]
        l = (((y2 - y1) ** 2) + ((x2 - x1) ** 2)) ** 0.5
        return round(l, 2)


class Rectangle(QGraphicsRectItem):
    def __init__(self, x, y, rect_prop):
        super().__init__(x, y, 0, 0)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setPen(QPen(Qt.blue, 2))  # Set the border color to blue
        self.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))  # Set the fill color to transparent
        self.timer = QTimer()
        self.timer.timeout.connect(self.change_color)
        self.colors = [QColor.fromRgb(245, 80, 80, 100), QColor.fromRgb(253, 231, 103, 230)]
        self.current_color = 0
        self.rect_prop = rect_prop
        self.beam_properties_page = None
        self.elementName = "beam"

    # CONTROL ON BEAM
    def mousePressEvent(self, event):
        center = self.boundingRect().center().toTuple()
        # properties page open
        if event.button() == Qt.RightButton:  # beam Properties page
            height = self.boundingRect().height() - 1  # ATTENTION: I don't know why but this method return height + 1
            width = self.boundingRect().width() - 1  # ATTENTION: I don't know why but this method return width + 1
            self.beam_properties_page = BeamProperties(self, self.rect_prop,
                                                       self.scene(), self.timer)
            self.beam_properties_page.show()

            if not self.timer.isActive():
                self.timer.start(400)  # Change color every 500 ms

    def change_color(self):
        self.setBrush(QColor(self.colors[self.current_color]))
        self.current_color = (self.current_color + 1) % len(self.colors)
