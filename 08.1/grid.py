from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QPainter, QBrush
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem
from mouse import SelectableLineItem
from post_new import PostDrawing
from joist_new import joistDrawing
from Beam import beamDrawing
from ShearWall import shearWallDrawing
from StudWall import studWallDrawing

from snap import SnapLine, SnapPoint

# from main import magnification_factor
from post_new import magnification_factor

from back.input import receiver


class GridWidget(QGraphicsView):
    def __init__(self, h_grid, v_grid, y, x, post, joist, beam, shearWall, studWall, run, parent=None):
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

        self.joist_instance = joistDrawing(joist, self.scene, snapPoint, snapLine)
        self.post_instance = PostDrawing(post, self.x, self.y, self.scene, snapPoint, snapLine)
        self.shearWall_instance = shearWallDrawing(shearWall, self.x, self.y, self.scene, snapPoint, snapLine)
        self.beam_instance = beamDrawing(beam, self.x, self.y, self.scene, self.post_instance, self.shearWall_instance,
                                         snapPoint, snapLine)
        self.studWall_instance = studWallDrawing(studWall, self.x, self.y, self.scene, snapPoint, snapLine)

        # CONTROL ON OTHER BUTTONS
        self.post_instance.other_button = [self.beam_instance, self.joist_instance, self.shearWall_instance,
                                           self.studWall_instance]
        self.beam_instance.other_button = [self.post_instance, self.joist_instance, self.shearWall_instance,
                                           self.studWall_instance]
        self.joist_instance.other_button = [self.post_instance, self.beam_instance, self.shearWall_instance,
                                            self.studWall_instance]
        self.shearWall_instance.other_button = [self.post_instance, self.beam_instance, self.joist_instance,
                                                self.studWall_instance]
        self.studWall_instance.other_button = [self.post_instance, self.beam_instance, self.joist_instance,
                                               self.shearWall_instance]

        beam.beam.clicked.connect(self.beam_instance.beam_selector)
        joist.joist.clicked.connect(self.joist_instance.joist_selector)
        post.post.clicked.connect(self.post_instance.post_drawing_control)
        shearWall.shearWall.clicked.connect(self.shearWall_instance.shearWall_selector)
        studWall.studWall.clicked.connect(self.studWall_instance.studWall_selector)

        run.clicked.connect(self.run_control)

    # SLOT RUN BUTTON
    def run_control(self):
        data = receiver(self.post_instance.post_prop, self.beam_instance.beam_rect_prop, self.joist_instance.rect_prop,
                        self.shearWall_instance.shearWall_rect_prop, self.studWall_instance.studWall_rect_prop)
        for i in data.beam_properties.beam.values():
            print(i)

    def mousePressEvent(self, event):
        if self.beam_instance.beam_select_status:  # CONTROL BEAM
            # 1 (draw mode) and 2(delete mode)
            self.beam_instance.draw_beam_mousePress(self, event)
        elif self.joist_instance.joist_status:  # CONTROL JOIST
            # 1 (draw mode) and 2(delete mode)
            self.joist_instance.draw_joist_mousePress(self, event)
        elif self.post_instance.post_drawing_mode:  # CONTROL POST
            # 1 (draw mode) and 2(delete mode)
            self.post_instance.draw_post_mousePress(self, event)
        elif self.shearWall_instance.shearWall_select_status:  # CONTROL SHEAR WALL
            # 1 (draw mode) and 2(delete mode)
            self.shearWall_instance.draw_shearWall_mousePress(self, event)
        elif self.studWall_instance.studWall_select_status:  # CONTROL STUD WALL
            # 1 (draw mode) and 2(delete mode)
            self.studWall_instance.draw_studWall_mousePress(self, event)

    def mouseMoveEvent(self, event):
        if self.beam_instance.beam_select_status == 1:  # CONTROL BEAM
            self.beam_instance.draw_beam_mouseMove(self, event)
        elif self.joist_instance.joist_status == 1:
            self.joist_instance.draw_joist_mouseMove()
        elif self.post_instance.post_drawing_mode:
            self.post_instance.draw_post_mouseMove(self, event)
        elif self.shearWall_instance.shearWall_select_status == 1:  # CONTROL SHEAR WALL
            self.shearWall_instance.draw_shearWall_mouseMove(self, event)
        elif self.studWall_instance.studWall_select_status == 1:  # CONTROL STUD WALL
            self.studWall_instance.draw_studWall_mouseMove(self, event)

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
