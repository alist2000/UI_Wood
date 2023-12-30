from PySide6.QtWidgets import QApplication, QSplashScreen, QTabWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os
import time


class Welcome:
    def __init__(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        image_path = os.path.join(script_dir, 'images', 'logo.png')
        print(image_path)
        splash_pix = load_scaled_pixmap(image_path)
        self.splash = QSplashScreen(splash_pix)
        self.splash.show()

        # Simulate long loading time
        time.sleep(3)


def load_scaled_pixmap(image_path):
    # Get the screen size
    screen_geometry = QApplication.primaryScreen().availableGeometry()

    # Calculate the desired width and height
    desired_width = int(screen_geometry.width() * 2 / 3)
    desired_height = int(screen_geometry.height() * 4 / 5)

    # Load the pixmap from the image file
    pixmap = QPixmap(image_path)

    # Scale the pixmap to the desired size while maintaining aspect ratio
    scaled_pixmap = pixmap.scaled(desired_width, desired_height, Qt.AspectRatioMode.KeepAspectRatio)

    return scaled_pixmap
