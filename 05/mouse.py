from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsItem


class SelectableLineItem(QGraphicsLineItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.setSelected(True)
            self.setPen(QPen(Qt.red, 2, Qt.SolidLine))  # Set pen on the SelectableLineItem object
            self.update()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.isSelected():
            self.setPen(QPen(Qt.blue, 2, Qt.SolidLine))  # Set pen on the SelectableLineItem object
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setSelected(False)
            self.setPen(QPen(Qt.black, 1, Qt.SolidLine))  # Set pen on the SelectableLineItem object
        super().mouseReleaseEvent(event)
