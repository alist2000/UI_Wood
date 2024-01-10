from UI_Wood.stableVersion5.layout.LineDraw import BeamLabel
from UI_Wood.stableVersion5.post_new import magnification_factor, CustomRectItem
from UI_Wood.stableVersion5.mouse import SelectableLineItem

from PySide6.QtGui import QPainter, QPixmap, QFont, QPen, QBrush, QColor
from PySide6.QtCore import QRectF, Qt, QPointF, QLineF
from PySide6.QtWidgets import QWidget, QGraphicsLineItem, QGraphicsProxyWidget, QLabel


class PointDraw:
    def __init__(self, properties, scene, story):
        self.story = story
        self.scene = scene
        coordinates = properties["coordinate"]
        labels = properties["label"]
        self.post_dimension = 3 * magnification_factor  # Set post dimension
        for i, coordinate in enumerate(coordinates):
            size = properties["size"][i]
            axial_dcr = properties["axial_dcr"][i]
            x, y = coordinate
            rect_width = rect_height = self.post_dimension
            rect_item = CustomRectItem(None)
            rect_item.setRect(x - rect_width / 2, y - rect_height / 2, rect_width, rect_height)
            scene.addItem(rect_item)
            mainText = QGraphicsProxyWidget()
            sizeMain = QGraphicsProxyWidget()
            dcr = QLabel(f"Axial DCR: {axial_dcr}")
            sizeLabel = QLabel(f"{size}")
            font = QFont()
            font.setPointSize(20)
            dcr.setFont(font)
            font2 = QFont()
            font2.setPointSize(30)
            sizeLabel.setFont(font2)
            mainText.setWidget(dcr)
            sizeMain.setWidget(sizeLabel)
            # text = QGraphicsTextItem("Hello, PySide6!")

            # Set the color of the text to red
            mainText.setPos(x - rect_width, y + 0.6 * rect_width)
            sizeMain.setPos(x - 1 * magnification_factor, y - 0.5 * magnification_factor)
            sizeLabel.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : black; }")

            self.scene.addItem(sizeMain)

            if axial_dcr > 1:
                rect_item.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
                rect_item.setBrush(QBrush(QColor.fromRgb(245, 80, 80, 100), Qt.SolidPattern))
                dcr.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : red; }")
                self.scene.addItem(mainText)
            else:
                rect_item.setPen(QPen(QColor.fromRgb(150, 194, 145, 100), 2))
                rect_item.setBrush(QBrush(QColor.fromRgb(150, 194, 145, 100), Qt.SolidPattern))
                dcr.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : green; }")

            # LabelText = QLabel(label)
            # Label = QGraphicsProxyWidget()
            # LabelText = QLabel(labels[i])
            # font = QFont()
            # font.setPointSize(30)
            # LabelText.setFont(font)
            # # sizeMain.setFont(font)
            # LabelText.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : black; }")
            # Label.setWidget(LabelText)
            PostLabel(x, y, scene, labels[i])
            # return rect_item
        self.saveImage()

        for i, coordinate in enumerate(coordinates):
            size = properties["size"][i]
            axial_dcr = properties["axial_dcr"][i]
            x, y = coordinate
            rect_width = rect_height = self.post_dimension
            rect_item = CustomRectItem(None, "not normal")
            rect_item.setRect(x - rect_width / 2, y - rect_height / 2, rect_width, rect_height)
            mainText = QGraphicsProxyWidget()
            dcr = QLabel(f"Axial DCR: {axial_dcr}")
            font = QFont()
            font.setPointSize(20)
            dcr.setFont(font)
            mainText.setWidget(dcr)
            # text = QGraphicsTextItem("Hello, PySide6!")

            # Set the color of the text to red
            mainText.setPos(x - rect_width, y + 0.6 * rect_width)
            if axial_dcr > 1:
                dcr.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : red; }")
                self.scene.addItem(mainText)
            else:
                dcr.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : green; }")

            # LabelText = QLabel(label)
            self.scene.addItem(rect_item)

            # Label = QGraphicsProxyWidget()
            # LabelText = QLabel(labels[i])
            # font = QFont()
            # font.setPointSize(25)
            # LabelText.setFont(font)
            # LabelText.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : black; }")
            # Label.setWidget(LabelText)
            #
            # # BeamLabel((x1 + x2) / 2, (y1 + y2) / 2, self.scene, properties["label"], direction)
            # Label.setPos(x - 1.1 * rect_width, y - 1.1 * rect_width)
            #
            # self.scene.addItem(Label)
            scene.addItem(rect_item)
            self.saveImageElement(labels[i])
            self.scene.removeItem(rect_item)

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
        pixmap.save(f"images/output/Posts_label_{label}_story{self.story + 1}.png")


class PostLabel:
    def __init__(self, x, y, scene, label):
        # Create a line shape
        # line = QGraphicsLineItem()
        # line1 = QGraphicsLineItem()
        # line.setLine(QLineF(QPointF(x, y), QPointF(x + 10, y - 50)))
        # line1.setLine(QLineF(QPointF(x + 10, y - 50), QPointF(x + 30, y - 50)))
        # scene.addItem(line)
        # scene.addItem(line1)
        Label = QGraphicsProxyWidget()
        LabelText = QLabel(label)
        font = QFont()
        font.setPointSize(30)
        LabelText.setFont(font)
        LabelText.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : black; }")
        Label.setWidget(LabelText)

        # BeamLabel((x1 + x2) / 2, (y1 + y2) / 2, self.scene, properties["label"], direction)
        Label.setPos(x - 2 * magnification_factor, y - 3.5 * magnification_factor)

        scene.addItem(Label)
        # BeamLabel(x + 30, y - 50, scene, label, "E-W", 12, 6, 30)


class postDraw:
    def __init__(self):
        pass
