import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QWidget, \
    QPushButton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Input Boxes")

        # Create a combo box with options
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Option 1", "Option 2", "Option 3"])
        self.combo_box.currentIndexChanged.connect(self.index_changed)

        # Create input boxes and add them to the layout
        self.input_boxes = []
        for i in range(3):
            input_box = QLineEdit()
            self.input_boxes.append(input_box)
            layoutt = QVBoxLayout()
            layoutt.addWidget(input_box)

        # Set the layout for the main window
        layout = QVBoxLayout()
        self.Layout = layout
        layout.addWidget(self.combo_box)
        layout.addStretch()

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.central_widget = central_widget

        self.setCentralWidget(central_widget)

    def index_changed(self, index):
        if index == 0:
            button = QPushButton("000")
        elif index == 1:
            button = QPushButton("111")

        last_item = self.central_widget.layout().itemAt(2)
        if last_item:
            last_item = last_item.layout()
            self.central_widget.layout().removeItem(last_item)

        h_layout = QHBoxLayout()
        h_layout.addWidget(button)
        self.Layout.addLayout(h_layout)
        # Hide or show input boxes based on the selected index
        for i, input_box in enumerate(self.input_boxes):
            input_box.setVisible(index == i)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
