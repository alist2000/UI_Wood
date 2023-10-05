from UI_Wood.stableVersion3.Beam import Rectangle
from UI_Wood.stableVersion3.mouse import SelectableLineItem
from UI_Wood.stableVersion3.joist_new import joistRectangle
from UI_Wood.stableVersion3.layout.LineDraw import BeamLabel
from UI_Wood.stableVersion3.image import image_control

from PySide6.QtGui import QPainter, QPixmap, QBrush, QPen, QColor
from PySide6.QtCore import QRectF, Qt, QPointF, QLineF, QPoint, QSize, QRect
from PySide6.QtWidgets import QWidget, QGraphicsLineItem, QGraphicsProxyWidget, QLabel, QGraphicsPathItem


class AreaDraw:
    def __init__(self, coordinates, labels, scene, story, orientations):
        self.story = story
        self.scene = scene
        self.labels = labels
        self.orientations = orientations

        for i, coordinate in enumerate(coordinates):
            self.joistDraw(coordinate, i)

        self.saveImage()

        for i, coordinate in enumerate(coordinates):
            self.joistDraw(coordinate, i, "not normal")

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
        pixmap.save(f"images/output/Joists_story{self.story + 1}.png")

    def saveImageElement(self, label):
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
        pixmap.save(f"images/output/Joists_label_{label}_story{self.story + 1}.png")

    def joistDraw(self, coordinate, i, color="normal"):
        x1, y1 = coordinate[0]
        x2, y2 = coordinate[1]
        rect_x, rect_y, rect_w, rect_h = min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)
        if self.orientations[i] == "N-S":
            path = "images/n_s.png"
        else:
            path = "images/e_w.png"
        self.rect_item = joistRectangle(rect_x, rect_y, rect_w, rect_h, None)
        image = image_control(rect_x, rect_y, rect_w, rect_h, self.rect_item, path)
        self.rect_item.image = image

        if color == "normal":
            self.rect_item.setBrush(QBrush(QColor.fromRgb(249, 155, 125, 100)))
            self.rect_item.setPen(QPen(Qt.black))
            self.scene.addItem(self.rect_item)
            BeamLabel((x1 + x2) / 2, (y1 + y2) / 2, self.scene, self.labels[i], self.orientations[i])
        else:
            self.rect_item.setBrush(QBrush(QColor.fromRgb(254, 0, 0, 100)))
            self.rect_item.setPen(QPen(Qt.black))
            self.scene.addItem(self.rect_item)
            self.saveImageElement(self.labels[i])
            self.scene.removeItem(self.rect_item)
