from PySide6.QtWidgets import QLabel


def DimensionLabel(length, magnification_factor):
    dimension = QLabel(str(round(abs(length / magnification_factor), 2)) + " ft(m)")
    dimension.setStyleSheet("QLabel { background-color : white; color : black; }")
    return dimension
