from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QUndoStack
from PySide6.QtGui import QPen, QBrush
from PySide6.QtWidgets import QDialog, QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PySide6.QtWidgets import QGraphicsProxyWidget, QGraphicsRectItem
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene

from UI_Wood.stableVersion5.image import image_control
from UI_Wood.stableVersion5.layout.LineDraw import BeamLabel
from UI_Wood.stableVersion5.post_new import magnification_factor
from UI_Wood.stableVersion5.path import PathHandler
from UI_Wood.stableVersion5.navigation_graphics_view import NavigationGraphicsView


class DrawJoist(QDialog):
    def __init__(self, GridClass, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)

        self.setWindowTitle("Continue or Break?")

        self.mainLayout = QVBoxLayout()
        self.view = NavigationGraphicsView()
        self.undoStack = QUndoStack()
        self.scene = QGraphicsScene()
        self.view.scene = self.scene
        self.view.setScene(self.scene)
        GridClass.Draw(self.scene)
        self.joist_width = magnification_factor / 2  # Set joist width
        self.dimension = None

    def story(self, story):
        mainText = QGraphicsProxyWidget()
        dcr = QLabel(f"Story {story}")
        font = QFont()
        font.setPointSize(30)
        dcr.setFont(font)
        dcr.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : black; }")
        mainText.setWidget(dcr)
        mainText.setPos(-150, -150)
        self.scene.addItem(mainText)

    def draw(self, properties):
        coordinate = properties["coordinate"]
        x1, y1 = coordinate[0]
        x2, y2 = coordinate[2]
        length = (((x2 - x1) ** 2) + (
                (y2 - y1) ** 2)) ** 0.5
        rect_x, rect_y, rect_w, rect_h = min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)

        rect_item = joistRectangle(rect_x, rect_y, rect_w, rect_h, properties)
        if properties["direction"] == "E-W":
            imagePath = PathHandler("images/e_w.png")
            x_size = x1
            y_size = y2
        else:
            imagePath = PathHandler("images/n_s.png")
            x_size = x2
            y_size = y1

        image = image_control(rect_x, rect_y, rect_w, rect_h, rect_item, imagePath)
        rect_item.image = image

        rect_item.setBrush(QBrush(QColor.fromRgb(249, 155, 125, 100)))
        rect_item.setPen(QPen(Qt.black))
        self.scene.addItem(rect_item)

        bending_dcr = properties["bending_dcr"]
        shear_dcr = properties["shear_dcr"]
        deflection_dcr = properties["deflection_dcr"]
        dcr = [bending_dcr, shear_dcr, deflection_dcr]
        color = "green"
        for i in dcr:
            if i > 1:
                color = "red"
                break
        if color == "red":
            rect_item.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
            rect_item.setBrush(QBrush(QColor.fromRgb(245, 80, 80, 100), Qt.SolidPattern))
            self.CheckValuesNew(bending_dcr, shear_dcr, deflection_dcr, x1, y1, properties["direction"])

        else:
            rect_item.setPen(QPen(QColor.fromRgb(150, 194, 145, 100), 2))
            rect_item.setBrush(QBrush(QColor.fromRgb(150, 194, 145, 100), Qt.SolidPattern))

        self.TextValue(f"{properties['size']}", x_size, y_size, properties["direction"])
        BeamLabel(x1 + length / 2, y1, self.scene, properties["label"], properties["direction"], (x1, y1))

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
            mainText1.setPos(x + 2 * self.joist_width, y)
        else:
            mainText1.setPos(x, y + 0.3 * self.joist_width)

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
            mainText1.setPos(x - 0.4 * self.joist_width, y + 0.3 * self.joist_width)
        else:
            mainText1.setPos(x + 0.3 * self.joist_width, y - 1.5 * self.joist_width)

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


class joistRectangle(QGraphicsRectItem):
    def __init__(self, rect_x, rect_y, rect_w, rect_h, rect_prop):
        super().__init__(rect_x, rect_y, rect_w, rect_h)
        self.image = None
        self.joist_properties_page = None
        self.rect_prop = rect_prop

    # CONTROL ON JOIST
    def mousePressEvent(self, event):
        center = self.boundingRect().center().toTuple()
        # properties page open
        if event.button() == Qt.RightButton:  # Joist Properties page
            print(self.rect_prop["label"])


class JoistStoryBy:
    def __init__(self, joists, GridClass, story):
        print(joists)
        self.view = None
        self.dialog = DrawJoist(GridClass)
        self.dialog.story(story)

        self.view = self.dialog.view
        for joist in joists:
            self.dialog.draw(joist)
        self.dialog.Show()
        # self.dialog.show()
        self.result = self.dialog.exec()
