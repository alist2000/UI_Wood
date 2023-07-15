from PySide6.QtWidgets import QPushButton, QDialog, QVBoxLayout, QComboBox, QColorDialog


class Choose_load_and_color(QDialog):
    def __init__(self, loads, parent=None):
        super(Choose_load_and_color, self).__init__(parent)

        self.setWindowTitle("Choose Load")
        self.color = "#ffa7a8"
        self.loads = loads

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.color_button = QPushButton("Choose color")
        self.layout.addWidget(self.color_button)

        self.combo_box = QComboBox()
        self.combo_box.addItems(list(loads.keys()))
        self.layout.addWidget(self.combo_box)

        self.color_button.clicked.connect(self.change_color)

    def change_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color.name()
            print(self.color)
            self.close()
