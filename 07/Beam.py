from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QTabWidget, QGraphicsRectItem, QWidget, QPushButton, QDialog, QDialogButtonBox, \
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox

from pointer_control import control_post_range, range_post, beam_end_point, selectable_beam_range, \
    control_selectable_beam_range
from post import magnification_factor


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
        self.beam_rect_prop = {}
        self.beam_number = 1
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
                    snapped_pos = self.snapPoint.snap(pos)
                    # if snap to some point we don't need to check with snap line
                    if pos == snapped_pos:
                        snapped_pos = self.snapLine.snap(pos)
                    self.finalize_rectangle(pos)
                    # Create a new rectangle instance
                    self.start_pos = snapped_pos
                    if self.beam_loc:  # Add this condition
                        end_point = snapped_pos.toTuple()
                        start_point = self.beam_loc[0]
                        final_end_point = beam_end_point(start_point, end_point)
                        self.beam_loc.append(final_end_point)
                        self.beam_rect_prop[self.current_rect] = {"label": f"B{self.beam_number}",
                                                                  "coordinate": [start_point, final_end_point]}
                        self.beam_number += 1
                        self.current_rect = None

                        # Add Snap Line
                        self.snapLine.add_line(self.beam_loc[0], self.beam_loc[1])

                        # Add Start and End beam point to Snap Point
                        self.snapPoint.add_point(self.beam_loc[0][0], self.beam_loc[0][1])
                        self.snapPoint.add_point(self.beam_loc[1][0], self.beam_loc[1][1])

                        self.beam_loc.clear()

                else:
                    snapped_pos = self.snapPoint.snap(pos)
                    # Start point just snap to point not line.
                    point = snapped_pos.toTuple()
                    post_ranges = range_post(self.post_instance.post_prop, self.post_dimension)
                    beam_ranges = selectable_beam_range(self.beam_rect_prop, self.beam_width)
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
                                                      y - self.beam_width / 2, self.beam_rect_prop)
                        self.scene.addItem(self.current_rect)

    def draw_beam_mouseMove(self, main_self, event):
        if self.current_rect and (self.start_pos or self.start_pos == QPointF(0.000000, 0.000000)):
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
        # self.current_rect = None
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
    def __init__(self, x, y, rect_prop):
        super().__init__(x, y, 0, 0)
        self.setPen(QPen(Qt.blue, 2))  # Set the border color to blue
        self.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))  # Set the fill color to transparent

        self.rect_prop = rect_prop
        self.beam_properties_page = None

    # CONTROL ON BEAM
    def mousePressEvent(self, event):
        center = self.boundingRect().center().toTuple()
        # properties page open
        if event.button() == Qt.RightButton:  # beam Properties page
            height = self.boundingRect().height() - 1  # ATTENTION: I don't know why but this method return height + 1
            width = self.boundingRect().width() - 1  # ATTENTION: I don't know why but this method return width + 1
            self.beam_properties_page = BeamProperties(self, self.rect_prop,
                                                       self.scene())
            self.beam_properties_page.show()


class BeamProperties(QDialog):
    def __init__(self, rectItem, rect_prop, scene, parent=None):
        super().__init__(parent)
        self.direction = None
        self.rectItem = rectItem
        self.rect_prop = rect_prop

        # IMAGE
        self.scene = scene

        self.setWindowTitle("Beam Properties")
        self.setMinimumSize(200, 400)

        v_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setWindowTitle("Object Data")
        self.button_box = button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)  # Change from dialog.accept to self.accept
        self.button_box.rejected.connect(self.reject)  # Change from dialog.reject to self.reject

        self.create_geometry_tab()

        v_layout.addWidget(self.tab_widget)
        v_layout.addWidget(button_box)
        self.setLayout(v_layout)  # Change from dialog.setLayout to self.setLayout

    # Rest of the code remains the same

    # dialog.show()

    def accept_control(self):
        print(self.rect_prop)

    def create_geometry_tab(self):
        start = tuple([i / magnification_factor for i in self.rect_prop[self.rectItem]["coordinate"][0]])
        end = tuple([i / magnification_factor for i in self.rect_prop[self.rectItem]["coordinate"][1]])
        tab = QWidget()
        self.tab_widget.addTab(tab, f"Geometry")
        label0 = QLabel("Label")
        joistLabel = QLabel(self.rect_prop[self.rectItem]["label"])
        label1 = QLabel("Start")
        start_point = QLabel(f"{start}")
        label2 = QLabel("End")
        end_point = QLabel(f"{end}")

        # calc length
        l = self.length(start, end)
        label3 = QLabel("Length")
        length = QLabel(f"{l}")

        # LAYOUT
        h_layout0 = QHBoxLayout()
        h_layout0.addWidget(label0)
        h_layout0.addWidget(joistLabel)
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(label1)
        h_layout1.addWidget(start_point)
        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(label2)
        h_layout2.addWidget(end_point)
        h_layout3 = QHBoxLayout()
        h_layout3.addWidget(label3)
        h_layout3.addWidget(length)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout0)
        v_layout.addLayout(h_layout1)
        v_layout.addLayout(h_layout2)
        v_layout.addLayout(h_layout3)
        tab.setLayout(v_layout)

    @staticmethod
    def length(start, end):
        x1 = start[0]
        x2 = end[0]
        y1 = start[1]
        y2 = end[1]
        l = (((y2 - y1) ** 2) + ((x2 - x1) ** 2)) ** 0.5
        return round(l, 2)
