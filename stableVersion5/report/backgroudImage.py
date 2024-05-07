from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QLabel, \
    QFileDialog
from UI_Wood.stableVersion5.styles import ButtonCheck, ButtonUnCheck, TabWidgetStyle


class ImageSelector(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.imagePath = None

        self.image_label = QLabel()

        layout.addWidget(self.image_label)

        self.select_button = QPushButton("Select Image")

        self.select_button.clicked.connect(self.open_image_dialog)
        self.setStyleSheet(TabWidgetStyle)
        layout.addWidget(self.select_button)

    def open_image_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
                                                   "Image Files (*.png *.jpg *.jpeg)", options=options)
        if file_path:
            self.select_button.setStyleSheet(ButtonCheck)
            self.imagePath = file_path
        else:
            self.select_button.setStyleSheet(ButtonUnCheck)
            self.imagePath = None

            # pixmap = QPixmap(file_path)
            # self.image_label.setPixmap(pixmap)
