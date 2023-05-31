from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from widget import GridWidget
from PySide6.QtGui import QCloseEvent


class DataPlotting(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Data Plotting")
        self.setGeometry(300, 300, 400, 400)

    def closeEvent(self, event: QCloseEvent):
        # You can add any custom logic here before the window is closed.
        print("Closing DataPlotting window")
        event.accept()  # Accept the close event to close the window.


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid Example")
        self.setGeometry(300, 300, 400, 400)
        self.grid_widget = GridWidget()
        self.setCentralWidget(self.grid_widget)

        self.data_plotting_button = QPushButton("Open Data Plotting", self)
        self.data_plotting_button.setGeometry(10, 10, 150, 30)
        self.data_plotting_button.clicked.connect(self.open_data_plotting)

    def open_data_plotting(self):
        self.data_plotting_window = DataPlotting(self)
        self.data_plotting_window.show()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
