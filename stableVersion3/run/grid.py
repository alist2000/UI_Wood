from UI_Wood.stableVersion3.post_new import magnification_factor
from UI_Wood.stableVersion3.mouse import SelectableLineItem
from PySide6.QtGui import QPen
from PySide6.QtCore import Qt


class GridDraw:
    def __init__(self, h_grid_number, v_grid_number, y, x):
        self.h_grid_number = h_grid_number
        self.v_grid_number = v_grid_number
        self.y = y
        self.x = x
        self.x, self.y = self.control_inputs()

    def Draw(self, scene):
        width_manual = sum(self.x)
        height_manual = sum(self.y)
        x_list, y_list = self.edit_spacing()
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        for i in range(self.h_grid_number):
            line_horizontal = SelectableLineItem(0, y_list[i], width_manual, y_list[i])
            # snap
            line_horizontal.setPen(pen)
            scene.addItem(line_horizontal)

        for i in range(self.v_grid_number):
            line_vertical = SelectableLineItem(x_list[i], 0, x_list[i], height_manual)
            # snap
            line_vertical.setPen(pen)
            scene.addItem(line_vertical)

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
