from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsTextItem
from PySide6.QtGui import QPainterPath
from PySide6.QtCore import Qt
from PySide6.QtCore import Qt, Signal, QObject, QEvent
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QTabWidget, QGraphicsRectItem, QWidget, QPushButton, QDialog, QDialogButtonBox, \
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QGraphicsItem, QGraphicsProxyWidget
from PySide6.QtWidgets import QWidget, QGraphicsLineItem, QGraphicsProxyWidget, QLabel, QGraphicsPathItem, \
    QGraphicsRectItem
from PySide6.QtGui import QFont, QColor, QUndoStack
from PySide6.QtWidgets import QGraphicsTextItem

from PySide6.QtWidgets import QTabWidget, QDialog, QDialogButtonBox, \
    QLabel, QWidget, QVBoxLayout, QPushButton, QComboBox, QDoubleSpinBox, QHBoxLayout, \
    QTableWidget, QAbstractItemView
from UI_Wood.stableVersion5.post_new import magnification_factor
from UI_Wood.stableVersion5.pointer_control import control_post_range, range_post, beam_end_point, \
    selectable_beam_range, \
    control_selectable_beam_range
from UI_Wood.stableVersion5.navigation_graphics_view import NavigationGraphicsView


class DrawPost(QDialog):
    def __init__(self, GridClass, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Continue or Break?")

        self.mainLayout = QVBoxLayout()
        self.view = NavigationGraphicsView()
        self.undoStack = QUndoStack()
        self.scene = QGraphicsScene()
        self.view.scene = self.scene
        self.view.setScene(self.scene)
        GridClass.Draw(self.scene)
        self.current_rect = None
        self.start_pos = None
        self.beam_select_status = 0  # 0: neutral, 1: select Post, 2: delete Post
        self.other_button = None
        # self.beam_width = min(min(x), min(y)) / 25  # Set Post width
        self.beam_width = magnification_factor / 2  # Set Post width
        # self.post_dimension = min(min(x), min(y)) / 8  # Set post dimension
        self.post_dimension = magnification_factor  # Set post dimension
        self.dimension = None

        # coordinate = properties["coordinate"]
        # x1, y1 = coordinate[0]
        # x2, y2 = coordinate[1]
        # self.finalize_rectangle_copy((x1, y1), (x2, y2), properties)

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

    def drawPost(self, x, y, properties):
        rect_width = rect_height = magnification_factor
        self.current_rect = CustomRectItem(properties)
        self.current_rect.setRect(x - rect_width / 2, y - rect_height / 2, rect_width, rect_height)
        mainText = QGraphicsProxyWidget()
        dcr = QLabel(f"Axial DCR: {properties['axial_dcr']}")
        font = QFont()
        font.setPointSize(10)
        dcr.setFont(font)
        mainText.setWidget(dcr)
        # text = QGraphicsTextItem("Hello, PySide6!")

        # Set the color of the text to red
        if properties["axial_dcr"] > 1:
            dcr.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : red; }")

        else:
            dcr.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : green; }")
        mainText.setPos(x - rect_width, y + 0.6 * rect_width)

        # LabelText = QLabel(label)
        self.scene.addItem(mainText)
        self.scene.addItem(self.current_rect)

        Label = QGraphicsProxyWidget()
        LabelText = QLabel(properties["label"])
        font = QFont()
        font.setPointSize(16)
        LabelText.setFont(font)
        LabelText.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : black; }")
        Label.setWidget(LabelText)

        # BeamLabel((x1 + x2) / 2, (y1 + y2) / 2, self.scene, properties["label"], direction)
        Label.setPos(x - 1.1 * rect_width, y - 1.1 * rect_width)

        self.scene.addItem(Label)
        #
        self.current_rect = None
        self.start_pos = None

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


class CustomRectItem(QGraphicsRectItem):
    def __init__(self, post_prop, *args, **kwargs):
        super(CustomRectItem, self).__init__(*args, **kwargs)
        # self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        if post_prop["axial_dcr"] > 1:
            self.setBrush(QBrush(QColor("#BB2525")))
        else:
            self.setBrush(QBrush(QColor("#A8DF8E")))

        # Properties
        self.post_properties_page = None
        self.post_prop = post_prop

    def mousePressEvent(self, event):
        pos = self.boundingRect().center().toTuple()
        # properties page open
        # if event.button() == Qt.RightButton:
        #     try:
        #         wallWidth_default = self.post_prop[self]["wall_width"]
        #         self.post_properties_page = PostProperties(self, self.post_prop)
        #         self.post_properties_page.show()
        #     except KeyError:
        #         pass


class PostStoryBy:
    def __init__(self, posts, GridClass, story):
        print(posts)
        # coordinate = [i["coordinate_main"] for i in beams]
        # label = [i["label"] for i in beams]
        # bending_dcr = [i["bending_dcr"] for i in beams]
        # shear_dcr = [i["shear_dcr"] for i in beams]
        # deflection_dcr = [i["deflection_dcr"] for i in beams]
        self.view = None
        # instance = DrawBeam()
        self.dialog = DrawPost(GridClass)
        self.dialog.story(story)

        self.view = self.dialog.view
        for Post in posts:
            start = Post["coordinate"][0] * magnification_factor
            end = Post["coordinate"][1] * magnification_factor
            self.dialog.drawPost(start, end, Post)
        self.dialog.Show()
        # self.dialog.show()
        self.result = self.dialog.exec()
