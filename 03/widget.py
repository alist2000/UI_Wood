from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from mouse import SelectableLineItem


class GridWidget(QGraphicsView):
    def __init__(self, h_grid, v_grid, y, x, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.x = x
        self.y = y
        width_manual = sum(x)
        height_manual = sum(y)

        x, y = self.edit_spacing()

        pen = QPen(Qt.black, 1, Qt.SolidLine)

        for i in range(h_grid):
            line_horizontal = SelectableLineItem(0, y[i], width_manual, y[i])
            line_horizontal.setPen(pen)
            self.scene.addItem(line_horizontal)
        for i in range(v_grid):
            line_vertical = SelectableLineItem(x[i], 0, x[i], height_manual)
            line_vertical.setPen(pen)
            self.scene.addItem(line_vertical)

        self.setRenderHint(QPainter.Antialiasing)

    def edit_spacing(self):
        x = self.x
        y = self.y
        x_list = [0]
        y_list = [0]
        for i in range(len(x)):
            x_list.append(sum(x[:i + 1]))
        for i in range(len(y)):
            y_list.append(sum(y[:i + 1]))
        return x_list, y_list
