from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsTextItem
from PySide6.QtGui import QPainterPath
from PySide6.QtCore import Qt
from PySide6.QtCore import Qt, Signal, QObject, QEvent
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
from UI_Wood.stableVersion3.post_new import magnification_factor
from UI_Wood.stableVersion3.pointer_control import control_post_range, range_post, beam_end_point, \
    selectable_beam_range, \
    control_selectable_beam_range
from UI_Wood.stableVersion3.layout.LineDraw import BeamLabel


class DrawBeam(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Continue or Break?")

        self.mainLayout = QVBoxLayout()
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.current_rect = None
        self.start_pos = None
        self.beam_select_status = 0  # 0: neutral, 1: select beam, 2: delete beam
        self.other_button = None
        # self.beam_width = min(min(x), min(y)) / 25  # Set beam width
        self.beam_width = magnification_factor / 2  # Set beam width
        # self.post_dimension = min(min(x), min(y)) / 8  # Set post dimension
        self.post_dimension = magnification_factor  # Set post dimension
        self.dimension = None

        # coordinate = properties["coordinate"]
        # x1, y1 = coordinate[0]
        # x2, y2 = coordinate[1]
        # self.finalize_rectangle_copy((x1, y1), (x2, y2), properties)

    def finalize_rectangle_copy(self, start, end, properties):

        x1, y1 = start
        x2, y2 = end
        self.current_rect = Rectangle(x1 - self.beam_width / 2,
                                      y1 - self.beam_width / 2, properties)

        self.scene.addItem(self.current_rect)

        # Label = QGraphicsProxyWidget()
        # LabelText = QLabel(properties["label"])
        # LabelText.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : black; }")
        # Label.setWidget(LabelText)

        width = abs(x2 - x1)
        height = abs(y2 - y1)
        # x, y = (x1 + x2) / 2, (y1 + y2) / 2

        if abs(width) > abs(height):
            self.current_rect.setRect(min(x1, x2),
                                      y1 - self.beam_width / 2, abs(width), self.beam_width)
            # Label.setPos(x - 7, y - 30)
            direction = "E-W"

        else:
            self.current_rect.setRect(x1 - self.beam_width / 2,
                                      min(y1, y2), self.beam_width,
                                      abs(height))
            # Label.setPos(x + 30, y - 7)
            # Label.setRotation(90)
            direction = "N-S"

        BeamLabel((x1 + x2) / 2, (y1 + y2) / 2, self.scene, properties["label"], direction)

        # self.scene.addItem(Label)

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
            self.current_rect.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
            self.current_rect.setBrush(QBrush(QColor.fromRgb(245, 80, 80, 100), Qt.SolidPattern))
        else:
            self.current_rect.setPen(QPen(QColor.fromRgb(150, 194, 145, 100), 2))
            self.current_rect.setBrush(QBrush(QColor.fromRgb(150, 194, 145, 100), Qt.SolidPattern))

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


class Rectangle(QGraphicsRectItem):
    def __init__(self, x, y, rect_prop):
        super().__init__(x, y, 0, 0)
        self.setPen(QPen(Qt.blue, 2))  # Set the border color to blue
        self.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))  # Set the fill color to transparent

        self.rect_prop = rect_prop
        self.beam_properties_page = None

    # CONTROL ON BEAM
    def mousePressEvent(self, event):
        center = self.boundingRect().center().toTuple()
        # properties page open
        if event.button() == Qt.RightButton:  # beam Properties page
            height = self.boundingRect().height() - 1  # ATTENTION: I don't know why but this method return height + 1
            width = self.boundingRect().width() - 1  # ATTENTION: I don't know why but this method return width + 1
            # self.beam_properties_page = BeamProperties(self, self.rect_prop,
            #                                            self.scene())
            # self.beam_properties_page.show()
            print(f"BEAM {self.rect_prop['label']} CLICKED")


class BeamStoryBy:
    def __init__(self, beams):
        print(beams)
        # coordinate = [i["coordinate_main"] for i in beams]
        # label = [i["label"] for i in beams]
        # bending_dcr = [i["bending_dcr"] for i in beams]
        # shear_dcr = [i["shear_dcr"] for i in beams]
        # deflection_dcr = [i["deflection_dcr"] for i in beams]
        self.view = None
        # instance = DrawBeam()
        self.dialog = DrawBeam()

        self.view = self.dialog.view
        for beam in beams:
            start = beam["coordinate_main"][0]
            end = beam["coordinate_main"][1]
            self.dialog.finalize_rectangle_copy(start, end, beam)
        self.dialog.Show()
        # self.dialog.show()
        self.result = self.dialog.exec()


class BeamProperties(QDialog):
    def __init__(self, rectItem, rect_prop, scene, parent=None):
        super().__init__(parent)
        self.direction = None
        self.rectItem = rectItem
        self.rect_prop = rect_prop
        self.beamDepth = None

        # IMAGE
        self.scene = scene

        self.setWindowTitle("Beam Properties")
        self.setMinimumSize(200, 400)

        v_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setWindowTitle("Object Data")
        self.button_box = button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept_control)  # Change from dialog.accept to self.accept
        self.button_box.rejected.connect(self.reject)  # Change from dialog.reject to self.reject

        self.create_geometry_tab()

        v_layout.addWidget(self.tab_widget)
        v_layout.addWidget(button_box)
        self.setLayout(v_layout)  # Change from dialog.setLayout to self.setLayout

    # Rest of the code remains the same

    # dialog.show()

    def accept_control(self):
        self.accept()

        print(self.rect_prop)

    def create_geometry_tab(self):
        start = tuple([round(i / magnification_factor, 2) for i in self.rect_prop["coordinate_main"][0]])
        end = tuple([round(i / magnification_factor, 2) for i in self.rect_prop["coordinate_main"][1]])
        tab = QWidget()
        self.tab_widget.addTab(tab, f"Check")
        label0 = QLabel("Label")
        joistLabel = QLabel(self.rect_prop["label"])
        label1 = QLabel("Start")
        start_point = QLabel(f"{start}")
        label2 = QLabel("End")
        end_point = QLabel(f"{end}")

        # calc length
        l = self.length(start, end)
        label3 = QLabel("Length")
        length = QLabel(f"{l}")

        # LAYOUT
        h_layout0 = QHBoxLayout()
        h_layout0.addWidget(label0)
        h_layout0.addWidget(joistLabel)
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(label1)
        h_layout1.addWidget(start_point)
        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(label2)
        h_layout2.addWidget(end_point)
        h_layout3 = QHBoxLayout()
        h_layout3.addWidget(label3)
        h_layout3.addWidget(length)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout0)
        v_layout.addLayout(h_layout1)
        v_layout.addLayout(h_layout2)
        v_layout.addLayout(h_layout3)
        tab.setLayout(v_layout)

    def beam_depth_control(self):
        depth = self.beamDepth.currentText()
        if "10" in depth:
            floor = False
        else:
            floor = True
        self.rect_prop[self.rectItem]["floor"] = floor

    @staticmethod
    def length(start, end):
        x1 = start[0]
        x2 = end[0]
        y1 = start[1]
        y2 = end[1]
        l = (((y2 - y1) ** 2) + ((x2 - x1) ** 2)) ** 0.5
        return round(l, 2)
