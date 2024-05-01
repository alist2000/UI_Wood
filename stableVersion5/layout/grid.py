from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem
from PySide6.QtGui import QColor
import numpy as np
from UI_Wood.stableVersion5.line import LineDrawHandler
from UI_Wood.stableVersion5.post_new import magnification_factor
from UI_Wood.stableVersion5.line import PointDrawing

color = QColor.fromRgb(0, 0, 255)
color_range = np.array([0, 0, 255])


class GridWidget(QGraphicsView):
    def __init__(self, x_grid, y_grid, gridBase, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        line = LineDrawHandler(x_grid, y_grid, self.scene, None, None, gridBase)
        self.lineLabels, self.boundaryLineLabels, self.x_grid, self.y_grid = line.output()
        pointDrawing = PointDrawing(self.scene)
        points = pointDrawing.FindPoints(self.x_grid, self.y_grid)
        pointDrawing.Draw(points, color)
        print("Finish Grid Drawing")
