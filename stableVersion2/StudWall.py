from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QTabWidget, QGraphicsRectItem, QWidget, QPushButton, QDialog, QDialogButtonBox, \
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QGraphicsProxyWidget

from pointer_control import beam_end_point
from post_new import magnification_factor
from DeActivate import deActive
from beam_prop import lineLoad
from dimension import DimensionLabel

from back.beam_control import beam_line_creator
from UI_Wood.stableVersion2.pointer_control import pointer_control_studWall


class StudWallButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.studWall = QPushButton("STUD WALL")


class studWallDrawing(QGraphicsRectItem):
    def __init__(self, studWallButton, x, y, grid, scene, snapPoint, snapLine):
        super().__init__()
        self.studWall = studWallButton
        self.scene = scene
        self.snapPoint = snapPoint
        self.snapLine = snapLine
        self.grid = grid

        self.current_rect = None
        self.start_pos = None
        self.direction = None
        self.interior_exterior = None
        self.studWall_select_status = 0  # 0: neutral, 1: select studWall, 2: delete studWall
        self.other_button = None
        self.studWall_width = magnification_factor / 3  # Set studWall width, magnification = 1 ft or 1 m
        # self.studWall_width = min(min(x), min(y)) / 12  # Set studWall width
        self.dimension = None

        # studWall PROPERTIES
        # START / END
        self.studWall_rect_prop = {}
        self.studWall_number = 1
        self.studWall_loc = []  # for every single studWall

    def draw_studWall_mousePress(self, main_self, event, prop=None):
        if prop:  # for copy/load
            coordinate = prop["coordinate"]
            x1, y1 = coordinate[0]
            x2, y2 = coordinate[1]
            self.finalize_rectangle_copy((x1, y1), (x2, y2), prop)
        else:
            if event.button() == Qt.LeftButton:

                pos = main_self.mapToScene(event.position().toPoint())
                # snapped_pos = self.snap_to_grid(pos)
                snapped_pos = self.snapPoint.snap(pos)
                # if snap to some point we don't need to check with snap line
                if pos == snapped_pos:
                    snapped_pos = self.snapLine.snap(pos)
                if self.studWall_select_status == 2:
                    item = main_self.itemAt(event.position().toPoint())
                    if isinstance(item, Rectangle):  # Finding studWall
                        # Delete the coordinates of the rectangle
                        if item in self.studWall_rect_prop:
                            # delete snap points (start & end)
                            self.snapPoint.remove_point(self.studWall_rect_prop[item]["coordinate"][0])
                            self.snapPoint.remove_point(self.studWall_rect_prop[item]["coordinate"][1])
                            self.snapLine.remove_line(tuple(self.studWall_rect_prop[item]["coordinate"]))
                            # delete item
                            del self.studWall_rect_prop[item]
                        self.scene.removeItem(item)


                else:
                    if self.current_rect:
                        if self.dimension:
                            self.scene.removeItem(self.dimension)
                        snapped_pos = self.snapPoint.snap(pos)
                        # if snap to some point we don't need to check with snap line
                        if pos == snapped_pos:
                            snapped_pos = self.snapLine.snap(pos)
                        self.finalize_rectangle(pos)
                        # Create a new rectangle instanceself.studWall_rect_prop[self.current_rect]
                        self.start_pos = snapped_pos
                        if self.studWall_loc:  # Add this condition
                            end_point = snapped_pos.toTuple()
                            start_point = self.studWall_loc[0]
                            final_end_point = beam_end_point(start_point, end_point)
                            self.studWall_loc.append(final_end_point)
                            l = self.length(start_point, end_point)
                            self.direction, self.interior_exterior = pointer_control_studWall(start_point, end_point,
                                                                                              self.grid)

                            self.studWall_rect_prop[self.current_rect] = {"label": f"ST{self.studWall_number}",
                                                                          "coordinate": [start_point, final_end_point],
                                                                          "length": l,
                                                                          "direction": self.direction,
                                                                          "interior_exterior": self.interior_exterior,
                                                                          "thickness": "4 in",  # in
                                                                          "load": {"point": [], "line": [],
                                                                                   "reaction": []}
                                                                          }

                            beam_line_creator(self.studWall_rect_prop[self.current_rect])

                            self.studWall_number += 1
                            self.current_rect = None

                            # Add Snap Line
                            self.snapLine.add_line(self.studWall_loc[0], self.studWall_loc[1])

                            # Add Start and End studWall point to Snap Point
                            self.snapPoint.add_point(self.studWall_loc[0][0], self.studWall_loc[0][1])
                            self.snapPoint.add_point(self.studWall_loc[1][0], self.studWall_loc[1][1])

                            self.studWall_loc.clear()

                    else:
                        self.dimension = QGraphicsProxyWidget()
                        snapped_pos = self.snapPoint.snap(pos)
                        # Start point just snap to point not line.
                        point = snapped_pos.toTuple()
                        x, y = point[0], point[1]

                        self.start_pos = QPointF(x, y)

                        self.studWall_loc.append(self.start_pos.toTuple())

                        self.current_rect = Rectangle(x - self.studWall_width / 2,
                                                      y - self.studWall_width / 2, self.studWall_rect_prop)
                        self.scene.addItem(self.current_rect)

    def draw_studWall_mouseMove(self, main_self, event):
        if self.current_rect and (self.start_pos or self.start_pos == QPointF(0.000000, 0.000000)):
            if self.dimension:
                self.scene.removeItem(self.dimension)
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
                                          self.start_pos.y() - self.studWall_width / 2, abs(width), self.studWall_width)
                dimension = DimensionLabel(width, magnification_factor)

                self.dimension.setWidget(dimension)

                self.dimension.setPos((self.start_pos.x() + snapped_pos.x()) / 2,
                                      self.start_pos.y() - 2 * self.studWall_width)
                self.dimension.setRotation(0)
            else:
                # Move vertically, keep horizontal dimension constant
                self.current_rect.setRect(self.start_pos.x() - self.studWall_width / 2,
                                          min(self.start_pos.y(), snapped_pos.y()), self.studWall_width,
                                          abs(height))

                dimension = DimensionLabel(height, magnification_factor)

                self.dimension.setWidget(dimension)

                self.dimension.setPos(self.start_pos.x() - 2 * self.studWall_width,
                                      (self.start_pos.y() + snapped_pos.y()) / 2)
                self.dimension.setRotation(-90)

            self.scene.addItem(self.dimension)

    def finalize_rectangle(self, pos):
        snapped_pos = self.snapPoint.snap(pos)
        # if snap to some point we don't need to check with snap line
        if pos == snapped_pos:
            snapped_pos = self.snapLine.snap(pos)
        width = snapped_pos.x() - self.start_pos.x()
        height = snapped_pos.y() - self.start_pos.y()

        if abs(width) > abs(height):
            self.current_rect.setRect(min(self.start_pos.x(), snapped_pos.x()),
                                      self.start_pos.y() - self.studWall_width / 2, abs(width), self.studWall_width)
        else:
            self.current_rect.setRect(self.start_pos.x() - self.studWall_width / 2,
                                      min(self.start_pos.y(), snapped_pos.y()), self.studWall_width,
                                      abs(height))

        self.current_rect.setPen(QPen(QColor.fromRgb(152, 238, 204, 160), 2))
        self.current_rect.setBrush(QBrush(QColor.fromRgb(152, 238, 204, 150), Qt.SolidPattern))
        # self.current_rect = None
        self.start_pos = None

    def finalize_rectangle_copy(self, start, end, prop):
        self.studWall_loc.append(start)

        x1, y1 = start
        x2, y2 = end

        # if snap to some point we don't need to check with snap line
        self.current_rect = Rectangle(x1,
                                      y1, self.studWall_rect_prop)
        self.scene.addItem(self.current_rect)
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        if abs(width) > abs(height):
            self.current_rect.setRect(min(x1, x2),
                                      y1 - self.studWall_width / 2, abs(width), self.studWall_width)
        else:
            self.current_rect.setRect(x1 - self.studWall_width / 2,
                                      min(y1, y2), self.studWall_width,
                                      abs(height))

        self.current_rect.setPen(QPen(QColor.fromRgb(152, 238, 204, 160), 2))
        self.current_rect.setBrush(QBrush(QColor.fromRgb(152, 238, 204, 150), Qt.SolidPattern))
        self.start_pos = None
        end_point = end
        start_point = self.studWall_loc[0]
        final_end_point = beam_end_point(start_point, end_point)
        self.studWall_loc.append(final_end_point)
        l = self.length(start, end)
        self.direction, self.interior_exterior = pointer_control_studWall(start_point, end_point,
                                                                          self.grid)
        try:
            thickness = prop["thickness"]
        except KeyError:
            thickness = "4 in"

        self.studWall_rect_prop[self.current_rect] = {"label": f"ST{self.studWall_number}",
                                                      "coordinate": [start_point, final_end_point],
                                                      "length": l,
                                                      "direction": self.direction,
                                                      "interior_exterior": self.interior_exterior,
                                                      "thickness": thickness,  # in
                                                      "load": {"point": [], "line": [], "reaction": []}
                                                      }

        beam_line_creator(self.studWall_rect_prop[self.current_rect])

        self.studWall_number += 1
        self.current_rect = None

        # Add Snap Line
        self.snapLine.add_line(self.studWall_loc[0], self.studWall_loc[1])

        # Add Start and End studWall point to Snap Point
        self.snapPoint.add_point(self.studWall_loc[0][0], self.studWall_loc[0][1])
        self.snapPoint.add_point(self.studWall_loc[1][0], self.studWall_loc[1][1])

        self.studWall_loc.clear()

    @staticmethod
    def length(start, end):
        x1 = start[0]
        x2 = end[0]
        y1 = start[1]
        y2 = end[1]
        l = (((y2 - y1) ** 2) + ((x2 - x1) ** 2)) ** 0.5
        return round(l, 2)

    # SLOT
    def studWall_selector(self):
        if self.other_button:
            post, beam, joist, shearWall, load = self.other_button
        if self.studWall_select_status == 0:
            self.studWall_select_status = 1
            self.studWall.studWall.setText("Draw Stud Wall")
            self.setCursor(Qt.CursorShape.UpArrowCursor)

            # DE ACTIVE OTHER BUTTONS
            if self.other_button:
                deActive(self, post, beam, joist, shearWall, self, load)
        elif self.studWall_select_status == 1:
            self.studWall_select_status = 2
            self.studWall.studWall.setText("Delete Stud Wall")
            self.setCursor(Qt.CursorShape.ArrowCursor)

            # DE ACTIVE OTHER BUTTONS
            if self.other_button:
                deActive(self, post, beam, joist, shearWall, self, load)
        elif self.studWall_select_status == 2:
            self.studWall_select_status = 0
            self.studWall.studWall.setText("STUD WALL")
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
        self.studWall_properties_page = None

    # CONTROL ON STUD WALL
    def mousePressEvent(self, event):
        center = self.boundingRect().center().toTuple()
        # properties page open
        if event.button() == Qt.RightButton:  # studWall Properties page
            height = self.boundingRect().height() - 1  # ATTENTION: I don't know why but this method return height + 1
            width = self.boundingRect().width() - 1  # ATTENTION: I don't know why but this method return width + 1
            self.studWall_properties_page = StudWallProperties(self, self.rect_prop,
                                                               self.scene())
            self.studWall_properties_page.show()


