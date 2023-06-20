from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QGraphicsPixmapItem


class image_control:
    def __init__(self, x, y, width, height, rectItem):
        self.path = "images/n_s.png"

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rectItem = rectItem

        # Create a QGraphicsPixmapItem with the image
        self.image = image = QPixmap(self.path)
        image = size_image(self.width, self.height, self.rectItem, self.image)

        self.pixmap_item = QGraphicsPixmapItem(image, rectItem)

        # Calculate the position to center the pixmap item within the parent rectangle
        pixmap_width = self.pixmap_item.pixmap().width()
        pixmap_height = self.pixmap_item.pixmap().height()
        pixmap_x = x + (width - pixmap_width) / 2
        pixmap_y = y + (height - pixmap_height) / 2

        # Set the pixmap item's position
        self.pixmap_item.setPos(pixmap_x, pixmap_y)

    def change_image(self, path, scene):
        self.path = path

        # Remove the pixmap item from the scene
        scene.removeItem(self.pixmap_item)
        # Delete the pixmap item
        del self.pixmap_item
        self.pixmap_item = None

        # Create a QGraphicsPixmapItem with the image
        self.image = QPixmap(self.path)

        image = size_image(self.width, self.height, self.rectItem, self.image)
        self.pixmap_item = QGraphicsPixmapItem(image, self.rectItem)

        # Calculate the position to center the pixmap item within the parent rectangle
        pixmap_width = self.pixmap_item.pixmap().width()
        pixmap_height = self.pixmap_item.pixmap().height()
        pixmap_x = self.x + (self.width - pixmap_width) / 2
        pixmap_y = self.y + (self.height - pixmap_height) / 2

        # Set the pixmap item's position
        self.pixmap_item.setPos(pixmap_x, pixmap_y)


def size_image(width, height, rectItem, image):
    # Calculate the new width and height
    image_aspect_ratio = image.width() / image.height()
    rect_aspect_ratio = width / height

    if image_aspect_ratio > rect_aspect_ratio:
        new_width = width
        new_height = int(width / image_aspect_ratio)
    else:
        new_width = int(height * image_aspect_ratio)
        new_height = height

    # Ensure the new dimensions do not exceed the rectangle dimensions
    new_width = min(new_width, width)
    new_height = min(new_height, height)

    # Scale the image based on the new width and height, maintaining the aspect ratio
    scaled_image = image.scaled(new_width, new_height, Qt.KeepAspectRatio)
    return scaled_image
