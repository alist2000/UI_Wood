from UI_Wood.stableVersion3.post_new import magnification_factor, CustomRectItem
from UI_Wood.stableVersion3.Beam import Rectangle
from UI_Wood.stableVersion3.mouse import SelectableLineItem

from PySide6.QtGui import QPainter, QPixmap, QFont
from PySide6.QtCore import QRectF, Qt, QPointF, QLineF, QPoint, QSize, QRect
from PySide6.QtWidgets import QWidget, QGraphicsLineItem, QGraphicsProxyWidget, QLabel, QGraphicsPathItem, \
    QGraphicsRectItem, QHBoxLayout
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath


class LineDraw:
    def __init__(self, properties, scene, story, lineType):
        self.story = story
        self.scene = scene
        self.labels = properties["label"]
        coordinates = properties["coordinate"]
        self.lineType = lineType.capitalize()
        # self.beam_width = magnification_factor / 2  # Set beam width
        self.beam_width = magnification_factor  # Set beam width
        self.shearWall_width = magnification_factor  # Set shearWall width, magnification = 1 ft or 1 m
        self.post_dimension = magnification_factor / 4  # Set post dimension
        self.studWall_width = 2 * magnification_factor / 3  # Set studWall width, magnification = 1 ft or 1 m

        for i, coordinate in enumerate(coordinates):
            if lineType == "beam":
                bending_dcr = properties["bending_dcr"][i]
                shear_dcr = properties["shear_dcr"][i]
                deflection_dcr = properties["deflection_dcr"][i]
                size = properties["size"][i]
                beamProp = [coordinate, size, bending_dcr, shear_dcr, deflection_dcr]
                # self.beamDraw(beamProp, i)
                beamDraw(self, beamProp, i)
            elif lineType == "shearWall":
                size = properties["size"][i]
                dcr_shear = properties["dcr_shear"][i]
                dcr_tension = properties["dcr_tension"][i]
                dcr_compression = properties["dcr_compression"][i]
                deflection_dcr = properties["deflection_dcr"][i]
                shearWallProp = [coordinate, size, dcr_shear, dcr_tension, dcr_compression, deflection_dcr]
                shearWallDraw(self, shearWallProp, i)
            else:  # studWall
                dcr_comp = properties["dcr_comp"][i]
                dcr_bend = properties["dcr_bend"][i]
                dcr_comb = properties["dcr_comb"][i]
                size = properties["size"][i]
                studProp = [coordinate, dcr_comp, dcr_bend, dcr_comb, size]
                # self.studWallDraw(coordinate, i)
                studWallDraw(self, studProp, i)

        self.saveImage()

        for i, coordinate in enumerate(coordinates):
            if lineType == "beam":
                bending_dcr = properties["bending_dcr"][i]
                shear_dcr = properties["shear_dcr"][i]
                deflection_dcr = properties["deflection_dcr"][i]
                size = properties["size"][i]
                beamProp = [coordinate, size, bending_dcr, shear_dcr, deflection_dcr]
                # self.beamDraw(beamProp, i, "not normal")
                beamDraw(self, beamProp, i, "not normal")
            elif lineType == "shearWall":
                size = properties["size"][i]
                dcr_shear = properties["dcr_shear"][i]
                dcr_tension = properties["dcr_tension"][i]
                dcr_compression = properties["dcr_compression"][i]
                deflection_dcr = properties["deflection_dcr"][i]
                shearWallProp = [coordinate, size, dcr_shear, dcr_tension, dcr_compression, deflection_dcr]
                shearWallDraw(self, shearWallProp, i, "not normal")

                # self.shearWallDraw(shearWallProp, i, "not normal")
            else:  # studWall
                dcr_comp = properties["dcr_comp"][i]
                dcr_bend = properties["dcr_bend"][i]
                dcr_comb = properties["dcr_comb"][i]
                size = properties["size"][i]
                studProp = [coordinate, dcr_comp, dcr_bend, dcr_comb, size]
                # self.studWallDraw(studProp, i, "not normal")
                studWallDraw(self, studProp, i, "not normal")

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
        pixmap.save(f"images/output/{self.lineType}s_label_{label}_story{self.story + 1}.png")


