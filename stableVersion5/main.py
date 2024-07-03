from path import main_path, directories, HandleDirectories

if __name__ == "__main__":
    main_path()
    from PySide6.QtWidgets import QApplication
    from welcome import Welcome
    from tab_widget import tabWidget
    import sys

    dirs = HandleDirectories(directories)
    dirs.make_all()
    app = QApplication(sys.argv)
    welcomePage = Welcome()
    # Finish the splash screen after the main window is loaded
    window = tabWidget()
    welcomePage.splash.finish(window)
    window.show()
    app.exec()
