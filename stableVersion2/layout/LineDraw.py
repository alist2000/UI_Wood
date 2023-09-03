from UI_Wood.stableVersion2.post_new import magnification_factor, CustomRectItem
from UI_Wood.stableVersion2.Beam import Rectangle
from UI_Wood.stableVersion2.mouse import SelectableLineItem

from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import QRectF, Qt, QPointF, QLineF, QPoint, QSize, QRect
from PySide6.QtWidgets import QWidget, QGraphicsLineItem, QGraphicsProxyWidget, QLabel, QGraphicsPathItem, \
    QGraphicsRectItem
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath


class LineDraw:
    def __init__(self, coordinates, labels, scene, story, lineType):
        self.story = story
        self.scene = scene
        self.labels = labels
        self.lineType = lineType.capitalize()
        self.beam_width = magnification_factor / 2  # Set beam width
        self.shearWall_width = magnification_factor  # Set shearWall width, magnification = 1 ft or 1 m
        self.post_dimension = magnification_factor / 4  # Set post dimension
        self.studWall_width = magnification_factor / 3  # Set studWall width, magnification = 1 ft or 1 m

        for i, coordinate in enumerate(coordinates):
            if lineType == "beam":
                self.beamDraw(coordinate, i)
            elif lineType == "shearWall":
                self.shearWallDraw(coordinate, i)
            else:  # studWall
                self.studWallDraw(coordinate, i)

        self.saveImage()

        for item in scene.items():
            if item and (
                    isinstance(item, Rectangle) or isinstance(item, QGraphicsProxyWidget) or not isinstance(item,
                                                                                                            SelectableLineItem)):
                self.scene.removeItem(item)

    def saveImage(self):
        # Create a QPixmap to hold the image of the scene
        border_size = 10  # Border size in pixels
        # border_color = QColor(Qt.black)  # Set border as black color
        margin_size = 20  # Margin size in pixels

        # Get the rectangle that contains all items
        rect = self.scene.itemsBoundingRect()

        # Create QPixmap to hold the image of the scene with additional space for the border and margin
        pixmap = QPixmap(rect.width() + 2 * (border_size + margin_size),
                         rect.height() + 2 * (border_size + margin_size))
        # pixmap = QPixmap(rect.size().toSize())
        pixmap.fill(Qt.white)

        # Create a QPainter instance for the QPixmap
        painter = QPainter(pixmap)
        # Define a rectangle for the margin inside the border, and fill it with white color
        margin_rect = QRectF(border_size, border_size, rect.width() + 2 * margin_size,
                             rect.height() + 2 * margin_size)
        painter.fillRect(margin_rect, Qt.white)

        # Define rectangle for the scene inside the margin, and render the scene into this rectangle
        scene_rect = QRectF(border_size + margin_size, border_size + margin_size, rect.width(), rect.height())
        # self.render(painter, scene_rect, rect)

        # Render the scene onto the QPainter
        self.scene.render(painter, scene_rect, rect)

        # End the QPainter to apply the drawing to the QPixmap
        painter.end()

        # Save the QPixmap as an image file
        pixmap.save(f"images/output/{self.lineType}s_story{self.story + 1}.png")

    def beamDraw(self, coordinate, i):
        point1, point2 = coordinate
        x1, y1 = point1
        x2, y2 = point2
        self.current_rect = Rectangle(x1 - self.beam_width / 2,
                                      y1 - self.beam_width / 2, None)
        self.scene.addItem(self.current_rect)

        width = abs(x2 - x1)
        height = abs(y2 - y1)

        if abs(width) > abs(height):
            self.current_rect.setRect(min(x1, x2),
                                      y1 - self.beam_width / 2, abs(width), self.beam_width)
            direction = "E-W"

        else:
            self.current_rect.setRect(x1 - self.beam_width / 2,
                                      min(y1, y2), self.beam_width,
                                      abs(height))
            direction = "N-S"

        self.current_rect.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
        self.current_rect.setBrush(QBrush(QColor.fromRgb(245, 80, 80, 100), Qt.SolidPattern))
        BeamLabel((x1 + x2) / 2, (y1 + y2) / 2, self.scene, self.labels[i], direction)

    def shearWallDraw(self, coordinate, i):
        start, end = coordinate
        x1, y1 = start
        x2, y2 = end
        self.current_rect = Rectangle(x1,
                                      y1, None)
        self.scene.addItem(self.current_rect)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        if width > height:
            direction = "E-W"
        else:
            direction = "N-S"

        if direction == "E-W":
            self.current_rect.setRect(min(x1, x2),
                                      y1 - self.shearWall_width / 2, abs(width), self.shearWall_width)
        else:
            self.current_rect.setRect(x1 - self.shearWall_width / 2,
                                      min(y1, y2), self.shearWall_width,
                                      abs(height))

        center_left = QPoint(self.current_rect.boundingRect().left(),
                             self.current_rect.boundingRect().top() + self.current_rect.boundingRect().height() // 2)
        center_right = QPoint(self.current_rect.boundingRect().right(),
                              self.current_rect.boundingRect().top() + self.current_rect.boundingRect().height() // 2)
        center_top = QPoint(self.current_rect.boundingRect().left() + self.current_rect.boundingRect().width() // 2,
                            self.current_rect.boundingRect().top())
        center_bottom = QPoint(self.current_rect.boundingRect().left() + self.current_rect.boundingRect().width() // 2,
                               self.current_rect.boundingRect().bottom())

        # Calculate the positions and sizes for the start and end rectangles
        if direction == "E-W":
            start_rect_pos = QPoint(center_left.x(), center_left.y() - self.current_rect.boundingRect().height() // 2)
            end_rect_pos = QPoint(center_right.x() - (magnification_factor / 2),
                                  center_right.y() - self.current_rect.boundingRect().height() // 2)
            rect_size = QSize((magnification_factor / 2), self.current_rect.boundingRect().height())

            # post points
            start_x = min(x1, x2)
            end_x = max(x1, x2)
        else:
            start_rect_pos = QPoint(center_top.x() - self.current_rect.boundingRect().width() // 2, center_top.y())
            end_rect_pos = QPoint(center_bottom.x() - self.current_rect.boundingRect().width() // 2,
                                  center_bottom.y() - (magnification_factor / 2))
            rect_size = QSize(self.current_rect.boundingRect().width(), (magnification_factor / 2))

        # Create the start and end rectangles
        start_rect = QRect(start_rect_pos, rect_size)
        end_rect = QRect(end_rect_pos, rect_size)

        start_rect_item = QGraphicsRectItem(start_rect)
        end_rect_item = QGraphicsRectItem(end_rect)
        self.scene.addItem(start_rect_item)
        self.scene.addItem(end_rect_item)

        self.current_rect.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
        self.current_rect.setBrush(QBrush(QColor.fromRgb(255, 133, 81, 100), Qt.SolidPattern))
        ShearWallLabel((x1 + x2) / 2, (y1 + y2) / 2, self.scene, self.labels[i], direction)

    def studWallDraw(self, coordinate, i):
        start, end = coordinate
        x1, y1 = start
        x2, y2 = end

        # if snap to some point we don't need to check with snap line
        self.current_rect = Rectangle(x1,
                                      y1, None)
        self.scene.addItem(self.current_rect)
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        if abs(width) > abs(height):
            self.current_rect.setRect(min(x1, x2),
                                      y1 - self.studWall_width / 2, abs(width), self.studWall_width)
            direction = "E-W"
        else:
            self.current_rect.setRect(x1 - self.studWall_width / 2,
                                      min(y1, y2), self.studWall_width,
                                      abs(height))
            direction = "N-S"

        self.current_rect.setPen(QPen(QColor.fromRgb(152, 238, 204, 160), 2))
        self.current_rect.setBrush(QBrush(QColor.fromRgb(152, 238, 204, 150), Qt.SolidPattern))
        BeamLabel((x1 + x2) / 2, (y1 + y2) / 2, self.scene, self.labels[i], direction)


class BeamLabel:
    def __init__(self, x, y, scene, label, direction):
        # Create a QPainterPath object
        path = QPainterPath()
        path.moveTo(x, y)
        if direction == "E-W":
            path.lineTo(x + 30, y - 30)
            path.lineTo(x - 30, y - 30)
        else:
            path.lineTo(x + 30, y - 30)
            path.lineTo(x + 30, y + 30)
        path.closeSubpath()

        # Create a QGraphicsPathItem and set the path
        path_item = QGraphicsPathItem(path)
        path_item.setPen(QPen(Qt.black, 2))
        brush = QBrush(QColor(252, 248, 118, 180))
        path_item.setBrush(brush)  # Set the fill color
        scene.addItem(path_item)
        Label = QGraphicsProxyWidget()
        LabelText = QLabel(label)
        LabelText.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : black; }")
        Label.setWidget(LabelText)
        if direction == "N-S":
            Label.setPos(x + 30, y - 7)
            Label.setRotation(90)

        else:
            Label.setPos(x - 7, y - 30)

        scene.addItem(Label)


class ShearWallLabel:
    def __init__(self, x, y, scene, label, direction):
        # Create a QPainterPath object
        path = QPainterPath()
        path.moveTo(x, y)
        if direction == "E-W":
            path.lineTo(x + 35, y - 35)
            path.lineTo(x - 35, y - 35)
        else:
            path.lineTo(x + 35, y - 35)
            path.lineTo(x + 35, y + 35)
        path.closeSubpath()

        # Create a QGraphicsPathItem and set the path
        path_item = QGraphicsPathItem(path)
        path_item.setPen(QPen(Qt.black, 2))
        brush = QBrush(QColor(252, 248, 118, 180))
        path_item.setBrush(brush)  # Set the fill color
        scene.addItem(path_item)
        Label = QGraphicsProxyWidget()
        LabelText = QLabel(label)
        LabelText.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : black; }")
        Label.setWidget(LabelText)
        if direction == "N-S":
            Label.setPos(x + 35, y - 12)
            Label.setRotation(90)

        else:
            Label.setPos(x - 12, y - 35)

        scene.addItem(Label)
