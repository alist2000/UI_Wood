import itertools

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QKeyEvent
from PySide6.QtWidgets import QTabWidget, QGraphicsRectItem, QWidget, QPushButton, QDialog, QDialogButtonBox, \
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox

from area_centroid_calculator import calculate_centroid_and_area
from post import magnification_factor
from image import image_control


class JoistButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.joist = QPushButton("JOIST")


class joistDrawing(QGraphicsRectItem):
    def __init__(self, joistButton, scene, snapPoint, snapLine):
        super().__init__()
        self.joist = joistButton
        self.scene = scene
        self.snapPoint = snapPoint
        self.snapLine = snapLine

        self.scene_pos = None

        self.first_click = None
        self.temp_rect = None

        self.joist_status = 0  # 0: neutral, 1: select beam, 2: delete beam

        self.rect_coordinates = {}  # Dictionary to store coordinates of rectangles

        # note spacing x = width, spacing y = height

    def draw_joist_mousePress(self, main_self, event):
        if event.button() == Qt.LeftButton:
            self.scene_pos = scene_pos = main_self.mapToScene(event.pos())  # Use pos() with QMouseEvent
            if self.joist_status == 1:
                if not self.first_click:
                    self.first_click = self.snapPoint.snap(scene_pos)  # Snap to a nearby point if close
                    self.temp_rect = QGraphicsRectItem()
                    self.temp_rect.setPen(QPen(Qt.black))
                    self.temp_rect.setBrush(QBrush(Qt.red))
                    self.scene.addItem(self.temp_rect)
                else:
                    snapped_scene_pos = self.snapPoint.snap(scene_pos)  # Snap to a nearby point if close
                    x1, y1 = self.first_click.x(), self.first_click.y()
                    x2, y2 = snapped_scene_pos.x(), snapped_scene_pos.y()
                    rect_x, rect_y, rect_w, rect_h = min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)
                    self.temp_rect.setRect(rect_x, rect_y, rect_w, rect_h)

                    rect_item = QGraphicsRectItem(rect_x, rect_y, rect_w, rect_h)
                    rect_item.setBrush(QBrush(QColor("#F99B7D")))
                    rect_item.setPen(QPen(Qt.black))
                    self.scene.addItem(rect_item)
                    self.scene.removeItem(self.temp_rect)

                    # Save coordinates of the rectangle corners
                    self.rect_coordinates[rect_item] = [(x1, y1), (x1, y2), (x2, y1), (x2, y2)]

                    self.temp_rect = None
                    self.first_click = None
            elif self.joist_status == 2:
                # item = self.scene.itemAt(scene_pos, main_self.transform())
                item = main_self.itemAt(event.position().toPoint())
                print(item)
                if item and isinstance(item, QGraphicsRectItem):
                    # Delete the coordinates of the rectangle
                    if item in self.rect_coordinates:
                        del self.rect_coordinates[item]
                    self.scene.removeItem(item)

    def draw_joist_mouseMove(self):
        if self.first_click:
            x1, y1 = self.first_click.x(), self.first_click.y()
            x2, y2 = self.scene_pos.x(), self.scene_pos.y()
            rect_x, rect_y, rect_w, rect_h = min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)
            self.temp_rect.setRect(rect_x, rect_y, rect_w, rect_h)

    # SLOT
    def joist_selector(self):
        if self.joist_status == 0:
            self.joist_status = 1
            self.joist.joist.setText("Select Joist")
            self.setCursor(Qt.CursorShape.UpArrowCursor)
        elif self.joist_status == 1:
            self.joist_status = 2
            self.joist.joist.setText("Delete Joist")
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif self.joist_status == 2:
            self.joist_status = 0
            self.joist.joist.setText("JOIST")
            self.setCursor(Qt.CursorShape.ArrowCursor)
    # self.coordinate = values
    # self.Joist_Position = Joist_Position = set()
    # for i in show_values:
    #     rect = QGraphicsRectItem()
    #     index_show = show_values.index(i)
    #     j = values[index_show]
    #     rect.setRect(j[0], j[1], j[2], j[3])
    #     rect.setBrush(QBrush(QColor("#F99B7D")))
    #     rect.setPen(QPen(Qt.black))
    #
    #     # add Joist Direction Image
    #     image = image_control(i[0], i[1], i[2], i[3], rect)
    #     scene.addItem(rect)
    #     click_detector1 = ClickableRectItem(i[0], i[1], i[2], i[3], rect, joist_status, Joist_Position, image)
    #     click_detector1.setBrush(QBrush(Qt.transparent))
    #     click_detector1.setPen(QPen(Qt.transparent))
    #     scene.addItem(click_detector1)
    #
    # self.clickable_area_enabled = True


