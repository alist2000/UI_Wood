from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout
from widget import GridWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid Example")
        self.setGeometry(300, 300, 500, 500)
        self.grid_widget = GridWidget()
        self.setCentralWidget(self.grid_widget)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
