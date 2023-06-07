from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QTabWidget, QGraphicsRectItem, QWidget, QPushButton, QDialog, QDialogButtonBox, \
    QVBoxLayout, QHBoxLayout, QLabel

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
        # self.post.clicked.connect(self.post_selector)
        # self.post_select = False

    # # SLOT
    # def post_selector(self):
    #     print("POST BUTTON CLICKED!")
    #     self.post_select = not self.post_select
    #     print(self.post_select)


class PostArea:
    def __init__(self, x, y, spacing_x, spacing_y, scene, post_select):
        self.postButton = post_select
        # note spacing x = width, spacing y = height
        min_spacing = min(min(spacing_x), min(spacing_y))
        # limit post area based on minimum spacing
        values = [
            (x[i] - min_spacing / 8, y[j] - min_spacing / 8,
             (min_spacing / 4),
             (min_spacing / 4))
            for i, j in itertools.product(range(len(x)), range(len(y)))]
        # values = [
        #     (x[i] - spacing_x[i if i == 0 else i - 1] / 8, y[j] - spacing_y[j if j == 0 else j - 1] / 8,
        #      (spacing_x[i if i == 0 else i - 1] / 4) if i == len(x) - 1 else (spacing_x[i if i == 0 else i - 1] / 8) + (
        #              spacing_x[i] / 8),
        #      (spacing_y[j if j == 0 else j - 1] / 4) if j == len(y) - 1 else (spacing_y[j if j == 0 else j - 1] / 8) + (
        #              spacing_y[j] / 8))
        #     for i, j in itertools.product(range(len(x)), range(len(y)))
        # ]
        self.coordinate = values
        self.Post_Position = Post_Position = set()
        for i in values:
            rect = QGraphicsRectItem()
            rect.setRect(i[0], i[1], i[2], i[3])
            rect.setBrush(QBrush(QColor("#E76161")))
            rect.setPen(QPen(Qt.black))
            scene.addItem(rect)
            click_detector1 = ClickableRectItem(i[0], i[1], i[2], i[3], rect, post_select, Post_Position)
            click_detector1.setBrush(QBrush(Qt.transparent))
            click_detector1.setPen(QPen(Qt.transparent))
            scene.addItem(click_detector1)

        self.clickable_area_enabled = True


class ClickableRectItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, associated_rect, post, Post_Position):
        super().__init__(x, y, width, height)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.associated_rect = associated_rect
        self.associated_rect.setVisible(False)
        self.post_select = 0
        self.post = post
        signal_handler.button_clicked.connect(self.post_selector)
        # post.post.clicked.connect(self.post_selector)

        self.Post_Position = Post_Position

        self.post_properties_page = None

    # SLOT OF POST BUTTON
    def post_selector(self):
        if self.post_select == 0:
            self.post_select = 1
            self.post.post.setText("Select Post")
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif self.post_select == 1:
            self.post_select = 2
            self.post.post.setText("Delete Post")
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif self.post_select == 2:
            self.post_select = 0
            self.post.post.setText("POST")
            self.setCursor(Qt.CursorShape.ArrowCursor)
        print(self.Post_Position)

    def mousePressEvent(self, event):
        pos = self.associated_rect.boundingRect().center().toTuple()
        # properties page open
        if event.button() == Qt.RightButton:
            self.post_properties_page = PostProperties(pos, self.Post_Position)
            self.post_properties_page.show()
        else:  # select/deselect
            # self.associated_rect.setVisible(not self.associated_rect.isVisible())
            if self.post_select:
                visibility = True if self.post_select == 1 else False
                self.associated_rect.setVisible(visibility)
                if self.post_select == 1:
                    self.Post_Position.add(pos)
                else:
                    try:
                        self.Post_Position.remove(pos)
                    except:
                        pass
    # def mouseDoubleClickEvent(self, event):
    #     pos = self.associated_rect.boundingRect().center().toTuple()
    #     self.post_properties_page = PostProperties(pos, self.Post_Position)
    #     self.post_properties_page.show()


class PostProperties(QDialog):
    def __init__(self, position, Post_Position, parent=None):
        super().__init__(parent)
        self.position = position
        self.Post_position_list = Post_Position
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
        label1 = QLabel("Global X")
        x = QLabel(f"{self.position[0] / magnification_factor}")
        label2 = QLabel("Global Y")
        y = QLabel(f"{self.position[1] / magnification_factor}")

        label3 = QLabel("Post Exist")

        # control post existence
        if self.position in self.Post_position_list:
            post_exist = QLabel("Yes")
        else:
            post_exist = QLabel("No")

        # LAYOUT
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(label1)
        h_layout1.addWidget(x)
        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(label2)
        h_layout2.addWidget(y)
        h_layout3 = QHBoxLayout()
        h_layout3.addWidget(label3)
        h_layout3.addWidget(post_exist)
        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout1)
        v_layout.addLayout(h_layout2)
        v_layout.addLayout(h_layout3)
        tab.setLayout(v_layout)
