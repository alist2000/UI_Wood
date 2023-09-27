from PySide6.QtWidgets import QLabel


def DimensionLabel(length, magnification_factor):
    dimension = QLabel(str(round(abs(length / magnification_factor), 2)) + " ft(m)")
    dimension.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : black; }")
    return dimension


def CoordinateLabel(x, y, magnification_factor):
    dimension = QLabel(f"({str(round(x / magnification_factor, 2))}, {str(round(y / magnification_factor, 2))})")
    dimension.setStyleSheet("QLabel { background-color : rgba(255, 255, 255, 0); color : black; }")
    return dimension
