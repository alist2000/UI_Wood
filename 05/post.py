from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QWidget, QPushButton

from mouse import SelectableLineItem


class PostButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.post = QPushButton("POST")
        self.post.clicked.connect(self.post_selector)

    # SLOT
    def post_selector(self):
        print("POST BUTTON CLICKED!")


class PostArea(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.allowed_clickable_areas = [
            QRectF(0, 0, 100, 100),
            QRectF(500, 500, 100, 222)
        ]
        self.clickable_area_enabled = True

    def mousePressEvent(self, event):
        if self.isInteractive():
            point = self.mapToScene(event.pos())
            print(f"You selected this area: {point}")
            # self.setInteractive(False)
            self.setCursor(Qt.CursorShape.CrossCursor)
        super().mousePressEvent(event)