class BeamLabel:
    def __init__(self, x, y, scene, label, direction, halfLength=108, startDist1=27, startDist2=108):
        # Create a QPainterPath object
        path = QPainterPath()
        path.moveTo(x, y)
        if direction == "E-W":
            path.lineTo(x + halfLength, y - halfLength)
            path.lineTo(x - halfLength, y - halfLength)
        else:
            path.lineTo(x + halfLength, y - halfLength)
            path.lineTo(x + halfLength, y + halfLength)
        path.closeSubpath()

        # Create a QGraphicsPathItem and set the path
        path_item = QGraphicsPathItem(path)
        path_item.setPen(QPen(Qt.black, 2))
        brush = QBrush(QColor(252, 248, 118, 180))
        path_item.setBrush(brush)  # Set the fill color
        scene.addItem(path_item)
        Label = QGraphicsProxyWidget()
        LabelText = QLabel(label)
        font = QFont()
        font.setPointSize(35)
        LabelText.setFont(font)
        LabelText.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : black; }")
        Label.setWidget(LabelText)
        if direction == "N-S":
            Label.setPos(x + startDist2, y - startDist1)
            Label.setRotation(90)

        else:
            Label.setPos(x - startDist1, y - startDist2)

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


class shearWallDraw:
    def __init__(self, superClass, shearWallProp, i, color="normal"):
        self.superClass = superClass
        [coordinate, size, dcr_shear, dcr_tension, dcr_compression, dcr_deflection] = shearWallProp

        start, end = coordinate
        x1, y1 = start
        x2, y2 = end
        y1_main = min(y1, y2)
        x1_main = min(x1, x2)
        self.current_rect = Rectangle(x1,
                                      y1, None)
        superClass.scene.addItem(self.current_rect)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        if width > height:
            direction = "E-W"
        else:
            direction = "N-S"

        if direction == "E-W":
            self.current_rect.setRect(min(x1, x2),
                                      y1 - superClass.shearWall_width / 2, abs(width), superClass.shearWall_width)
        else:
            self.current_rect.setRect(x1 - superClass.shearWall_width / 2,
                                      min(y1, y2), superClass.shearWall_width,
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
        superClass.scene.addItem(start_rect_item)
        superClass.scene.addItem(end_rect_item)
        if color == "normal":
            dcr = [dcr_shear, dcr_tension, dcr_compression, dcr_deflection]
            color = "green"
            for value in dcr:
                if value > 1:
                    color = "red"
                    break
            if color == "red":
                self.current_rect.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
                self.current_rect.setBrush(QBrush(QColor.fromRgb(245, 80, 80, 100), Qt.SolidPattern))
                self.CheckValuesNew(dcr_shear, dcr_tension, dcr_compression, dcr_deflection, x1_main, y1_main,
                                    direction)

            else:
                self.current_rect.setPen(QPen(QColor.fromRgb(150, 194, 145, 100), 2))
                self.current_rect.setBrush(QBrush(QColor.fromRgb(150, 194, 145, 100), Qt.SolidPattern))
            self.TextValue(f"{size}", x1_main, y1_main, direction)
            BeamLabel((x1 + x2) / 2, (y1 + y2) / 2, superClass.scene, "SW" + superClass.labels[i], direction, startDist1=45)

            # ShearWallLabel((x1 + x2) / 2, (y1 + y2) / 2, superClass.scene, superClass.labels[i], direction)
        else:
            self.current_rect.setPen(QPen(QColor.fromRgb(254, 0, 0, 100), 2))
            self.current_rect.setBrush(QBrush(QColor.fromRgb(254, 0, 0, 100), Qt.SolidPattern))
            superClass.saveImageElement(superClass.labels[i])
            superClass.scene.removeItem(self.current_rect)

    def CheckValuesNew(self, dcr_shear, dcr_tension, dcr_compression, dcr_deflection, x, y, direction):
        mainText1 = QGraphicsProxyWidget()
        dcr1 = QLabel(f"DCR <sub>shear</sub>: {dcr_shear}, ")
        dcr2 = QLabel(f"DCR <sub>tension</sub>: {dcr_tension}, ")
        dcr3 = QLabel(f"DCR <sub>comp</sub>: {dcr_compression}")
        dcr4 = QLabel(f"DCR <sub>deflection</sub>: {dcr_deflection}")
        font = QFont()
        font.setPointSize(7)
        dcr1.setFont(font)
        dcr2.setFont(font)
        dcr3.setFont(font)
        dcr4.setFont(font)
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

        self.setColor(dcr_shear, dcr1)
        self.setColor(dcr_tension, dcr2)
        self.setColor(dcr_compression, dcr3)
        self.setColor(dcr_deflection, dcr4)
        if direction == "N-S":
            mainText1.setRotation(90)
            mainText1.setPos(x - 0.4 * self.superClass.shearWall_width, y)
        else:
            mainText1.setPos(x, y + 0.4 * self.superClass.shearWall_width)

        # LabelText = QLabel(label)
        self.superClass.scene.addItem(mainText1)

    @staticmethod
    def setColor(item, label):
        if item > 1:
            label.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : red; }")

        else:
            label.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : green; }")

    def TextValue(self, text, x, y, direction, color="black", size=30):
        mainText1 = QGraphicsProxyWidget()
        label = QLabel(text)
        font = QFont()
        font.setPointSize(size)
        label.setFont(font)
        mainText1.setWidget(label)
        # text = QGraphicsTextItem("Hello, PySide6!")

        label.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color :" + f"{color}" + " ;}")
        if direction == "N-S":
            mainText1.setRotation(90)
            mainText1.setPos(x + 2 * self.superClass.shearWall_width, y)
        else:
            mainText1.setPos(x, y - 2 * self.superClass.shearWall_width)

        # LabelText = QLabel(label)
        self.superClass.scene.addItem(mainText1)