# class ClickableRectItem(QGraphicsRectItem):
#     def __init__(self, x, y, width, height, associated_rect, joist, Joist_Position, image):
#         super().__init__(x, y, width, height)
#         self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
#         self.associated_rect = associated_rect
#         self.associated_rect.setVisible(False)
#         self.joist_status = 0  # 0: neutral, 1: select joist, 2: delete joist
#         joist.joist.clicked.connect(self.joist_selector)
#         self.joist = joist
#
#         # IMAGE
#         self.image = image
#
#         self.Joist_Center_Position = Joist_Position
#
#         self.joist_properties_page = None
#
#     # SLOT
#     def joist_selector(self):
#         if self.joist_status == 0:
#             self.joist_status = 1
#             self.joist.joist.setText("Select Joist")
#             self.setCursor(Qt.CursorShape.UpArrowCursor)
#         elif self.joist_status == 1:
#             self.joist_status = 2
#             self.joist.joist.setText("Delete Joist")
#             self.setCursor(Qt.CursorShape.ArrowCursor)
#         elif self.joist_status == 2:
#             self.joist_status = 0
#             self.joist.joist.setText("JOIST")
#             self.setCursor(Qt.CursorShape.ArrowCursor)
#
#         print(self.Joist_Center_Position)
#
#     def mousePressEvent(self, event):
#         center = self.associated_rect.boundingRect().center().toTuple()
#         # properties page open
#         if event.button() == Qt.RightButton:
#             height = self.associated_rect.boundingRect().height() - 1  # ATTENTION: I don't know why but this method return height + 1
#             width = self.associated_rect.boundingRect().width() - 1  # ATTENTION: I don't know why but this method return width + 1
#             joist_joint_coordinates = find_coordinate(center[0], center[1], width, height)
#             self.joist_properties_page = JoistProperties(center, joist_joint_coordinates, self.Joist_Center_Position,
#                                                          self.image, self.scene())
#             self.joist_properties_page.show()
#         else:  # select/deselect
#             # self.associated_rect.setVisible(not self.associated_rect.isVisible())
#             if self.joist_status:
#                 visibility = True if self.joist_status == 1 else False
#                 self.associated_rect.setVisible(visibility)
#                 if self.joist_status == 1:
#                     self.Joist_Center_Position.add(center)
#                 else:
#                     try:
#                         self.Joist_Center_Position.remove(center)
#                     except:
#                         pass


