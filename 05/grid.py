from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from mouse import SelectableLineItem
from post import PostArea


class GridWidget(QGraphicsView):
    def __init__(self, h_grid, v_grid, y, x, post, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)  # Corrected attribute
        self.clickable_area_enabled = True
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

        post_area_instance = PostArea(x_list, y_list, self.x, self.y, self.scene, post)
        # self.allowed_clickable_areas = post_area_instance.allowed_clickable_areas

    # def mousePressEvent(self, event):
    #     if self.clickable_area_enabled:
    #         clicked_position = event.position().toPoint()
    #         print(clicked_position)
    #         for area in self.allowed_clickable_areas:
    #             if area.contains(clicked_position):
    #                 print(area)
    #                 # Perform your desired action here
    #                 print(f"Clicked within the allowed clickable area: {clicked_position}")
    #                 break
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
            self.x = [400]  # 20 ft or 20 m
        if self.y:
            # better appearance
            self.y = [i * 20 for i in self.y]
        else:
            self.y = [400]  # 20 ft or 20 m

        return self.x, self.y
