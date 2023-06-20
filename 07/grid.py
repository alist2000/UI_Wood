from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QPainter, QBrush
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem
from mouse import SelectableLineItem
from post import PostArea, signal_handler
from joist import JoistArea
from joist_new import joistDrawing
from Beam import beamDrawing

from snap import SnapLine, SnapPoint

# from main import magnification_factor
from post import magnification_factor


class GridWidget(QGraphicsView):
    def __init__(self, h_grid, v_grid, y, x, post, joist, beam, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)  # Corrected attribute
        self.clickable_area_enabled = True
        self.x = x
        self.y = y

        # self.beam = beam

        self.current_rect = None
        self.start_pos = None

        # control inputs
        self.x, self.y = self.control_inputs()
        self.snap_distance = min(min(self.x), min(self.y)) / 15  # Set the grid size

        # CREATE INSTANCE FOR SNAP
        snapPoint = SnapPoint()
        snapPoint.set_snap_distance(self.snap_distance)
        snapLine = SnapLine()
        snapLine.set_snap_distance(self.snap_distance)

        width_manual = sum(self.x)
        height_manual = sum(self.y)
        x_list, y_list = self.edit_spacing()

        pen = QPen(Qt.black, 1, Qt.SolidLine)

        for i in range(h_grid):
            line_horizontal = SelectableLineItem(0, y_list[i], width_manual, y_list[i])
            # snap
            snapLine.add_line((0, y_list[i]), (width_manual, y_list[i]))
            line_horizontal.setPen(pen)
            self.scene.addItem(line_horizontal)
        for i in range(v_grid):
            line_vertical = SelectableLineItem(x_list[i], 0, x_list[i], height_manual)
            # snap
            snapLine.add_line((x_list[i], 0), (x_list[i], height_manual))
            line_vertical.setPen(pen)
            self.scene.addItem(line_vertical)

        # Add Snap Points (grid joint points)
        for x in x_list:
            for y in y_list:
                snapPoint.add_point(x, y)

        self.setRenderHint(QPainter.Antialiasing)

        # self.Joist_area_instance = JoistArea(x_list, y_list, self.x, self.y, self.scene, joist)
        self.joist_instance = joistDrawing(joist, self.scene, snapPoint, snapLine)
        post_area_instance = PostArea(x_list, y_list, self.x, self.y, self.scene, post)
        self.beam_instance = beamDrawing(beam, self.x, self.y, self.scene, post_area_instance, snapPoint, snapLine)
        beam.beam.clicked.connect(self.beam_instance.beam_selector)
        joist.joist.clicked.connect(self.joist_instance.joist_selector)

    def mousePressEvent(self, event):
        if self.beam_instance.beam_select_status:  # CONTROL BEAM -> now beam select can
            # one (draw mode) and 2(delete mode)
            self.beam_instance.draw_beam_mousePress(self, event)
        elif self.joist_instance.joist_status:
            self.joist_instance.draw_joist_mousePress(self, event)

    def mouseMoveEvent(self, event):
        if self.beam_instance.beam_select_status == 1:  # CONTROL BEAM
            self.beam_instance.draw_beam_mouseMove(self, event)
        elif self.joist_instance.joist_status == 1:
            self.joist_instance.draw_joist_mouseMove()

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


class Rectangle(QGraphicsRectItem):
    def __init__(self, x, y):
        super().__init__(x, y, 0, 0)
        self.setPen(QPen(Qt.blue, 2))  # Set the border color to blue
        self.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))  # Set the fill color to transparent
