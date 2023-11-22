from UI_Wood.stableVersion3.Beam import Rectangle
from UI_Wood.stableVersion3.mouse import SelectableLineItem
from UI_Wood.stableVersion3.joist_new import joistRectangle
from UI_Wood.stableVersion3.layout.LineDraw import BeamLabel
from UI_Wood.stableVersion3.image import image_control
from UI_Wood.stableVersion3.post_new import magnification_factor
from PySide6.QtGui import QPainter, QPixmap, QBrush, QPen, QColor, QFont
from PySide6.QtCore import QRectF, Qt, QPointF, QLineF, QPoint, QSize, QRect
from PySide6.QtWidgets import QWidget, QGraphicsLineItem, QGraphicsProxyWidget, QLabel, QGraphicsPathItem, QHBoxLayout


class AreaDraw:
    def __init__(self, properties, scene, story):
        self.story = story
        self.scene = scene
        self.labels = properties["label"]
        self.orientations = properties["direction"]
        coordinates = properties["coordinate"]
        self.joist_width = magnification_factor / 2  # Set joist width

        for i, coordinate in enumerate(coordinates):
            bending_dcr = properties["bending_dcr"][i]
            shear_dcr = properties["shear_dcr"][i]
            deflection_dcr = properties["deflection_dcr"][i]
            size = properties["size"][i]
            joistProp = [coordinate, size, bending_dcr, shear_dcr, deflection_dcr]
            joistDraw(self, joistProp, i)

        self.saveImage()

        for i, coordinate in enumerate(coordinates):
            bending_dcr = properties["bending_dcr"][i]
            shear_dcr = properties["shear_dcr"][i]
            deflection_dcr = properties["deflection_dcr"][i]
            size = properties["size"][i]
            joistProp = [coordinate, size, bending_dcr, shear_dcr, deflection_dcr]
            joistDraw(self, joistProp, i, "not normal")

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


class joistDraw:
    def __init__(self, superClass, joistProp, i, color="normal"):
        [coordinate, size, bending_dcr, shear_dcr, deflection_dcr] = joistProp

        self.superClass = superClass
        x1, y1 = coordinate[0]
        x2, y2 = coordinate[1]
        rect_x, rect_y, rect_w, rect_h = min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)

        if superClass.orientations[i] == "N-S":
            path = "images/n_s.png"
            x_size = x2
            y_size = y1
        else:
            path = "images/e_w.png"
            x_size = x1
            y_size = y2
        self.rect_item = joistRectangle(rect_x, rect_y, rect_w, rect_h, None)
        image = image_control(rect_x, rect_y, rect_w, rect_h, self.rect_item, path)
        self.rect_item.image = image

        if color == "normal":
            self.rect_item.setBrush(QBrush(QColor.fromRgb(249, 155, 125, 100)))
            self.rect_item.setPen(QPen(Qt.black))
            superClass.scene.addItem(self.rect_item)
            dcr = [bending_dcr, shear_dcr, deflection_dcr]
            color = "green"
            for value in dcr:
                if value > 1:
                    color = "red"
                    break
            if color == "red":
                self.rect_item.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
                self.rect_item.setBrush(QBrush(QColor.fromRgb(245, 80, 80, 100), Qt.SolidPattern))
                self.CheckValuesNew(bending_dcr, shear_dcr, deflection_dcr, x1, y1, superClass.orientations[i])

            else:
                self.rect_item.setPen(QPen(QColor.fromRgb(150, 194, 145, 100), 2))
                self.rect_item.setBrush(QBrush(QColor.fromRgb(150, 194, 145, 100), Qt.SolidPattern))

            self.TextValue(f"{size}", x_size, y_size, superClass.orientations[i])
            BeamLabel((x1 + x2) / 2, (y1 + y2) / 2, superClass.scene, superClass.labels[i], superClass.orientations[i])
        else:
            self.rect_item.setBrush(QBrush(QColor.fromRgb(254, 0, 0, 100)))
            self.rect_item.setPen(QPen(Qt.black))
            superClass.scene.addItem(self.rect_item)
            superClass.saveImageElement(superClass.labels[i])
            superClass.scene.removeItem(self.rect_item)

    def CheckValuesNew(self, bending_dcr, shear_dcr, deflection_dcr, x, y, direction):
        mainText1 = QGraphicsProxyWidget()
        dcr1 = QLabel(f"DCR <sub>m</sub>: {bending_dcr}, ")
        dcr2 = QLabel(f"DCR <sub>v</sub>: {shear_dcr}, ")
        dcr3 = QLabel(f"DCR <sub>def</sub>: {deflection_dcr}")
        font = QFont()
        font.setPointSize(7)
        dcr1.setFont(font)
        dcr2.setFont(font)
        dcr3.setFont(font)
        layout = QHBoxLayout()
        layout.setSpacing(7)  # Set the space between widgets to 20 pixels
        layout.addWidget(dcr1)
        layout.addWidget(dcr2)
        layout.addWidget(dcr3)
        widget = QWidget()
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: transparent;")
        mainText1.setWidget(widget)
        # text = QGraphicsTextItem("Hello, PySide6!")

        self.setColor(bending_dcr, dcr1)
        self.setColor(shear_dcr, dcr2)
        self.setColor(deflection_dcr, dcr3)
        if direction == "N-S":
            mainText1.setRotation(90)
            mainText1.setPos(x + 2 * self.superClass.joist_width, y)
        else:
            mainText1.setPos(x, y + 0.3 * self.superClass.joist_width)

        # LabelText = QLabel(label)
        self.superClass.scene.addItem(mainText1)

    @staticmethod
    def setColor(item, label):
        if item > 1:
            label.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : red; }")

        else:
            label.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : green; }")

    def TextValue(self, text, x, y, direction, color="black", size=20):
        mainText1 = QGraphicsProxyWidget()
        dcr1 = QLabel(text)
        font = QFont()
        font.setPointSize(size)
        dcr1.setFont(font)
        mainText1.setWidget(dcr1)
        # text = QGraphicsTextItem("Hello, PySide6!")

        dcr1.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color :" + f"{color}" + " ;}")
        if direction == "N-S":
            mainText1.setRotation(90)
            mainText1.setPos(x - 0.4 * self.superClass.joist_width, y + 0.3 * self.superClass.joist_width)
        else:
            mainText1.setPos(x + 0.3 * self.superClass.joist_width, y - 1.5 * self.superClass.joist_width)

        # LabelText = QLabel(label)
        self.superClass.scene.addItem(mainText1)
