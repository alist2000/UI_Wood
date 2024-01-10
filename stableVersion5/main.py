from PySide6.QtWidgets import QApplication
from welcome import Welcome
from tab_widget import tabWidget
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcomePage = Welcome()
    # Finish the splash screen after the main window is loaded
    window = tabWidget()
    welcomePage.splash.finish(window)
    window.show()
    app.exec()
