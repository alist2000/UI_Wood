from PySide6.QtCore import Qt, Signal, QObject, QEvent
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QTabWidget, QGraphicsRectItem, QWidget, QPushButton, QDialog, QDialogButtonBox, \
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QGraphicsItem

from DeActivate import deActive
from post_prop import PostProperties

import itertools

magnification_factor = 40


class SignalHandler(QObject):
    button_clicked = Signal()

    def emit_button_clicked(self):
        self.button_clicked.emit()


signal_handler = SignalHandler()


class PostButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.post = QPushButton("POST")  # Create an instance of SignalHandler
        # Assuming you have a button called `push_button`, connect its clicked signal to the custom signal
        self.post.clicked.connect(signal_handler.emit_button_clicked)


class PostDrawing(QGraphicsRectItem):
    def __init__(self, postButton, x, y, scene, snapPoint, snapLine):
        super().__init__()
        self.postButton = postButton
        self.scene = scene
        self.snapPoint = snapPoint
        self.snapLine = snapLine
        # self.post_dimension = min(min(x), min(y)) / 8  # Set post dimension
        self.post_dimension = magnification_factor  # Set post dimension

        self.post_drawing_mode = 0
        self.preview_rect_item = None
        self.scene_pos = None
        self.other_button = None

        # Label
        self.post_number = 1

        self.post_prop = {}  # Dictionary to store coordinates of rectangles

    def draw_post_mousePress(self, main_self, event, properties=None):
        if properties:  # for copy/load
            coordinate = properties["coordinate"]
            x, y = coordinate
            rect = self.add_rectangle(x, y)
            self.post_prop[rect] = {"label": f"P{self.post_number}", "coordinate": (x, y),
                                    "load": {"point": properties["load"]["point"]},
                                    "wall_width": properties["wall_width"]}
            self.snapPoint.add_point(x, y)
            self.post_number += 1
            return True
        else:
            if event.button() == Qt.LeftButton and self.post_drawing_mode == 1:
                pos = main_self.mapToScene(event.pos())
                snapped_pos = self.snapPoint.snap(pos)
                rect = self.add_rectangle(snapped_pos.x(), snapped_pos.y())
                self.post_prop[rect] = {"label": f"P{self.post_number}", "coordinate": snapped_pos.toTuple(),
                                        "load": {"point": []}, "wall_width": "6 in"}
                self.snapPoint.add_point(snapped_pos.x(), snapped_pos.y())
                self.post_number += 1
                return True
            elif event.button() == Qt.LeftButton and self.post_drawing_mode == 2:
                # item = self.scene.itemAt(scene_pos, main_self.transform())
                item = main_self.itemAt(event.position().toPoint())
                if item and isinstance(item, CustomRectItem):
                    # Delete the coordinates of the rectangle
                    if item in self.post_prop:
                        self.snapPoint.remove_point(self.post_prop[item]["coordinate"])
                        del self.post_prop[item]
                    self.scene.removeItem(item)

    def draw_post_mouseMove(self, main_self, event):
        pos = main_self.mapToScene(event.pos())
        snapped_pos = self.snapPoint.snap(pos)
        if self.post_drawing_mode == 1:
            self.update_preview_rect(snapped_pos.x(), snapped_pos.y())
        return True

    def add_rectangle(self, x, y):
        rect_width = rect_height = self.post_dimension
        rect_item = CustomRectItem(self.post_prop)
        rect_item.setRect(x - rect_width / 2, y - rect_height / 2, rect_width, rect_height)
        self.scene.addItem(rect_item)
        return rect_item

    def update_preview_rect(self, x, y):
        if self.preview_rect_item is None:
            self.preview_rect_item = CustomRectItem(self.post_prop)
            self.preview_rect_item.setOpacity(0.5)
            self.scene.addItem(self.preview_rect_item)

        rect_width = rect_height = self.post_dimension
        self.preview_rect_item.setRect(x - rect_width / 2, y - rect_height / 2, rect_width, rect_height)

    def remove_preview_rect(self):
        if self.preview_rect_item:
            self.scene.removeItem(self.preview_rect_item)
            self.preview_rect_item = None

        # SLOT OF POST BUTTON

    def post_drawing_control(self):
        if self.other_button:
            beam, joist, shearWall, studWall, load = self.other_button
        if self.post_drawing_mode == 0:
            self.post_drawing_mode = 1
            self.postButton.post.setText("Draw Post")
            self.setCursor(Qt.CursorShape.CrossCursor)

            # DE ACTIVE OTHER BUTTONS
            if self.other_button:
                deActive(self, self, beam, joist, shearWall, studWall, load)
        elif self.post_drawing_mode == 1:
            self.post_drawing_mode = 2
            self.postButton.post.setText("Delete Post")
            self.setCursor(Qt.CursorShape.ArrowCursor)

            # DE ACTIVE OTHER BUTTONS
            if self.other_button:
                deActive(self, self, beam, joist, shearWall, studWall, load)
            self.remove_preview_rect()
        elif self.post_drawing_mode == 2:
            self.post_drawing_mode = 0
            self.postButton.post.setText("POST")
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.remove_preview_rect()

        # print(self.Post_Position)

    # def mousePressEvent(self, event):
    #     pos = self.associated_rect.boundingRect().center().toTuple()
    #     # properties page open
    #     if event.button() == Qt.RightButton:
    #         self.post_properties_page = PostProperties(pos, self.Post_Position, self.post_label)
    #         self.post_properties_page.show()
    #     else:  # select/deselect
    #         # self.associated_rect.setVisible(not self.associated_rect.isVisible())
    #         if self.post_drawing_mode:
    #             print(self.post_drawing_mode)
    #             visibility = True if self.post_drawing_mode == 1 else False
    #             self.associated_rect.setVisible(visibility)
    #             if self.post_drawing_mode == 1:
    #                 self.Post_Position.add(pos)
    #                 # self.post_label.add(f"P{len(self.Post_Position)}")
    #                 self.post_label.add(f"P{pos}")
    #                 print(self.post_label)
    #             else:
    #                 print(pos)
    #                 print(self.Post_Position)
    #                 try:
    #                     self.post_label.remove(f"P{pos}")
    #                     self.Post_Position.remove(pos)
    #
    #                 except:
    #                     print("remove fail")
    # def mouseDoubleClickEvent(self, event):
    #     pos = self.associated_rect.boundingRect().center().toTuple()
    #     self.post_properties_page = PostProperties(pos, self.Post_Position)
    #     self.post_properties_page.show()


class CustomRectItem(QGraphicsRectItem):
    def __init__(self, post_prop, *args, **kwargs):
        super(CustomRectItem, self).__init__(*args, **kwargs)
        # self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setBrush(QBrush(QColor("#E76161")))

        # Properties
        self.post_properties_page = None
        self.post_prop = post_prop

    def mousePressEvent(self, event):
        pos = self.boundingRect().center().toTuple()
        # properties page open
        if event.button() == Qt.RightButton:
            self.post_properties_page = PostProperties(self, self.post_prop)
            self.post_properties_page.show()
