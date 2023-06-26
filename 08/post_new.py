from PySide6.QtCore import Qt, Signal, QObject, QEvent
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QTabWidget, QGraphicsRectItem, QWidget, QPushButton, QDialog, QDialogButtonBox, \
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QGraphicsItem

import itertools

magnification_factor = 20


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
        self.post_dimension = min(min(x), min(y)) / 8  # Set post dimension

        self.post_drawing_mode = 0
        self.preview_rect_item = None
        self.scene_pos = None

        # Label
        self.post_number = 1

        self.post_prop = {}  # Dictionary to store coordinates of rectangles

    def draw_post_mousePress(self, main_self, event):
        if event.button() == Qt.LeftButton and self.post_drawing_mode == 1:
            pos = main_self.mapToScene(event.pos())
            snapped_pos = self.snapPoint.snap(pos)
            rect = self.add_rectangle(snapped_pos.x(), snapped_pos.y())
            self.post_prop[rect] = {"label": f"P{self.post_number}", "coordinate": snapped_pos.toTuple()}
            print(self.post_prop)
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
        print(self.snapPoint.points)
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
        if self.post_drawing_mode == 0:
            self.post_drawing_mode = 1
            self.postButton.post.setText("Draw Post")
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif self.post_drawing_mode == 1:
            self.post_drawing_mode = 2
            self.postButton.post.setText("Delete Post")
            self.setCursor(Qt.CursorShape.ArrowCursor)
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
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
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


class PostProperties(QDialog):
    def __init__(self, rectItem, post_properties, parent=None):
        super().__init__(parent)
        self.rect = rectItem
        self.post_prop = post_properties
        self.setWindowTitle("Post Properties")
        self.setMinimumSize(200, 400)

        v_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setWindowTitle("Object Data")
        self.create_geometry_tab()

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)  # Change from dialog.accept to self.accept
        button_box.rejected.connect(self.reject)  # Change from dialog.reject to self.reject

        v_layout.addWidget(self.tab_widget)
        v_layout.addWidget(button_box)
        self.setLayout(v_layout)  # Change from dialog.setLayout to self.setLayout

    # Rest of the code remains the same

    # dialog.show()

    def create_geometry_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, f"Geometry")

        # Label
        print(self.post_prop)
        Post_label = self.post_prop[self.rect]["label"]
        label = QLabel("Post Label")
        post_label = QLabel(Post_label)

        # coordinate
        position = self.post_prop[self.rect]["coordinate"]
        label1 = QLabel("Global X")
        x = QLabel(f"{position[0] / magnification_factor}")
        label2 = QLabel("Global Y")
        y = QLabel(f"{position[1] / magnification_factor}")

        # label3 = QLabel("Post Exist")

        # control post existence
        # if self.position in self.Post_position_list:
        #     post_exist = QLabel("Yes")
        #     label = QLabel("Post Label")
        #     post_label = QLabel(list(self.post_label)[list(self.Post_position_list).index(self.position)])
        #     # post_label = QLabel(f"P{list(self.Post_position_list).index(self.position) + 1}")
        # else:
        #     post_exist = QLabel("No")
        #     label = QLabel("Post Label")
        #     post_label = QLabel("-")

        # LAYOUT
        h_layout0 = QHBoxLayout()
        h_layout0.addWidget(label)
        h_layout0.addWidget(post_label)
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(label1)
        h_layout1.addWidget(x)
        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(label2)
        h_layout2.addWidget(y)
        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout0)
        v_layout.addLayout(h_layout1)
        v_layout.addLayout(h_layout2)
        tab.setLayout(v_layout)
