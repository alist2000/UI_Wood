from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsTextItem
from PySide6.QtGui import QPainterPath
from PySide6.QtCore import Qt
from PySide6.QtCore import Qt, QRect, QPoint, QSize
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QTabWidget, QGraphicsRectItem, QWidget, QPushButton, QDialog, QDialogButtonBox, \
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QGraphicsItem, QGraphicsProxyWidget
from PySide6.QtWidgets import QWidget, QGraphicsLineItem, QGraphicsProxyWidget, QLabel, QGraphicsPathItem, \
    QGraphicsRectItem
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QGraphicsTextItem

from PySide6.QtWidgets import QTabWidget, QDialog, QDialogButtonBox, \
    QLabel, QWidget, QVBoxLayout, QPushButton, QComboBox, QDoubleSpinBox, QHBoxLayout, \
    QTableWidget, QAbstractItemView
from UI_Wood.stableVersion4.post_new import magnification_factor
from UI_Wood.stableVersion4.layout.LineDraw import BeamLabel


class DrawStudWall(QDialog):
    def __init__(self, GridClass, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Continue or Break?")

        self.mainLayout = QVBoxLayout()
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        GridClass.Draw(self.scene)
        self.current_rect = None
        self.studWall_width = magnification_factor / 3  # Set studWall width, magnification = 1 ft or 1 m

    def story(self, story):
        mainText = QGraphicsProxyWidget()
        if story == "999999":
            story = "Roof"

        dcr = QLabel(f"Story {story}")
        font = QFont()
        font.setPointSize(30)
        dcr.setFont(font)
        dcr.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : black; }")
        mainText.setWidget(dcr)
        mainText.setPos(-150, -150)
        self.scene.addItem(mainText)

    # coordinate = properties["coordinate"]
    # x1, y1 = coordinate[0]
    # x2, y2 = coordinate[1]
    # self.finalize_rectangle_copy((x1, y1), (x2, y2), properties)

    def finalize_rectangle_copy(self, start, end, prop):
        x1, y1 = start
        x2, y2 = end
        y1_main = min(y1, y2)
        x1_main = min(x1, x2)
        # if snap to some point we don't need to check with snap line
        self.current_rect = Rectangle(x1,
                                      y1, prop)
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

        dcr_comp = prop["dcr_comp"]
        dcr_bend = prop["dcr_bend"]
        dcr_comb = prop["dcr_comb"]
        dcr = [dcr_comp, dcr_bend, dcr_comb]
        color = "green"
        for i in dcr:
            if i > 1:
                color = "red"
                break
        if color == "red":
            self.current_rect.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
            self.current_rect.setBrush(QBrush(QColor.fromRgb(245, 80, 80, 100), Qt.SolidPattern))
            self.CheckValuesNew(dcr_comp, dcr_bend, dcr_comb, x1_main, y1_main, direction)

        else:
            self.current_rect.setPen(QPen(QColor.fromRgb(150, 194, 145, 100), 2))
            self.current_rect.setBrush(QBrush(QColor.fromRgb(150, 194, 145, 100), Qt.SolidPattern))
        self.TextValue(f"{prop['size']}", x1_main, y1_main, direction)

        # self.current_rect.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
        # self.current_rect.setBrush(QBrush(QColor.fromRgb(255, 133, 81, 100), Qt.SolidPattern))

        BeamLabel((x1 + x2) / 2, (y1 + y2) / 2, self.scene, "ST" + prop["label"], direction)

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
            mainText1.setPos(x - 0.4 * self.studWall_width, y)
        else:
            mainText1.setPos(x, y + 0.4 * self.studWall_width)

        # LabelText = QLabel(label)
        self.scene.addItem(mainText1)

    @staticmethod
    def setColor(item, label):
        if item > 1:
            label.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : red; }")

        else:
            label.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : green; }")

    def TextValue(self, text, x, y, direction, color="black", size=10):
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
            mainText1.setPos(x + 1.1 * self.studWall_width, y)
        else:
            mainText1.setPos(x, y - 1.1 * self.studWall_width)

        # LabelText = QLabel(label)
        self.scene.addItem(mainText1)

    def Show(self):
        # Add the view to the layout
        yes_button = QPushButton("Continue")

        no_button = QPushButton("Break")
        yes_button.clicked.connect(self.accept)  # Connect "Yes" button to accept()

        no_button.clicked.connect(self.reject)  # Connect "No" button to reject()
        hLayout = QHBoxLayout()
        hLayout.addWidget(no_button)
        hLayout.addWidget(yes_button)
        self.view.setScene(self.scene)
        self.mainLayout.addWidget(self.view)
        self.mainLayout.addLayout(hLayout)
        self.setLayout(self.mainLayout)
        # self.show()

        # self.setScene(self.scene)
        # self.show()

    def wheelEvent(self, event):
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        # Save the scene pos
        oldPos = self.view.mapToScene(event.position().toPoint())

        # Zoom
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.view.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.view.mapToScene(event.position().toPoint())

        # Move scene to old position
        delta = newPos - oldPos
        self.view.translate(delta.x(), delta.y())


class Rectangle(QGraphicsRectItem):
    def __init__(self, x, y, rect_prop):
        super().__init__(x, y, 0, 0)
        self.setPen(QPen(Qt.blue, 2))  # Set the border color to blue
        self.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))  # Set the fill color to transparent

        self.rect_prop = rect_prop

    # CONTROL ON BEAM
    def mousePressEvent(self, event):
        center = self.boundingRect().center().toTuple()
        # properties page open
        if event.button() == Qt.RightButton:  # beam Properties page
            height = self.boundingRect().height() - 1  # ATTENTION: I don't know why but this method return height + 1
            width = self.boundingRect().width() - 1  # ATTENTION: I don't know why but this method return width + 1
            print(f"Stud wall {self.rect_prop['label']} CLICKED")


class StudWallStoryBy:
    def __init__(self, studWalls, GridClass, story):
        print(studWalls)
        # coordinate = [i["coordinate_main"] for i in studWalls]
        # label = [i["label"] for i in studWalls]
        # bending_dcr = [i["bending_dcr"] for i in studWalls]
        # stud_dcr = [i["stud_dcr"] for i in studWalls]
        # deflection_dcr = [i["deflection_dcr"] for i in studWalls]
        self.view = None
        # instance = DrawStudWall()
        self.dialog = DrawStudWall(GridClass)
        self.dialog.story(story)

        self.view = self.dialog.view
        for studWall in studWalls:
            start = [float(i.strip()) * magnification_factor for i in studWall["coordinate"][0][1:-1].split(",")]
            end = [float(i.strip()) * magnification_factor for i in studWall["coordinate"][1][1:-1].split(",")]
            self.dialog.finalize_rectangle_copy(start, end, studWall)
        self.dialog.Show()
        # self.dialog.show()
        self.result = self.dialog.exec()