class JoistProperties(QDialog):
    def __init__(self, center_position, joint_coordinate, Joist_Position, image, scene, parent=None):
        super().__init__(parent)
        self.direction = None
        self.default = "N-S"
        self.final_direction = "N-S"
        self.joint_coordinate = joint_coordinate
        self.position = center_position
        self.Joist_position_list = Joist_Position

        # IMAGE
        self.image = image
        self.scene = scene

        self.setWindowTitle("Joist Properties")
        self.setMinimumSize(200, 400)

        v_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setWindowTitle("Object Data")
        self.button_box = button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.create_geometry_tab()
        self.create_direction_tab()
        # self.direction = self.create_direction_tab()

        # self.button_box =button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # if button_box == QDialogButtonBox.Ok:
        #     print(self.default)
        #     self.direction.textActivated(self.default)
        # button_box.accepted.connect(self.accept)  # Change from dialog.accept to self.accept
        # button_box.accepted.connect(self.accept_control)  # Change from dialog.accept to self.accept
        # button_box.rejected.connect(self.reject)  # Change from dialog.reject to self.reject

        v_layout.addWidget(self.tab_widget)
        v_layout.addWidget(button_box)
        self.setLayout(v_layout)  # Change from dialog.setLayout to self.setLayout

    # Rest of the code remains the same

    # dialog.show()

    def accept_control(self):
        self.accept()
        print(self.default)
        self.final_direction = self.default
        if self.final_direction == "N-S":
            picture_path = "images/n_s.png"
        else:
            picture_path = "images/e_w.png"
        print(picture_path)
        self.image.change_image(picture_path, self.scene)

    def create_geometry_tab(self):
        point1 = tuple([i / magnification_factor for i in self.joint_coordinate[0]])
        point2 = tuple([i / magnification_factor for i in self.joint_coordinate[1]])
        point3 = tuple([i / magnification_factor for i in self.joint_coordinate[2]])
        point4 = tuple([i / magnification_factor for i in self.joint_coordinate[3]])
        xc, yc, area = calculate_centroid_and_area(self.joint_coordinate, magnification_factor)
        tab = QWidget()
        self.tab_widget.addTab(tab, f"Geometry")
        label1 = QLabel("Joint1")
        joint1 = QLabel(f"{point1}")
        label2 = QLabel("Joint2")
        joint2 = QLabel(f"{point2}")
        label3 = QLabel("Joint3")
        joint3 = QLabel(f"{point3}")
        label4 = QLabel("Joint4")
        joint4 = QLabel(f"{point4}")

        label5 = QLabel("Centroid X")
        joint5 = QLabel(f"{xc}")
        label6 = QLabel("Centroid Y")
        joint6 = QLabel(f"{yc}")
        label7 = QLabel("Total Area")
        joint7 = QLabel(f"{area}")

        label8 = QLabel("Joist Exist")

        # control post existence
        if self.position in self.Joist_position_list:
            post_exist = QLabel("Yes")
        else:
            post_exist = QLabel("No")

        # LAYOUT
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(label1)
        h_layout1.addWidget(joint1)
        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(label2)
        h_layout2.addWidget(joint2)
        h_layout3 = QHBoxLayout()
        h_layout3.addWidget(label3)
        h_layout3.addWidget(joint3)
        h_layout4 = QHBoxLayout()
        h_layout4.addWidget(label4)
        h_layout4.addWidget(joint4)
        h_layout5 = QHBoxLayout()
        h_layout5.addWidget(label5)
        h_layout5.addWidget(joint5)
        h_layout6 = QHBoxLayout()
        h_layout6.addWidget(label6)
        h_layout6.addWidget(joint6)
        h_layout7 = QHBoxLayout()
        h_layout7.addWidget(label7)
        h_layout7.addWidget(joint7)
        h_layout8 = QHBoxLayout()
        h_layout8.addWidget(label8)
        h_layout8.addWidget(post_exist)
        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout1)
        v_layout.addLayout(h_layout2)
        v_layout.addLayout(h_layout3)
        v_layout.addLayout(h_layout4)
        v_layout.addLayout(h_layout5)
        v_layout.addLayout(h_layout6)
        v_layout.addLayout(h_layout7)
        v_layout.addLayout(h_layout8)
        tab.setLayout(v_layout)

    def create_direction_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, f"Direction")
        label1 = QLabel("Joist Direction")
        self.direction = direction = QComboBox()
        direction.addItems(["N-S", "E-W"])
        self.direction.setCurrentText(self.final_direction)
        self.button_box.accepted.connect(self.accept_control)  # Change from dialog.accept to self.accept
        self.button_box.rejected.connect(self.reject)  # Change from dialog.reject to self.reject
        self.direction.currentTextChanged.connect(self.direction_control)

        # LAYOUT
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(label1)
        h_layout1.addWidget(direction)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout1)

        tab.setLayout(v_layout)
        # return self.direction

    # SLOT
    def direction_control(self):
        self.default = self.direction.currentText()
        print(self.default)


def find_coordinate(xc, yc, width, height):
    x1 = xc - width / 2
    x2 = xc + width / 2
    y1 = yc - height / 2
    y2 = yc + height / 2
    all_coordinates_list = [(x1, y1), (x1, y2), (x2, y2), (x2, y1)]
    # there is problem in sort
    # all_coordinates = itertools.product([x1, x2], [y1, y2])
    # all_coordinates_list = [i for i in all_coordinates]
    return all_coordinates_list
