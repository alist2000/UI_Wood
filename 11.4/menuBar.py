from PySide6.QtWidgets import QToolBar, \
    QMainWindow, QMenu, QMenuBar
from PySide6.QtWidgets import QMainWindow, QFileDialog, \
    QGraphicsPixmapItem, QGraphicsItem, QGraphicsOpacityEffect
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtCore import Qt


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

        hideShow = QAction("Hide/Show", self, shortcut="Ctrl+H", triggered=self.hide_show)
        file_menu.addAction(hideShow)

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

    def hide_show(self):
        if self.pixmapItem:
            self.pixmapItem.setVisible(not self.pixmapItem.isVisible())


class visual(QMainWindow):
    def __init__(self, grid, postProp, beamProp, joistProp, shearWallProp, studWallProp, loadMapProp):
        super(visual, self).__init__()
        self.view = grid
        self.postProp = postProp
        self.beamProp = beamProp
        self.shearWallProp = shearWallProp
        self.joistProp = joistProp
        self.studWallProp = studWallProp
        self.loadMapProp = loadMapProp
        self.scene = grid.scene
        self.pixmapItem = None
        self.unlock = True
        # self.view.setDragMode(QGraphicsView.RubberBandDrag)

        self.create_menu_bar()

    def create_menu_bar(self):
        # Create menu bar for individual tab
        menu_bar = QMenuBar()
        file_menu = QMenu("Visual Setting")

        # Create a Save action
        postAction = QAction("Post Hide/Show", self, shortcut="Ctrl+Shift+P", triggered=self.postHideShow)
        file_menu.addAction(postAction)

        # Create a Load action
        beamAction = QAction("Beam Hide/Show", self, shortcut="Ctrl+Shift+B", triggered=self.beamHideShow)
        file_menu.addAction(beamAction)

        shearWallAct = QAction("Shear Wall Hide/Show", self, shortcut="Ctrl+Shift+S", triggered=self.shearWallHideShow)
        file_menu.addAction(shearWallAct)

        joistAct = QAction("Joist Hide/Show", self, shortcut="Ctrl+Shift+J", triggered=self.joistHideShow)
        file_menu.addAction(joistAct)

        studWallAct = QAction("Stud Wall Hide/Show", self, shortcut="Ctrl+Shift+T", triggered=self.studWallHideShow)
        file_menu.addAction(studWallAct)

        loadMapAct = QAction("Load Map Hide/Show", self, shortcut="Ctrl+Shift+L", triggered=self.loadMapHideShow)
        file_menu.addAction(loadMapAct)

        menu_bar.addMenu(file_menu)

        self.setMenuBar(menu_bar)

    @staticmethod
    def hide_show(Keys):
        firstKey = Keys[0].isVisible()
        for key in Keys:
            key.setVisible(not firstKey)

    def postHideShow(self):
        Keys = list(self.postProp.keys())
        self.hide_show(Keys)

    def beamHideShow(self):
        Keys = list(self.beamProp.keys())
        self.hide_show(Keys)

    def shearWallHideShow(self):
        Keys = list(self.shearWallProp.keys())
        self.hide_show(Keys)

    def joistHideShow(self):
        Keys = list(self.joistProp.keys())
        self.hide_show(Keys)

    def studWallHideShow(self):
        Keys = list(self.studWallProp.keys())
        self.hide_show(Keys)

    def loadMapHideShow(self):
        Keys = list(self.loadMapProp.keys())
        self.hide_show(Keys)


class PixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap=None):
        super(PixmapItem, self).__init__(pixmap)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

    def scaleUp(self):
        self.setScale(self.scale() * 1.01)

    def scaleDown(self):
        self.setScale(self.scale() / 1.01)

    def adjust_transparency(self, value):
        self.opacity_effect.setOpacity(value / 100)
