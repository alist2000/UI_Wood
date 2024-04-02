from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QPainter, QBrush, QPixmap
from UI_Wood.stableVersion5.path import PathHandler


def saveImage(grid, currentTab):
    # Create a QPixmap to hold the image of the scene
    border_size = 10  # Border size in pixels
    # border_color = QColor(Qt.black)  # Set border as black color
    margin_size = 20  # Margin size in pixels

    # Get the rectangle that contains all items
    rect = grid[currentTab].scene.itemsBoundingRect()

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
    grid[currentTab].scene.render(painter, scene_rect, rect)

    # End the QPainter to apply the drawing to the QPixmap
    painter.end()

    # Save the QPixmap as an image file
    pixmap.save(PathHandler(f"images/output/Story{currentTab + 1}.png"))
