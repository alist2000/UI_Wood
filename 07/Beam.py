from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QGraphicsRectItem, QWidget, QPushButton

from pointer_control import control_post_range, range_post, beam_end_point, selectable_beam_range, \
    control_selectable_beam_range


class BeamButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.beam = QPushButton("BEAM")


class beamDrawing(QGraphicsRectItem):
    def __init__(self, beamButton, x, y, scene, post_instance, snapPoint, snapLine):
        super().__init__()
        self.beam = beamButton
        self.scene = scene
        self.post_instance = post_instance
        self.snapPoint = snapPoint
        self.snapLine = snapLine
        self.current_rect = None
        self.start_pos = None
        self.beam_select_status = 0  # 0: neutral, 1: select beam, 2: delete beam
        self.beam_width = min(min(x), min(y)) / 10  # Set beam width
        self.post_dimension = min(min(x), min(y)) / 8  # Set post dimension

        # BEAM PROPERTIES
        # START / END
        self.beam_position = set()
        self.beam_loc = []  # for every single beam

    def draw_beam_mousePress(self, main_self, event):
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
                    # Remove the corresponding beam position from the beam_position set
                    for beam_loc in self.beam_position.copy():
                        beam_ranges = selectable_beam_range([beam_loc], self.beam_width)
                        status_beam, x_beam, y_beam = control_selectable_beam_range(beam_ranges, pos.x(),
                                                                                    pos.y())
                        if status_beam:
                            self.scene.removeItem(item)
                            self.beam_position.remove(beam_loc)
                            self.snapLine.lines.remove((beam_loc[0], beam_loc[1]))
                            break

            else:
                if self.current_rect:
                    snapped_pos = self.snapPoint.snap(pos)
                    # if snap to some point we don't need to check with snap line
                    if pos == snapped_pos:
                        snapped_pos = self.snapLine.snap(pos)
                    self.finalize_rectangle(snapped_pos)
                    # Create a new rectangle instance
                    self.start_pos = snapped_pos
                    if self.beam_loc:  # Add this condition
                        end_point = snapped_pos.toTuple()
                        start_point = self.beam_loc[0]
                        final_end_point = beam_end_point(start_point, end_point)
                        self.beam_loc.append(final_end_point)
                        self.beam_position.add(tuple(self.beam_loc))

                        # Add Snap Line
                        self.snapLine.add_line(self.beam_loc[0], self.beam_loc[1])

                        self.beam_loc.clear()

                else:
                    snapped_pos = self.snapPoint.snap(pos)
                    # Start point just snap to point not line.
                    point = snapped_pos.toTuple()
                    post_ranges = range_post(self.post_instance.Post_Position, self.post_dimension)
                    beam_ranges = selectable_beam_range(self.beam_position, self.beam_width)
                    status_post, x_post, y_post = control_post_range(post_ranges, point[0], point[1])
                    status_beam, x_beam, y_beam = control_selectable_beam_range(beam_ranges, point[0], point[1])
                    if status_post or status_beam:
                        if status_post:
                            x, y = x_post, y_post
                        else:
                            x, y = x_beam, y_beam

                        self.start_pos = QPointF(x, y)

                        self.beam_loc.append(self.start_pos.toTuple())

                        self.current_rect = Rectangle(x - self.beam_width / 2,
                                                      y - self.beam_width / 2)
                        self.scene.addItem(self.current_rect)

    def draw_beam_mouseMove(self, main_self, event):
        if self.current_rect and self.start_pos:
            pos = main_self.mapToScene(event.pos())
            # snapped_pos = self.snap_to_grid(pos)
            snapped_pos = self.snapPoint.snap(pos)
            # if snap to some point we don't need to check with snap line
            if pos == snapped_pos:
                snapped_pos = self.snapLine.snap(pos)
            width = snapped_pos.x() - self.start_pos.x()
            height = snapped_pos.y() - self.start_pos.y()

            if abs(width) > abs(height):
                # Move horizontally, keep vertical dimension constant
                self.current_rect.setRect(min(self.start_pos.x(), snapped_pos.x()),
                                          self.start_pos.y() - self.beam_width / 2, abs(width), self.beam_width)
            else:
                # Move vertically, keep horizontal dimension constant
                self.current_rect.setRect(self.start_pos.x() - self.beam_width / 2,
                                          min(self.start_pos.y(), snapped_pos.y()), self.beam_width,
                                          abs(height))

    def finalize_rectangle(self, pos):
        snapped_pos = self.snapPoint.snap(pos)
        # if snap to some point we don't need to check with snap line
        if pos == snapped_pos:
            snapped_pos = self.snapLine.snap(pos)
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
        self.current_rect = None
        self.start_pos = None

    # SLOT
    def beam_selector(self):
        if self.beam_select_status == 0:
            self.beam_select_status = 1
            self.beam.beam.setText("Draw Beam")
            self.setCursor(Qt.CursorShape.UpArrowCursor)
        elif self.beam_select_status == 1:
            self.beam_select_status = 2
            self.beam.beam.setText("Delete Beam")
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif self.beam_select_status == 2:
            self.beam_select_status = 0
            self.beam.beam.setText("BEAM")
            self.setCursor(Qt.CursorShape.ArrowCursor)

    # @staticmethod
    # def post_slot2():
    #     print("self.a")
    #     print(post_position)
    #     # print(self.postObject.Post_Position)


class Rectangle(QGraphicsRectItem):
    def __init__(self, x, y):
        super().__init__(x, y, 0, 0)
        self.setPen(QPen(Qt.blue, 2))  # Set the border color to blue
        self.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))  # Set the fill color to transparent
