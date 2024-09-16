from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QGraphicsView, QToolBar, \
    QMainWindow, QMenu, QMenuBar, QDialogButtonBox, QDialog, QLabel, QDoubleSpinBox, QDoubleSpinBox, QComboBox


class Offset(QDialog):
    def __init__(self, offset):
        super(Offset, self).__init__()
        self.offset = offset
        self.setWindowTitle("Define Offset")

        self.spinbox = QDoubleSpinBox()
        self.spinbox.setRange(-20, 20)
        unit = QLabel("ft")
        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        # Create and add the OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        h_layout.addWidget(self.spinbox, 2)
        h_layout.addWidget(unit, 1)
        layout.addLayout(h_layout)
        layout.addWidget(button_box)

        button_box.accepted.connect(self.accept_control)
        button_box.rejected.connect(self.reject)
        self.setLayout(layout)

        self.exec()

    def accept_control(self):
        self.offset = self.spinbox.value()
        self.accept()
