from PySide6.QtWidgets import QGraphicsRectItem, QWidget, QPushButton
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
    def __init__(self, beamButton, x, y, scene, post_instance):
        super().__init__()
        self.beam = beamButton
        self.scene = scene
        self.post_instance = post_instance
        self.current_rect = None
        self.start_pos = None
        self.beam_select_status = 0  # 0: neutral, 1: select beam, 2: delete beam
        self.beam_width = min(min(x), min(y)) / 10  # Set beam width
        self.post_dimension = min(min(x), min(y)) / 8  # Set post dimension

        # BEAM PROPERTIES
        # START / END
        self.beam_position = set()
        self.beam_loc = []  # for every single beam

    # MUST BE DEVELOPED
    def snap_to_grid(self, point):
        return QPointF(round(point.x()),
                       round(point.y()))
        # return QPointF(round(point.x() / self.beam_width) * self.beam_width,
        #                round(point.y() / self.beam_width) * self.beam_width)

    def draw_beam_mousePress(self, main_self, event):
        print(self.beam_position)
        if event.button() == Qt.LeftButton:
            pos = main_self.mapToScene(event.position().toPoint())
            snapped_pos = self.snap_to_grid(pos)
            if self.current_rect:
                self.finalize_rectangle(snapped_pos)
                end_point = snapped_pos.toTuple()
                start_point = self.beam_loc[0]
                final_end_point = beam_end_point(start_point, end_point)
                self.beam_loc.append(final_end_point)
                self.beam_position.add(tuple(self.beam_loc))
                self.beam_loc.clear()

            else:
                point = snapped_pos.toTuple()
                post_ranges = range_post(self.post_instance.Post_Position, self.post_dimension)
                beam_ranges = selectable_beam_range(self.beam_position, self.beam_width)
                status_post, x_post, y_post = control_post_range(post_ranges, point[0], point[1])
                status_beam, x_beam, y_beam = control_selectable_beam_range(beam_ranges, point[0], point[1])
                print(status_beam, status_post)
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
            snapped_pos = self.snap_to_grid(pos)
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
        snapped_pos = self.snap_to_grid(pos)
        width = snapped_pos.x() - self.start_pos.x()
        height = snapped_pos.y() - self.start_pos.y()

        if abs(width) > abs(height):
            # Move horizontally, keep vertical dimension constant
            self.current_rect.setRect(self.start_pos.x(), self.start_pos.y() - self.beam_width / 2,
                                      width, self.beam_width)
        else:
            # Move vertically, keep horizontal dimension constant
            self.current_rect.setRect(self.start_pos.x() - self.beam_width / 2, self.start_pos.y(),
                                      self.beam_width, height)

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
