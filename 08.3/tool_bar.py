from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QGraphicsView, QToolBar, \
    QMainWindow, QMenu, QMenuBar, QDialogButtonBox, QDialog, QLabel, QSpinBox, QDoubleSpinBox, QComboBox
from PySide6.QtWidgets import QMainWindow, QGraphicsScene, QToolBar, QFileDialog, QApplication, QGraphicsView, \
    QGraphicsPixmapItem, QGraphicsItem, QSlider, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtGui import QPixmap, QAction, QKeyEvent
from PySide6.QtCore import Qt, QPoint


class seismicParameters:
    def __init__(self, mainPage):
        self.mainPage = mainPage
        self.dialogPage = load_seismic_dialog(self)
        self.spin_values = [0, 0, 0, 0, 0, 0]
        self.combo_values = ["1"]
        self.create_tool_bar()

    def create_tool_bar(self):
        tool_bar = QToolBar("My Toolbar")
        self.mainPage.addToolBar(tool_bar)

        # Create a Save action
        seismic_parameters_action = QAction('Seismic Parameters', self.mainPage)
        seismic_parameters_action.triggered.connect(self.dialogPage.load_seismic_parameters)
        tool_bar.addAction(seismic_parameters_action)
        # saveAction.triggered.connect(self.save_tabs)


class load_seismic_dialog:
    def __init__(self, mainPage):
        self.mainPage = mainPage

    def load_seismic_parameters(self):
        print("hi")
        dialog = QDialog()
        dialog.setWindowTitle("Seismic Parameters")

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        spin_boxes = []
        combo_boxes = []
        labels_number = ["S1", "Ss", "Fa", "Fv", "T model", "R Factor"]
        # Create and add the labels and spin_boxes
        for i, label in enumerate(labels_number):
            h_layout = QHBoxLayout()
            Label = QLabel(f'{label} ')
            h_layout.addWidget(Label)

            self.create_spin_box(i, h_layout, spin_boxes)
            layout.addLayout(h_layout)

        # Create and add the labels and combo_boxes
        h_layout = QHBoxLayout()

        label = QLabel("Risk Category")
        h_layout.addWidget(label)

        combobox = QComboBox()
        combobox.addItems(["I & II", "III", "IV"])
        combobox.setCurrentText(self.mainPage.combo_values[0])
        h_layout.addWidget(combobox)
        layout.addLayout(h_layout)
        combo_boxes.append(combobox)

        # Create and add the OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)

        button_box.accepted.connect(lambda: self.save_values(spin_boxes, combo_boxes, dialog))
        button_box.rejected.connect(dialog.reject)

        dialog.exec_()

    def save_values(self, spin_boxes, combo_boxes, dialog):
        self.mainPage.spin_values = [spinbox.value() for spinbox in spin_boxes]
        self.mainPage.combo_values = [combobox.currentText() for combobox in combo_boxes]
        dialog.accept()

    def create_spin_box(self, i, layout, spin_boxes):
        spinbox = QSpinBox()
        spinbox.setValue(self.mainPage.spin_values[i])
        layout.addWidget(spinbox)
        spin_boxes.append(spinbox)


class Image(QMainWindow):
    def __init__(self, grid, slider):
        super(Image, self).__init__()
        self.view = grid
        self.scene = grid.scene
        self.slider = slider
        self.pixmapItem = None
        self.unlock = True
        # self.view.setDragMode(QGraphicsView.RubberBandDrag)

        self.create_menu_bar()

    def create_menu_bar(self):
        # Create menu bar for individual tab
        menu_bar = QMenuBar()
        file_menu = QMenu("Image")

        # Create a Save action
        openAction = QAction("Open", self, shortcut="Ctrl+O", triggered=self.openImage)
        file_menu.addAction(openAction)

        # Create a Load action
        deleteAction = QAction("Delete", self, shortcut="Del", triggered=self.deleteImage)
        file_menu.addAction(deleteAction)

        scaleUpAct = QAction("Scale Up", self, shortcut="Ctrl+]", triggered=self.scaleUp)
        file_menu.addAction(scaleUpAct)

        scaleDownAct = QAction("Scale Down", self, shortcut="Ctrl+[", triggered=self.scaleDown)
        file_menu.addAction(scaleDownAct)

        lockAct = QAction("Lock/Unlock", self, shortcut="Ctrl+L", triggered=self.toggleLock)
        file_menu.addAction(lockAct)

        menu_bar.addMenu(file_menu)

        self.setMenuBar(menu_bar)

    def openImage(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "",
                                                  "Images (*.png *.xpm *.jpg *.bmp);;All Files (*)", options=options)
        if fileName:
            image = QPixmap(fileName)
            if not image.isNull():
                self.addImageToScene(image)

    def addImageToScene(self, image):
        # self.scene.clear()
        for item in self.scene.selectedItems():
            if isinstance(item, PixmapItem):
                self.scene.removeItem(item)
                try:
                    self.slider.valueChanged.disconnect(item.adjust_transparency)
                except TypeError:
                    pass  # The signal was not connected to this slot
        self.pixmapItem = pixmapItem = PixmapItem(image)
        pixmapItem.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.scene.addItem(pixmapItem)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.slider.valueChanged.connect(pixmapItem.adjust_transparency)

    def deleteImage(self):
        for item in self.scene.selectedItems():
            if isinstance(item, PixmapItem):
                self.scene.removeItem(item)

    def toggleLock(self):
        self.unlock = not self.unlock
        # for item in self.scene.selectedItems():
        #     if isinstance(item, PixmapItem):
        #         if item.flags() & QGraphicsItem.ItemIsMovable:
        #             item.setFlags(item.flags() & ~QGraphicsItem.ItemIsMovable)
        #         else:
        #             item.setFlags(item.flags() | QGraphicsItem.ItemIsMovable)

    def scaleUp(self):
        for item in self.scene.selectedItems():
            if isinstance(item, PixmapItem):
                item.scaleUp()

    def scaleDown(self):
        for item in self.scene.selectedItems():
            if isinstance(item, PixmapItem):
                item.scaleDown()




class PixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap=None):
        super(PixmapItem, self).__init__(pixmap)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

    def scaleUp(self):
        self.setScale(self.scale() * 1.2)

    def scaleDown(self):
        self.setScale(self.scale() / 1.2)

    def adjust_transparency(self, value):
        self.opacity_effect.setOpacity(value / 100)
