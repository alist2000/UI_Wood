from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from mouse import SelectableLineItem


class GridWidget(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        pen = QPen(Qt.black, 1, Qt.SolidLine)

        for i in range(5):
            line_vertical = SelectableLineItem(0, i * 30, self.width(), (i + 1) * 30)
            line_vertical.setPen(pen)
            self.scene.addItem(line_vertical)

            line_horizontal = SelectableLineItem(i * 30, 0, (i + 1) * 30, self.height())
            line_horizontal.setPen(pen)
            self.scene.addItem(line_horizontal)

        self.setRenderHint(QPainter.Antialiasing)