class beamDraw:
    def __init__(self, superClass, beamProp, i, color="normal"):
        self.superClass = superClass
        [coordinate, size, bending_dcr, shear_dcr, deflection_dcr] = beamProp

        point1, point2 = coordinate
        x1, y1 = point1
        x2, y2 = point2
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        # x, y = (x1 + x2) / 2, (y1 + y2) / 2
        y1_main = min(y1, y2)
        x1_main = min(x1, x2)
        y2_main = max(y1, y2)
        x2_main = max(x1, x2)
        self.current_rect = Rectangle(x1 - superClass.beam_width / 2,
                                      y1 - superClass.beam_width / 2, None)
        superClass.scene.addItem(self.current_rect)

        width = abs(x2 - x1)
        height = abs(y2 - y1)

        if abs(width) > abs(height):
            self.current_rect.setRect(min(x1, x2),
                                      y1 - superClass.beam_width / 2, abs(width), superClass.beam_width)
            direction = "E-W"

        else:
            self.current_rect.setRect(x1 - superClass.beam_width / 2,
                                      min(y1, y2), superClass.beam_width,
                                      abs(height))
            direction = "N-S"

        if color == "normal":
            self.current_rect.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
            self.current_rect.setBrush(QBrush(QColor.fromRgb(245, 80, 80, 100), Qt.SolidPattern))
            BeamLabel((x1 + x2) / 2, (y1 + y2) / 2, superClass.scene, superClass.labels[i], direction)
            dcr = [bending_dcr, shear_dcr, deflection_dcr]
            color = "green"
            for value in dcr:
                if value > 1:
                    color = "red"
                    break
            if color == "red":
                self.current_rect.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
                self.current_rect.setBrush(QBrush(QColor.fromRgb(245, 80, 80, 100), Qt.SolidPattern))
                self.CheckValuesNew(bending_dcr, shear_dcr, deflection_dcr, x1_main, y1_main, direction)

            else:
                self.current_rect.setPen(QPen(QColor.fromRgb(150, 194, 145, 100), 2))
                self.current_rect.setBrush(QBrush(QColor.fromRgb(150, 194, 145, 100), Qt.SolidPattern))
                # self.CheckValuesNew(bending_dcr, shear_dcr, deflection_dcr, x_dcr1, y_dcr1, direction)

            self.current_rect = None
            self.start_pos = None
            # self.CheckValues("DCR<sub>m</sub>", bending_dcr, x_dcr1, y_dcr1, direction)
            # self.CheckValues("DCR<sub>v</sub>", shear_dcr, x_dcr2, y_dcr2, direction)
            # self.CheckValues("DCR<sub>def</sub>", deflection_dcr, x_dcr3, y_dcr3, direction)
            self.TextValue(f"{size}", x1_main, y1_main, direction)
        else:
            self.current_rect.setPen(QPen(QColor.fromRgb(254, 0, 0, 100), 2))
            self.current_rect.setBrush(QBrush(QColor.fromRgb(254, 0, 0, 100), Qt.SolidPattern))
            superClass.saveImageElement(superClass.labels[i])
            superClass.scene.removeItem(self.current_rect)

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
            mainText1.setPos(x - 0.4 * self.superClass.beam_width, y)
        else:
            mainText1.setPos(x, y + 0.4 * self.superClass.beam_width)

        # LabelText = QLabel(label)
        self.superClass.scene.addItem(mainText1)

    @staticmethod
    def setColor(item, label):
        if item > 1:
            label.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : red; }")

        else:
            label.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : green; }")

    def TextValue(self, text, x, y, direction, color="black", size=30):
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
            mainText1.setPos(x + 2 * self.superClass.beam_width, y)
        else:
            mainText1.setPos(x, y - 2 * self.superClass.beam_width)

        # LabelText = QLabel(label)
        self.superClass.scene.addItem(mainText1)


