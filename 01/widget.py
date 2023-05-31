from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsLineItem


class GridWidget(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        pen = QPen(Qt.black, 1, Qt.SolidLine)

        for i in range(5):
            line_horizontal = QGraphicsLineItem(0, i * 30, 150, i * 30)
            line_horizontal.setPen(pen)
            self.scene.addItem(line_horizontal)

            line_vertical = QGraphicsLineItem(i * 30, 0, i * 30, 150)
            line_vertical.setPen(pen)
            self.scene.addItem(line_vertical)

        self.setRenderHint(QPainter.Antialiasing)
