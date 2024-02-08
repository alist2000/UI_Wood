from PySide6.QtWidgets import QWidget, QPushButton, QDialog, QTabWidget, QTableWidgetItem, QGraphicsWidget, \
    QGraphicsScene, \
    QApplication, QVBoxLayout, QLabel, QTableWidgetItem, QTableWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor

from UI_Wood.stableVersion5.styles import TabWidgetStyle, tableStyle
from UI_Wood.stableVersion5.Sync.Transfer import Transfer
from UI_Wood.stableVersion5.Sync.data import Data


class TransferControl(Data):
    def __init__(self, saveFunc, grid, tabWidgetCount):
        super(TransferControl, self).__init__()

        self.saveFunc = saveFunc
        self.grid = grid
        self.tabWidgetCount = tabWidgetCount
        self.transferPage = None

    def transferClicked(self):
        for currentTab in range(self.tabWidgetCount - 1, -1, -1):
            self.grid[currentTab].run_control()

        self.saveFunc()

        tabReversed = self.reverse_dict(self.tab)  # top to bottom
        shearWallTop = None
        studWallTop = None
        TransferInstance = Transfer()
        j = 0
        for story, Tab in tabReversed.items():
            shearWall = Tab["shearWall"]
            studWall = Tab["studWall"]

            if j == 0:
                storySW = "Roof"
            else:
                storySW = str(story + 1)
            for item in shearWall:
                item["story"] = storySW
            for item in studWall:
                item["story"] = storySW
            # shearWall["story"] = storySW
            # studWall["story"] = storySW

            # CONTROL STACK
            TransferInstance.StackControl(shearWallTop, shearWall, storySW, "shearWall")
            TransferInstance.StackControl(studWallTop, studWall, storySW, "studWall")
            shearWallTop = shearWall
            studWallTop = studWall
            j += 1

        self.transferPage = TransferPage()
        self.transferPage.fill_tab(TransferInstance.transferListShearWall, "shearWall")
        self.transferPage.fill_tab(TransferInstance.transferListStudWall, "studWall")
        self.transferPage.show()

    @staticmethod
    def reverse_dict(Dict):
        key = list(Dict.keys())
        value = list(Dict.values())
        key.reverse()
        value.reverse()
        newDict = {}
        for k, v in zip(key, value):
            newDict[k] = v

        return newDict


class TransferPage(QTabWidget):
    def __init__(self):
        super(TransferPage, self).__init__()
        # Get the screen's available geometry
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        # Apply some basic styling to the QTabWidget
        self.setStyleSheet(TabWidgetStyle)
        # Calculate the position to center the window
        window_width = 800
        window_height = 600
        pos_x = (screen_geometry.width() - window_width) // 2
        pos_y = (screen_geometry.height() - window_height) // 2

        # Set the size and position of the window
        self.resize(window_width, window_height)
        self.move(pos_x, pos_y)
        self.table_widget1 = QTableWidget(self)
        self.table_widget2 = QTableWidget(self)
        self.addTab(self.table_widget1, "ShearWall")
        self.addTab(self.table_widget2, "StudWall")
        # Connect the tabChanged signal to a slot that animates the color change
        # self.currentChanged.connect(self.animate_tab_click)

    def fill_tab(self, transferredData, itemName):
        if itemName == "shearWall":
            table_widget = self.table_widget1
        else:
            table_widget = self.table_widget2

        table_widget.setRowCount(len(transferredData))
        table_widget.setColumnCount(3)
        table_widget.setHorizontalHeaderLabels(['Label', 'Story', 'Transfer To'])
        # Fill the table with some data
        for i, item in enumerate(transferredData):
            label = QTableWidgetItem(item["label"])
            story = QTableWidgetItem(item["story"])
            select = QTableWidgetItem("SELECT")
            table_widget.setItem(i, 0, label)
            table_widget.setItem(i, 1, story)
            table_widget.setItem(i, 2, select)

    def animate_tab_click(self, index):
        # Create a new property animation for the background color
        animation = QPropertyAnimation(self.tabBar(), b"background-color", self)
        animation.setDuration(200)  # Duration in milliseconds
        animation.setStartValue(QColor("#FFFFFF"))  # Start color
        animation.setEndValue(QColor("#F0F0F0"))  # End color
        animation.setEasingCurve(QEasingCurve.OutQuad)  # Easing curve for smoothness
        animation.start()