class studWallDraw:
    def __init__(self, superClass, studProp, i, color="normal"):
        self.superClass = superClass
        [coordinate, dcr_comp, dcr_bend, dcr_comb, size] = studProp

        start, end = coordinate
        x1, y1 = start
        x2, y2 = end
        y1_main = min(y1, y2)
        x1_main = min(x1, x2)
        # if snap to some point we don't need to check with snap line
        self.current_rect = Rectangle(x1,
                                      y1, None)
        superClass.scene.addItem(self.current_rect)
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        if abs(width) > abs(height):
            self.current_rect.setRect(min(x1, x2),
                                      y1 - superClass.studWall_width / 2, abs(width), superClass.studWall_width)
            direction = "E-W"
        else:
            self.current_rect.setRect(x1 - superClass.studWall_width / 2,
                                      min(y1, y2), superClass.studWall_width,
                                      abs(height))
            direction = "N-S"

        if color == "normal":
            dcr = [dcr_comp, dcr_bend, dcr_comb]
            color = "green"
            for value in dcr:
                if value > 1:
                    color = "red"
                    break
            if color == "red":
                self.current_rect.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
                self.current_rect.setBrush(QBrush(QColor.fromRgb(245, 80, 80, 100), Qt.SolidPattern))
                self.CheckValuesNew(dcr_comp, dcr_bend, dcr_comb, x1_main, y1_main, direction)

            else:
                self.current_rect.setPen(QPen(QColor.fromRgb(150, 194, 145, 100), 2))
                self.current_rect.setBrush(QBrush(QColor.fromRgb(150, 194, 145, 100), Qt.SolidPattern))
            self.TextValue(f"{size}", x1_main, y1_main, direction)
            BeamLabel((x1 + x2) / 2, (y1 + y2) / 2, superClass.scene, "ST" + superClass.labels[i], direction, startDist1=50)
        else:
            self.current_rect.setPen(QPen(QColor.fromRgb(254, 0, 0, 160), 2))
            self.current_rect.setBrush(QBrush(QColor.fromRgb(254, 0, 0, 150), Qt.SolidPattern))
            superClass.saveImageElement(superClass.labels[i])
            superClass.scene.removeItem(self.current_rect)

    def CheckValuesNew(self, dcr_stud, dcr_tension, dcr_compression, x, y, direction):
        mainText1 = QGraphicsProxyWidget()
        dcr1 = QLabel(f"DCR <sub>stud</sub>: {dcr_stud}, ")
        dcr2 = QLabel(f"DCR <sub>tension</sub>: {dcr_tension}, ")
        dcr3 = QLabel(f"DCR <sub>comp</sub>: {dcr_compression}")
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

        self.setColor(dcr_stud, dcr1)
        self.setColor(dcr_tension, dcr2)
        self.setColor(dcr_compression, dcr3)
        if direction == "N-S":
            mainText1.setRotation(90)
            mainText1.setPos(x - 0.4 * self.superClass.studWall_width, y)
        else:
            mainText1.setPos(x, y + 0.4 * self.superClass.studWall_width)

        # LabelText = QLabel(label)
        self.superClass.scene.addItem(mainText1)

    @staticmethod
    def setColor(item, label):
        if item > 1:
            label.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : red; }")

        else:
            label.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : green; }")

    def TextValue(self, text, x, y, direction, color="black", size=30):
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
            mainText1.setPos(x + 2 * self.superClass.studWall_width, y)
        else:
            mainText1.setPos(x, y - 2 * self.superClass.studWall_width)

        # LabelText = QLabel(label)
        self.superClass.scene.addItem(mainText1)