class StudWallProperties(QDialog):
    def __init__(self, rectItem, rect_prop, scene, parent=None):
        super().__init__(parent)
        self.direction = None
        self.rectItem = rectItem
        self.rect_prop = rect_prop
        self.thickness = None
        self.thickness_default = rect_prop[rectItem]["thickness"]

        # IMAGE
        self.scene = scene

        self.setWindowTitle("Stud Wall Properties")
        self.setMinimumSize(200, 400)

        v_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setWindowTitle("Object Data")
        self.button_box = button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept_control)  # Change from dialog.accept to self.accept
        self.button_box.rejected.connect(self.reject)  # Change from dialog.reject to self.reject

        self.create_geometry_tab()
        self.create_assignment_tab()
        self.lineLoad = lineLoad(self.tab_widget, self.rect_prop[self.rectItem])

        v_layout.addWidget(self.tab_widget)
        v_layout.addWidget(button_box)
        self.setLayout(v_layout)  # Change from dialog.setLayout to self.setLayout

    # Rest of the code remains the same

    # dialog.show()

    def accept_control(self):
        print(self.rect_prop)
        self.lineLoad.print_values()
        self.accept()

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

    def create_assignment_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, f"Assignments")
        label1 = QLabel("Stud Wall Thickness")
        self.thickness = thickness = QComboBox()
        thickness.addItems(["4 in", "6 in"])
        self.thickness.setCurrentText(self.rect_prop[self.rectItem]["thickness"])
        self.button_box.accepted.connect(self.accept_control)  # Change from dialog.accept to self.accept
        self.button_box.rejected.connect(self.reject)  # Change from dialog.reject to self.reject
        self.thickness.currentTextChanged.connect(self.thickness_control)

        # LAYOUT
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(label1)
        h_layout1.addWidget(thickness)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout1)

        tab.setLayout(v_layout)
        # return self.direction
        # SLOT

    def thickness_control(self):
        self.thickness_default = self.thickness.currentText()
        self.rect_prop[self.rectItem]["thickness"] = self.thickness_default

    @staticmethod
    def length(start, end):
        x1 = start[0]
        x2 = end[0]
        y1 = start[1]
        y2 = end[1]
        l = (((y2 - y1) ** 2) + ((x2 - x1) ** 2)) ** 0.5
        return round(l, 2)
