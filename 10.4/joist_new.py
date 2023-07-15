import itertools

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QKeyEvent
from PySide6.QtWidgets import QTabWidget, QGraphicsRectItem, QWidget, QPushButton, QDialog, QDialogButtonBox, \
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox

from post_new import magnification_factor
from image import image_control
from DeActivate import deActive
from joist_prop import JoistProperties

from back.joist_control import joist_line_creator


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
        self.joist_number = 1

        self.scene_pos = None

        self.first_click = None
        self.temp_rect = None

        self.joist_status = 0  # 0: neutral, 1: select beam, 2: delete beam
        self.other_button = None

        self.rect_prop = {}  # Dictionary to store coordinates of rectangles

        # note spacing x = width, spacing y = height

    def draw_joist_mousePress(self, main_self, event, properties=None):
        if properties:  # for copy/load
            coordinate = properties["coordinate"]
            x1, y1 = coordinate[0]
            x2, y2 = coordinate[2]
            x1_main = min(x1, x2)
            x2_main = max(x1, x2)
            y1_main = min(y1, y2)
            y2_main = max(y1, y2)
            rect_x, rect_y, rect_w, rect_h = min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)

            rect_item = joistRectangle(rect_x, rect_y, rect_w, rect_h, self.rect_prop)
            if properties["direction"] == "E-W":
                imagePath = "images/e_w.png"
            else:
                imagePath = "images/n_s.png"

            image = image_control(rect_x, rect_y, rect_w, rect_h, rect_item, imagePath)
            rect_item.image = image

            rect_item.setBrush(QBrush(QColor.fromRgb(249, 155, 125, 100)))
            rect_item.setPen(QPen(Qt.black))
            self.scene.addItem(rect_item)

            # Save coordinates of the rectangle corners
            self.rect_prop[rect_item] = {"label": f"J{self.joist_number}",
                                         "coordinate": [(x1_main, y1_main), (x1_main, y2_main),
                                                        (x2_main, y2_main), (x2_main, y1_main)],
                                         "direction": properties["direction"],
                                         "load": {"total_area": properties["load"]["total_area"],
                                                  "custom_area": properties["load"]["custom_area"], "load_map": []}}
            joist_line_creator(self.rect_prop[rect_item])
            print(self.rect_prop)
            self.joist_number += 1

            # Add corner points to snap points

            for point in self.rect_prop[rect_item]["coordinate"]:
                self.snapPoint.add_point(point[0], point[1])

            self.temp_rect = None
            self.first_click = None
        else:
            if event.button() == Qt.LeftButton:
                self.scene_pos = scene_pos = main_self.mapToScene(event.pos())  # Use pos() with QMouseEvent
                if self.joist_status == 1:
                    if not self.first_click and self.first_click != QPointF(0.000000, 0.000000):
                        self.first_click = self.snapPoint.snap(scene_pos)  # Snap to a nearby point if close
                        self.temp_rect = QGraphicsRectItem()
                        self.temp_rect.setPen(QPen(Qt.black))
                        self.temp_rect.setBrush(QBrush(Qt.red))
                        self.scene.addItem(self.temp_rect)
                    elif self.first_click or self.first_click == QPointF(0.000000, 0.000000):
                        snapped_scene_pos = self.snapPoint.snap(scene_pos)  # Snap to a nearby point if close
                        x1, y1 = self.first_click.x(), self.first_click.y()
                        x2, y2 = snapped_scene_pos.x(), snapped_scene_pos.y()
                        x1_main = min(x1, x2)
                        x2_main = max(x1, x2)
                        y1_main = min(y1, y2)
                        y2_main = max(y1, y2)
                        rect_x, rect_y, rect_w, rect_h = min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)
                        self.temp_rect.setRect(rect_x, rect_y, rect_w, rect_h)

                        rect_item = joistRectangle(rect_x, rect_y, rect_w, rect_h, self.rect_prop)
                        image = image_control(rect_x, rect_y, rect_w, rect_h, rect_item)
                        rect_item.image = image

                        rect_item.setBrush(QBrush(QColor.fromRgb(249, 155, 125, 100)))
                        rect_item.setPen(QPen(Qt.black))
                        self.scene.addItem(rect_item)
                        self.scene.removeItem(self.temp_rect)

                        # Save coordinates of the rectangle corners
                        self.rect_prop[rect_item] = {"label": f"J{self.joist_number}",
                                                     "coordinate": [(x1_main, y1_main), (x1_main, y2_main),
                                                                    (x2_main, y2_main), (x2_main, y1_main)],
                                                     "direction": "N-S",
                                                     "load": {"total_area": [], "custom_area": [], "load_map": []}}
                        joist_line_creator(self.rect_prop[rect_item])
                        print(self.rect_prop)
                        self.joist_number += 1

                        # Add corner points to snap points

                        for point in self.rect_prop[rect_item]["coordinate"]:
                            self.snapPoint.add_point(point[0], point[1])

                        self.temp_rect = None
                        self.first_click = None
                elif self.joist_status == 2:
                    # item = self.scene.itemAt(scene_pos, main_self.transform())
                    item = main_self.itemAt(event.position().toPoint())
                    if item and isinstance(item, joistRectangle):
                        # Delete the coordinates of the rectangle
                        if item in self.rect_prop:
                            # remove corner points to snap points
                            for point in self.rect_prop[item]["coordinate"]:
                                self.snapPoint.remove_point(point)

                            del self.rect_prop[item]
                        self.scene.removeItem(item)

    def draw_joist_mouseMove(self):
        if self.first_click:
            x1, y1 = self.first_click.x(), self.first_click.y()
            x2, y2 = self.scene_pos.x(), self.scene_pos.y()
            rect_x, rect_y, rect_w, rect_h = min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)
            self.temp_rect.setRect(rect_x, rect_y, rect_w, rect_h)

    # SLOT
    def joist_selector(self):
        if self.other_button:
            post, beam, shearWall, studWall, load = self.other_button
        if self.joist_status == 0:
            self.joist_status = 1
            self.joist.joist.setText("Draw Joist")
            self.setCursor(Qt.CursorShape.UpArrowCursor)

            # DE ACTIVE OTHER BUTTONS
            if self.other_button:
                deActive(self, post, beam, self, shearWall, studWall, load)
        elif self.joist_status == 1:
            self.joist_status = 2
            self.joist.joist.setText("Delete Joist")
            self.setCursor(Qt.CursorShape.ArrowCursor)

            # DE ACTIVE OTHER BUTTONS
            if self.other_button:
                deActive(self, post, beam, self, shearWall, studWall, load)
        elif self.joist_status == 2:
            self.joist_status = 0
            self.joist.joist.setText("JOIST")
            self.setCursor(Qt.CursorShape.ArrowCursor)


class joistRectangle(QGraphicsRectItem):
    def __init__(self, rect_x, rect_y, rect_w, rect_h, rect_prop):
        super().__init__(rect_x, rect_y, rect_w, rect_h)
        self.image = None
        self.joist_properties_page = None
        self.rect_prop = rect_prop

    # CONTROL ON JOIST
    def mousePressEvent(self, event):
        center = self.boundingRect().center().toTuple()
        # properties page open
        if event.button() == Qt.RightButton:  # Joist Properties page
            height = self.boundingRect().height() - 1  # ATTENTION: I don't know why but this method return height + 1
            width = self.boundingRect().width() - 1  # ATTENTION: I don't know why but this method return width + 1
            joist_joint_coordinates = find_coordinate(center[0], center[1], width, height)
            self.joist_properties_page = JoistProperties(self, self.rect_prop, center, joist_joint_coordinates,
                                                         self.image, self.scene())
            self.joist_properties_page.show()


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
