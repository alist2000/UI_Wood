from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from mouse import SelectableLineItem
from post import PostArea


class GridWidget(QGraphicsView):
    def __init__(self, h_grid, v_grid, y, x, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)  # Corrected attribute
        self.setInteractive(True)

        self.x = x
        self.y = y

        # control inputs
        self.x, self.y = self.control_inputs()

        width_manual = sum(self.x)
        height_manual = sum(self.y)
        x_list, y_list = self.edit_spacing()

        pen = QPen(Qt.black, 1, Qt.SolidLine)

        for i in range(h_grid):
            line_horizontal = SelectableLineItem(0, y_list[i], width_manual, y_list[i])
            line_horizontal.setPen(pen)
            self.scene.addItem(line_horizontal)
        for i in range(v_grid):
            line_vertical = SelectableLineItem(x_list[i], 0, x_list[i], height_manual)
            line_vertical.setPen(pen)
            self.scene.addItem(line_vertical)

        self.setRenderHint(QPainter.Antialiasing)

        PostArea(self)

    # def mousePressEvent(self, event):
    #     if self.isInteractive():
    #         point = self.mapToScene(event.pos())
    #         print(f"You selected this area: {point}")
    #         # self.setInteractive(False)
    #         self.setCursor(Qt.CursorShape.CrossCursor)
    #     super().mousePressEvent(event)

    def edit_spacing(self):
        x = self.x
        y = self.y
        print(x, y)
        x_list = [0]
        y_list = [0]
        for i in range(len(x)):
            x_list.append(sum(x[:i + 1]))
        for i in range(len(y)):
            y_list.append(sum(y[:i + 1]))
        return x_list, y_list

    def control_inputs(self):
        if self.x:
            # better appearance
            self.x = [i * 20 for i in self.x]
        else:
            self.x = [400]
        if self.y:
            # better appearance
            self.y = [i * 20 for i in self.y]
        else:
            self.y = [400]

        return self.x, self.y
