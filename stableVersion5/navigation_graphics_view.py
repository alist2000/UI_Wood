from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import QPainter, QWheelEvent, QMouseEvent, QKeyEvent


class NavigationGraphicsView(QGraphicsView):
    sceneChanged = Signal()  # Signal to notify when the scene has changed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.pan_active = False
        self.last_pan_point = QPointF()

        self.sceneChanged.connect(self.fitInView)  # Connect the signal to fitInView

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.ControlModifier:
            # Zoom
            zoom_factor = 1.25 if event.angleDelta().y() > 0 else 1 / 1.25
            self.scale(zoom_factor, zoom_factor)
        elif event.modifiers() & Qt.AltModifier:
            # Horizontal scroll
            delta = event.angleDelta().x() if event.angleDelta().x() != 0 else event.angleDelta().y()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta)
        else:
            # Vertical scroll
            super().wheelEvent(event)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton or (
                event.button() == Qt.LeftButton and event.modifiers() & Qt.AltModifier):
            self.pan_active = True
            self.last_pan_point = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.pan_active:
            delta = event.position() - self.last_pan_point
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(delta.y()))
            self.last_pan_point = event.position()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton or (
                event.button() == Qt.LeftButton):
            self.pan_active = False
            self.setCursor(Qt.ArrowCursor)
            self.setDragMode(QGraphicsView.NoDrag)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Control, Qt.Key_Alt):
            self.setDragMode(QGraphicsView.NoDrag)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Control, Qt.Key_Alt):
            self.setDragMode(QGraphicsView.RubberBandDrag)
        super().keyReleaseEvent(event)

    def fitInView(self, rect: QRectF = None, aspect_ratio_mode: Qt.AspectRatioMode = Qt.KeepAspectRatio):
        if rect is None:
            rect = self.scene.itemsBoundingRect()  # Use .itemsBoundingRect() on self.scene()
            print("RECT: ", rect)
        if not rect.isNull():
            unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            view_rect = self.viewport().rect()
            scene_rect = self.transform().mapRect(rect)
            factor = min(view_rect.width() / scene_rect.width(),
                         view_rect.height() / scene_rect.height())
            self.scale(factor, factor)
            self.centerOn(rect.center())

    def setScene(self, scene: QGraphicsScene):
        super().setScene(scene)
        self.sceneChanged.emit()  # Emit the signal when the scene is set
