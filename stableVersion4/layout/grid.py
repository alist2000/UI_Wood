from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QPainter, QBrush
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem

from UI_Wood.stableVersion4.mouse import SelectableLineItem

from UI_Wood.stableVersion4.post_new import magnification_factor


class GridWidget(QGraphicsView):
    def __init__(self, h_grid_number, v_grid_number, y, x, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.lineLabels = []
        self.x = x
        self.y = y

        self.current_rect = None
        self.start_pos = None

        # control inputs
        self.x, self.y = self.control_inputs()

        width_manual = sum(self.x)
        height_manual = sum(self.y)
        x_list, y_list = self.edit_spacing()

        pen = QPen(Qt.black, 1, Qt.SolidLine)

        for i in range(h_grid_number):
            line_horizontal = SelectableLineItem(0, y_list[i], width_manual, y_list[i])
            # snap
            line_horizontal.setPen(pen)
            self.scene.addItem(line_horizontal)
            label = get_string_value(i + 1)
            self.lineLabels.append(label)
        for i in range(v_grid_number):
            line_vertical = SelectableLineItem(x_list[i], 0, x_list[i], height_manual)
            # snap
            line_vertical.setPen(pen)
            self.scene.addItem(line_vertical)

            self.lineLabels.append(str(i + 1))

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

    def control_inputs(self):
        if self.x:
            # better appearance
            self.x = [i * magnification_factor for i in self.x]
        else:
            self.x = [400]  # 20 ft or 20 m
        if self.y:
            # better appearance
            self.y = [i * magnification_factor for i in self.y]
        else:
            self.y = [400]  # 20 ft or 20 m

        return self.x, self.y


def get_string_value(num):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = ''
    while num > 0:
        num, remainder = divmod(num - 1, 26)
        result = alphabet[remainder] + result
    return result
