from PySide6.QtWidgets import QApplication, QMainWindow
from tab_widget import tabWidget
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = tabWidget()
    window.show()
    app.exec()
