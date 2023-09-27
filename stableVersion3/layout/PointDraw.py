from UI_Wood.stableVersion3.layout.LineDraw import BeamLabel
from UI_Wood.stableVersion3.post_new import magnification_factor, CustomRectItem
from UI_Wood.stableVersion3.mouse import SelectableLineItem

from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import QRectF, Qt, QPointF, QLineF
from PySide6.QtWidgets import QWidget, QGraphicsLineItem, QGraphicsProxyWidget, QLabel


class PointDraw:
    def __init__(self, coordinates, labels, scene, story):
        self.story = story
        self.scene = scene
        self.post_dimension = magnification_factor  # Set post dimension
        for i, coordinate in enumerate(coordinates):
            x, y = coordinate
            rect_width = rect_height = self.post_dimension
            rect_item = CustomRectItem(None)
            rect_item.setRect(x - rect_width / 2, y - rect_height / 2, rect_width, rect_height)
            scene.addItem(rect_item)
            PostLabel(x, y, scene, labels[i])
            # return rect_item
        self.saveImage()
        for item in scene.items():
            if item and (
                    isinstance(item, CustomRectItem) or isinstance(item, QGraphicsProxyWidget) or not isinstance(item,
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
        pixmap.save(f"images/output/Posts_story{self.story + 1}.png")


class PostLabel:
    def __init__(self, x, y, scene, label):
        # Create a line shape
        line = QGraphicsLineItem()
        line1 = QGraphicsLineItem()
        line.setLine(QLineF(QPointF(x, y), QPointF(x + 10, y - 50)))
        line1.setLine(QLineF(QPointF(x + 10, y - 50), QPointF(x + 30, y - 50)))
        scene.addItem(line)
        scene.addItem(line1)
        BeamLabel(x + 30, y - 50, scene, label, "E-W", 12, 6, 30)
