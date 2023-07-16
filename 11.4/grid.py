from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QPainter, QBrush
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem

from Beam import beamDrawing
from ShearWall import shearWallDrawing
from StudWall import studWallDrawing
from back.input import receiver
from output.beam_output import beam_output
from joist_new import joistDrawing
from load_map import loadDrawing
from mouse import SelectableLineItem
from post_new import PostDrawing
# from main import magnification_factor
from post_new import magnification_factor
from snap import SnapLine, SnapPoint
from menuBar import Image, visual


class GridWidget(QGraphicsView):
    def __init__(self, h_grid_number, v_grid_number, y, x, post, joist, beam, shearWall, studWall, run, shapes, slider,
                 load, toolBar,
                 parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)  # Corrected attribute
        self.clickable_area_enabled = True
        # self.lastPanPoint = QPoint()
        self.menu = Image(self, slider)
        self.dragging_pixmap = False

        self.grid = {"vertical": [], "horizontal": []}
        self.x = x
        self.y = y

        # ALL SHAPES ADD HERE FOR SAVE AND LOAD
        self.shapes = shapes

        # self.beam = beam

        self.current_rect = None
        self.start_pos = None

        # control inputs
        self.x, self.y = self.control_inputs()
        self.snap_distance = min(min(self.x), min(self.y)) / 25  # Set the grid size

        # CREATE INSTANCE FOR SNAP
        snapPoint = SnapPoint()
        snapPoint.set_snap_distance(self.snap_distance)
        snapLine = SnapLine()
        snapLine.set_snap_distance(self.snap_distance)

        width_manual = sum(self.x)
        height_manual = sum(self.y)
        x_list, y_list = self.edit_spacing()
        print("xlist", x_list)
        print("ylist", y_list)

        pen = QPen(Qt.black, 1, Qt.SolidLine)

        for i in range(h_grid_number):
            line_horizontal = SelectableLineItem(0, y_list[i], width_manual, y_list[i])
            # snap
            snapLine.add_line((0, y_list[i]), (width_manual, y_list[i]))
            line_horizontal.setPen(pen)
            self.scene.addItem(line_horizontal)
            self.grid["horizontal"].append({
                "label": f"{i + 1}",
                "position": y_list[i]
            })
        for i in range(v_grid_number):
            line_vertical = SelectableLineItem(x_list[i], 0, x_list[i], height_manual)
            # snap
            snapLine.add_line((x_list[i], 0), (x_list[i], height_manual))
            line_vertical.setPen(pen)
            self.scene.addItem(line_vertical)
            label = get_string_value(i + 1)

            self.grid["vertical"].append({
                "label": label,
                "position": x_list[i]
            })

        # Add Snap Points (grid joint points)
        for x in x_list:
            for y in y_list:
                snapPoint.add_point(x, y)

        self.setRenderHint(QPainter.Antialiasing)

        self.joist_instance = joistDrawing(joist, self.scene, snapPoint, snapLine)
        self.load_instance = loadDrawing(load, self.scene, snapPoint, snapLine, toolBar)
        self.post_instance = PostDrawing(post, self.x, self.y, self.scene, snapPoint, snapLine)
        self.shearWall_instance = shearWallDrawing(shearWall, self.x, self.y, self.grid, self.scene, snapPoint,
                                                   snapLine)
        self.beam_instance = beamDrawing(beam, self.x, self.y, self.scene, self.post_instance, self.shearWall_instance,
                                         snapPoint, snapLine)
        self.studWall_instance = studWallDrawing(studWall, self.x, self.y, self.scene, snapPoint, snapLine)

        # CONTROL ON OTHER BUTTONS
        self.post_instance.other_button = [self.beam_instance, self.joist_instance, self.shearWall_instance,
                                           self.studWall_instance, self.load_instance]
        self.beam_instance.other_button = [self.post_instance, self.joist_instance, self.shearWall_instance,
                                           self.studWall_instance, self.load_instance]
        self.joist_instance.other_button = [self.post_instance, self.beam_instance, self.shearWall_instance,
                                            self.studWall_instance, self.load_instance]
        self.load_instance.other_button = [self.post_instance, self.beam_instance, self.joist_instance,
                                           self.shearWall_instance,
                                           self.studWall_instance]
        self.shearWall_instance.other_button = [self.post_instance, self.beam_instance, self.joist_instance,
                                                self.studWall_instance, self.load_instance]
        self.studWall_instance.other_button = [self.post_instance, self.beam_instance, self.joist_instance,
                                               self.shearWall_instance, self.load_instance]

        # CRETE VISUAL MENU
        self.visual_setting = visual(self, self.post_instance.post_prop, self.beam_instance.beam_rect_prop,
                                     self.joist_instance.rect_prop,
                                     self.shearWall_instance.shearWall_rect_prop,
                                     self.studWall_instance.studWall_rect_prop,
                                     self.load_instance.rect_prop)

        beam.beam.clicked.connect(self.beam_instance.beam_selector)
        joist.joist.clicked.connect(self.joist_instance.joist_selector)
        load.load.clicked.connect(self.load_instance.load_selector)
        post.post.clicked.connect(self.post_instance.post_drawing_control)
        shearWall.shearWall.clicked.connect(self.shearWall_instance.shearWall_selector)
        studWall.studWall.clicked.connect(self.studWall_instance.studWall_selector)

        run.clicked.connect(self.run_control)

    # SLOT RUN BUTTON
    def run_control(self):
        data = receiver(self.grid, self.post_instance.post_prop, self.beam_instance.beam_rect_prop,
                        self.joist_instance.rect_prop,
                        self.shearWall_instance.shearWall_rect_prop, self.studWall_instance.studWall_rect_prop,
                        self.load_instance.rect_prop)

        print("FIRST BEAM")
        for i in data.beam_properties.beam.values():
            print(i)

        beamOutput = beam_output(data.beam_properties.beam)
        print("FINAL BEAM OUTPUT")
        for i in beamOutput.beamProperties.values():
            print(i)

        # for loadItem in self.load_instance.rect_prop.keys():
        #     loadItem.setVisible(not loadItem.isVisible())
        # for i in data.joist_properties.joist.values():
        #     print(i)
        # for i in data.shearWall_properties.shearWall.values():
        #     print(i)
        print(self.grid)
        print(self.joist_instance.rect_prop)
        print("RUN CLICK", data.midline.midline_dict)
        for i in data.midline.midline_dict:
            print(i)

    def wheelEvent(self, event):
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        # Save the scene pos
        oldPos = self.mapToScene(event.position().toPoint())

        # Zoom
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.mapToScene(event.position().toPoint())

        # Move scene to old position
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

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
        elif self.load_instance.load_status:  # CONTROL LOAD MAP
            # 1 (draw mode) and 2(delete mode)
            self.load_instance.draw_load_mousePress(self, event)
        else:
            if self.menu.pixmapItem:
                # First check if the pixmap is under the mouse cursor when pressed
                if self.menu.pixmapItem.contains(self.mapToScene(event.pos())):
                    self.dragging_pixmap = True  # set a flag indicating that pixmap dragging is in process
                else:
                    self.dragging_pixmap = False
                    self.scene.clearSelection()
                #     # Call base function if pixmap is not intended to be moved
                #     super().mousePressEvent(event)

                #   self.scene.clearSelection()

        # data = receiver(self.grid, self.post_instance.post_prop, self.beam_instance.beam_rect_prop,
        #                 self.joist_instance.rect_prop,
        #                 self.shearWall_instance.shearWall_rect_prop, self.studWall_instance.studWall_rect_prop,
        #                 self.load_instance.rect_prop)
        # self.lastPanPoint = event.position().toPoint()
        # self.setCursor(Qt.ClosedHandCursor)
        # self.scene.clearSelection()

    def mouseMoveEvent(self, event):
        # if not self.lastPanPoint.isNull():
        #     delta = self.mapToScene(self.lastPanPoint) - self.mapToScene(event.position().toPoint())
        #     self.lastPanPoint = event.position().toPoint()
        #     self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta.x())
        #     self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta.y())
        # else:
        #     super().mouseMoveEvent(event)

        if self.beam_instance.beam_select_status == 1:  # CONTROL BEAM
            self.beam_instance.draw_beam_mouseMove(self, event)
        elif self.joist_instance.joist_status == 1:
            self.joist_instance.draw_joist_mouseMove(self, event)
        elif self.post_instance.post_drawing_mode:
            self.post_instance.draw_post_mouseMove(self, event)
        elif self.shearWall_instance.shearWall_select_status == 1:  # CONTROL SHEAR WALL
            self.shearWall_instance.draw_shearWall_mouseMove(self, event)
        elif self.studWall_instance.studWall_select_status == 1:  # CONTROL STUD WALL
            self.studWall_instance.draw_studWall_mouseMove(self, event)
        elif self.load_instance.load_status == 1:
            self.load_instance.draw_load_mouseMove(self, event)

            # If pixmap dragging flag is set, move pixmap
        if self.menu.pixmapItem:
            if self.menu.pixmapItem.isSelected() and self.menu.unlock:
                # Get the position of the mouse event in scene coordinates
                pos = self.mapToScene(event.pos())
                # Update the position of the pixmapItem
                self.menu.pixmapItem.setPos(pos)

        # else:
        #     # Call base function  if pixmap is not intended to be moved
        #     super().mouseMoveEvent(event)

    # def mouseReleaseEvent(self, event):
    #     # reset pixmap dragging flag
    #     self.dragging_pixmap = False
    #     self.scene.clearSelection()

    # def mouseReleaseEvent(self, event):
    #     self.lastPanPoint = QPoint()
    #     self.setCursor(Qt.ArrowCursor)

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


def get_string_value(num):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = ''
    while num > 0:
        num, remainder = divmod(num - 1, 26)
        result = alphabet[remainder] + result
    return result
