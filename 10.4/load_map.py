import itertools

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QKeyEvent
from PySide6.QtWidgets import QTabWidget, QGraphicsRectItem, QWidget, QPushButton, QDialog, QDialogButtonBox, \
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QColorDialog

from post_new import magnification_factor
from image import image_control
from DeActivate import deActive
from load_prop import LoadProperties

from load_type_color import Choose_load_and_color
from back.joist_control import joist_line_creator


class LoadButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load = QPushButton("LOAD MAP")


class loadDrawing(QGraphicsRectItem):
    def __init__(self, loadButton, scene, snapPoint, snapLine, toolBar):
        super().__init__()
        self.load = loadButton
        self.scene = scene
        self.snapPoint = snapPoint
        self.snapLine = snapLine
        self.toolBar = toolBar
        self.load_number = 1

        self.scene_pos = None

        self.first_click = None
        self.temp_rect = None

        self.load_status = 0  # 0: neutral, 1: select beam, 2: delete beam
        self.other_button = None

        self.rect_prop = {}  # Dictionary to store coordinates of rectangles

        # note spacing x = width, spacing y = height

    def draw_load_mousePress(self, main_self, event, properties=None):
        if properties:  # for copy/load
            coordinate = properties["coordinate"]
            x1, y1 = coordinate[0]
            x2, y2 = coordinate[2]
            x1_main = min(x1, x2)
            x2_main = max(x1, x2)
            y1_main = min(y1, y2)
            y2_main = max(y1, y2)
            rect_x, rect_y, rect_w, rect_h = min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)

            rect_item = loadRectangle(rect_x, rect_y, rect_w, rect_h, self.rect_prop,
                                      self.toolBar.dialogPage2.all_set_load)
            # image = image_control(rect_x, rect_y, rect_w, rect_h, rect_item)
            # rect_item.image = image

            rect_item.setBrush(QBrush(QColor.fromRgb(222, 143, 111, 80)))
            rect_item.setPen(QPen(Qt.black))
            self.scene.addItem(rect_item)
            self.scene.removeItem(self.temp_rect)
            dialog = Choose_load_and_color(self.toolBar.dialogPage2.all_set_load)

            # result = dialog.exec()
            # dialog = ColorDialog(self)
            # result = dialog.exec()
            # print(dialog.color)
            # print(result)
            rect_item.setBrush(QColor(properties["color"]))
            print(f"Value chosen in combo box: {dialog.combo_box.currentText()}")
            if dialog.combo_box.currentText():
                load = self.toolBar.dialogPage2.all_set_load[
                    dialog.combo_box.currentText()]
            else:
                load = []

            # Save coordinates of the rectangle corners
            self.rect_prop[rect_item] = {"label": properties["label"],
                                         "coordinate": [(x1_main, y1_main), (x1_main, y2_main),
                                                        (x2_main, y2_main), (x2_main, y1_main)],
                                         "color": properties["color"],
                                         "load": properties["load"]}
            joist_line_creator(self.rect_prop[rect_item])
            print(self.rect_prop)
            self.load_number += 1

            # Add corner points to snap points

            for point in self.rect_prop[rect_item]["coordinate"]:
                self.snapPoint.add_point(point[0], point[1])

            self.temp_rect = None
            self.first_click = None
        else:
            if event.button() == Qt.LeftButton:
                self.scene_pos = scene_pos = main_self.mapToScene(event.pos())  # Use pos() with QMouseEvent
                if self.load_status == 1:
                    if not self.first_click and self.first_click != QPointF(0.000000, 0.000000):
                        self.first_click = self.snapPoint.snap(scene_pos)  # Snap to a nearby point if close
                        self.temp_rect = QGraphicsRectItem()
                        self.temp_rect.setPen(QPen(Qt.black))
                        # self.temp_rect.setBrush(QBrush(Qt.red))
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

                        rect_item = loadRectangle(rect_x, rect_y, rect_w, rect_h, self.rect_prop,
                                                  self.toolBar.dialogPage2.all_set_load)
                        # image = image_control(rect_x, rect_y, rect_w, rect_h, rect_item)
                        # rect_item.image = image

                        rect_item.setBrush(QBrush(QColor.fromRgb(222, 143, 111, 80)))
                        rect_item.setPen(QPen(Qt.black))
                        self.scene.addItem(rect_item)
                        self.scene.removeItem(self.temp_rect)
                        dialog = Choose_load_and_color(self.toolBar.dialogPage2.all_set_load)

                        result = dialog.exec()
                        # dialog = ColorDialog(self)
                        # result = dialog.exec()
                        # print(dialog.color)
                        # print(result)
                        rect_item.setBrush(QColor(dialog.color))
                        print(f"Value chosen in combo box: {dialog.combo_box.currentText()}")
                        if dialog.combo_box.currentText():
                            load = self.toolBar.dialogPage2.all_set_load[
                                dialog.combo_box.currentText()]
                        else:
                            load = []

                        # Save coordinates of the rectangle corners
                        self.rect_prop[rect_item] = {"label": dialog.combo_box.currentText(),
                                                     "coordinate": [(x1_main, y1_main), (x1_main, y2_main),
                                                                    (x2_main, y2_main), (x2_main, y1_main)],
                                                     "color": dialog.color,
                                                     "load": load}
                        joist_line_creator(self.rect_prop[rect_item])
                        print(self.rect_prop)
                        self.load_number += 1

                        # Add corner points to snap points

                        for point in self.rect_prop[rect_item]["coordinate"]:
                            self.snapPoint.add_point(point[0], point[1])

                        self.temp_rect = None
                        self.first_click = None
                elif self.load_status == 2:
                    # item = self.scene.itemAt(scene_pos, main_self.transform())
                    item = main_self.itemAt(event.position().toPoint())
                    if item and isinstance(item, loadRectangle):
                        # Delete the coordinates of the rectangle
                        if item in self.rect_prop:
                            # remove corner points to snap points
                            for point in self.rect_prop[item]["coordinate"]:
                                self.snapPoint.remove_point(point)

                            del self.rect_prop[item]
                        self.scene.removeItem(item)

    def draw_load_mouseMove(self, main_self, event):
        if self.first_click:
            pos = main_self.mapToScene(event.pos())
            # snapped_pos = self.snap_to_grid(pos)
            snapped_pos = self.snapPoint.snap(pos)
            # if snap to some point we don't need to check with snap line
            if pos == snapped_pos:
                snapped_pos = self.snapLine.snap(pos)
            width = snapped_pos.x() - self.first_click.x()
            height = snapped_pos.y() - self.first_click.y()

            x1, y1 = self.first_click.x(), self.first_click.y()
            x2, y2 = snapped_pos.x(), snapped_pos.y()
            rect_x, rect_y, rect_w, rect_h = min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)
            self.temp_rect.setRect(rect_x, rect_y, rect_w, rect_h)
            self.scene.addItem(self.temp_rect)
            print("fds")

            # self.scene.removeItem(self.temp_rect)

    # SLOT
    def load_selector(self):
        if self.other_button:
            post, beam, joist, shearWall, studWall = self.other_button
        if self.load_status == 0:
            self.load_status = 1
            self.load.load.setText("Draw Load")
            self.setCursor(Qt.CursorShape.UpArrowCursor)

            # DE ACTIVE OTHER BUTTONS
            if self.other_button:
                deActive(self, post, beam, joist, shearWall, studWall, self)
        elif self.load_status == 1:
            self.load_status = 2
            self.load.load.setText("Delete Load")
            self.setCursor(Qt.CursorShape.ArrowCursor)

            # DE ACTIVE OTHER BUTTONS
            if self.other_button:
                deActive(self, post, beam, joist, shearWall, studWall, self)
        elif self.load_status == 2:
            self.load_status = 0
            self.load.load.setText("LOAD MAP")
            self.setCursor(Qt.CursorShape.ArrowCursor)


class loadRectangle(QGraphicsRectItem):
    def __init__(self, rect_x, rect_y, rect_w, rect_h, rect_prop, all_load):
        super().__init__(rect_x, rect_y, rect_w, rect_h)
        self.image = None
        self.load_properties_page = None
        self.rect_prop = rect_prop
        self.all_load = all_load

    # CONTROL ON LOAD MAP
    def mousePressEvent(self, event):
        center = self.boundingRect().center().toTuple()
        # properties page open
        if event.button() == Qt.RightButton:  # Load Properties page
            height = self.boundingRect().height() - 1  # ATTENTION: I don't know why but this method return height + 1
            width = self.boundingRect().width() - 1  # ATTENTION: I don't know why but this method return width + 1
            load_joint_coordinates = find_coordinate(center[0], center[1], width, height)
            self.load_properties_page = LoadProperties(self, self.rect_prop, center, load_joint_coordinates,
                                                       self.all_load, self.scene())
            self.load_properties_page.show()


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
