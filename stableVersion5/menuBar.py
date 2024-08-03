from PySide6.QtWidgets import QMainWindow, QFileDialog, \
    QGraphicsPixmapItem, QGraphicsItem, QGraphicsOpacityEffect
from PySide6.QtGui import QPixmap, QAction, QImage
from UI_Wood.stableVersion5.styles import menuStyle
from UI_Wood.stableVersion5.post_new import magnification_factor
import cv2
import numpy as np
from PySide6.QtWidgets import QMainWindow, QMenuBar, QMenu, QFileDialog, QGraphicsItem
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QRectF
from PIL import Image as PILImage


class Image(QMainWindow):
    def __init__(self, grid, slider, y_grid):
        super(Image, self).__init__()
        self.view = grid
        self.scene = grid.scene
        self.slider = slider
        self.pixmapItem = None
        self.unlock = True
        self.image_path = None
        self.y_grid = y_grid
        self.magnification_factor = magnification_factor  # Add this line to define magnification_factor

        self.create_menu_bar()

    def create_menu_bar(self):
        # Create menu bar for individual tab
        menu_bar = QMenuBar()
        file_menu = QMenu("Image")
        menu_bar.setStyleSheet(menuStyle)
        file_menu.setStyleSheet(menuStyle)

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
            self.image_path = fileName
            try:
                q_image = self.scale_image()
                if q_image:
                    image = QPixmap.fromImage(q_image)
                else:
                    image = QPixmap(fileName)
                self.addImageToScene(image)

            except Exception as e:
                print(f"Error opening image: {str(e)}")

    def addImageToScene(self, image):
        if self.pixmapItem:
            self.scene.removeItem(self.pixmapItem)
            try:
                self.slider.valueChanged.disconnect(self.pixmapItem.adjust_transparency)
            except TypeError:
                pass

        self.pixmapItem = PixmapItem(image)
        self.pixmapItem.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.scene.addItem(self.pixmapItem)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.slider.valueChanged.connect(self.pixmapItem.adjust_transparency)

    def scale_image(self):
        if not self.image_path:
            return None

        try:
            # Open image with PIL
            pil_image = PILImage.open(self.image_path)
            width, height = pil_image.size

            main_distance = next((item.get('position', item.get('coordinate'))
                                  for item in self.y_grid if item.get('position') or item.get('coordinate')), None)

            if main_distance is None:
                print("Error: No valid distance found in y_grid")
                return None

            red_points = self.find_red_points(pil_image)
            if len(red_points) != 2:
                print(f"Error: Expected 2 red points, found {len(red_points)}")
                return None
            dist_red = self.calculate_distance(red_points[0], red_points[1])
            if dist_red == 0:
                print("Error: Distance between red points is zero")
                return None
            scale = (main_distance * self.magnification_factor) / dist_red

            new_width = max(1, int(width * scale))
            new_height = max(1, int(height * scale))
            resized_image = pil_image.resize((new_width, new_height), PILImage.LANCZOS)

            return self.pil_to_qimage(resized_image)
        except Exception as e:
            print(f"Error in scale_image: {str(e)}")
            return None

    def pil_to_qimage(self, pil_image):
        if pil_image.mode == "RGB":
            r, g, b = pil_image.split()
            pil_image = PILImage.merge("RGB", (b, g, r))
        elif pil_image.mode == "RGBA":
            r, g, b, a = pil_image.split()
            pil_image = PILImage.merge("RGBA", (b, g, r, a))
        elif pil_image.mode == "L":
            pil_image = pil_image.convert("RGBA")

        im_data = pil_image.tobytes("raw", pil_image.mode)
        qim = QImage(im_data, pil_image.size[0], pil_image.size[1], QImage.Format_RGBA8888)
        return qim

    def find_red_points(self, pil_image):
        try:
            # Convert PIL image to numpy array
            np_image = np.array(pil_image)

            # Convert to HSV color space
            hsv = cv2.cvtColor(np_image, cv2.COLOR_RGB2HSV)

            # Define range for red color
            lower_red = np.array([0, 100, 100])
            upper_red = np.array([10, 255, 255])
            mask1 = cv2.inRange(hsv, lower_red, upper_red)

            lower_red = np.array([160, 100, 100])
            upper_red = np.array([180, 255, 255])
            mask2 = cv2.inRange(hsv, lower_red, upper_red)

            mask = mask1 + mask2

            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Get centroids of contours
            red_points = []
            for contour in contours:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    red_points.append((cX, cY))

            return red_points
        except Exception as e:
            print(f"Error in find_red_points: {str(e)}")
            return []

    def calculate_distance(self, point1, point2):
        return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

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
        menu_bar.setStyleSheet(menuStyle)
        file_menu.setStyleSheet(menuStyle)

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
        if len(Keys) > 0:
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
