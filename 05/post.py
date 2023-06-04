from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QBrush
from PySide6.QtWidgets import QGraphicsScene, QGraphicsRectItem, QWidget, QPushButton

import itertools


class PostButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.post = QPushButton("POST")
        # self.post.clicked.connect(self.post_selector)
        # self.post_select = False

    # # SLOT
    # def post_selector(self):
    #     print("POST BUTTON CLICKED!")
    #     self.post_select = not self.post_select
    #     print(self.post_select)


class PostArea:
    def __init__(self, x, y, spacing_x, spacing_y, scene, post_select):
        # note spacing x = width, spacing y = height
        values = [
            (x[i] - spacing_x[i if i == 0 else i - 1] / 8, y[j] - spacing_y[j if j == 0 else j - 1] / 8,
             (spacing_x[i if i == 0 else i - 1] / 4) if i == len(x) - 1 else (spacing_x[i if i == 0 else i - 1] / 8) + (
                     spacing_x[i] / 8),
             (spacing_y[j if j == 0 else j - 1] / 4) if j == len(y) - 1 else (spacing_y[j if j == 0 else j - 1] / 8) + (
                     spacing_y[j] / 8))
            for i, j in itertools.product(range(len(x)), range(len(y)))
        ]
        self.coordinate = values
        self.Post_Position = Post_Position = set()
        for i in values:
            rect = QGraphicsRectItem()
            rect.setRect(i[0], i[1], i[2], i[3])
            rect.setBrush(QBrush(Qt.white))
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
        self.post_select = False
        post.post.clicked.connect(self.post_selector)

        self.Post_Position = Post_Position

    # SLOT
    def post_selector(self):
        self.post_select = not self.post_select
        print(self.Post_Position)

    def mousePressEvent(self, event):
        # self.associated_rect.setVisible(not self.associated_rect.isVisible())
        self.associated_rect.setVisible(self.post_select)
        pos = self.associated_rect.boundingRect().center().toTuple()
        if self.post_select:
            self.Post_Position.add(pos)
        else:
            try:
                self.Post_Position.remove(pos)
            except:
                pass


