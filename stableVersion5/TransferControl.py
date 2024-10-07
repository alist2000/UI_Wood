import copy

from PySide6.QtWidgets import QWidget, QPushButton, QDialog, QTabWidget, QListWidget, QGraphicsWidget, \
    QGraphicsScene, \
    QApplication, QVBoxLayout, QLabel, QListWidgetItem, QTableWidget, QHBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor

from UI_Wood.stableVersion5.styles import TabWidgetStyle, ButtonCheck
from UI_Wood.stableVersion5.Sync.Transfer import Transfer
from UI_Wood.stableVersion5.Sync.data import Data
from UI_Wood.stableVersion5.post_new import magnification_factor
from UI_Wood.stableVersion5.run.shearWall import DrawShearWall
from UI_Wood.stableVersion5.Sync.shearWallSync import EditLabels


class TransferControl(Data):
    def __init__(self, saveFunc, grid, tabWidgetCount, GridDrawClass):
        super(TransferControl, self).__init__()

        self.saveFunc = saveFunc
        self.grid = grid
        self.tabWidgetCount = tabWidgetCount
        self.GridDrawClass = GridDrawClass
        self.transferPage = None

    def transferClicked(self):
        shearWallsValues = []
        shearWallsKeys = []
        for currentTab in range(self.tabWidgetCount - 1, -1, -1):
            self.grid[currentTab].run_control()
            shearWall = self.grid[currentTab].shearWall_instance.shearWall_rect_prop
            studWall = self.grid[currentTab].studWall_instance.studWall_rect_prop
            shearWallsValues.append(list(shearWall.values()))
            shearWallsKeys.append(list(shearWall.keys()))
        shearWallsEdited = EditLabels(shearWallsValues)
        shearWallsEdited.reverse()
        shearWallsKeys.reverse()
        for currentTab in range(self.tabWidgetCount - 1, -1, -1):
            shearWallDict = {}
            for i in range(len(shearWallsEdited[currentTab])):
                try:
                    shearWallDict[shearWallsKeys[currentTab][i]] = shearWallsEdited[currentTab][i]
                except:
                    pass
            self.grid[currentTab].shearWall_instance.shearWall_rect_prop = shearWallDict

        self.saveFunc()

        tabReversed = self.reverse_dict(self.tab)  # top to bottom
        shearWallTop = None
        studWallTop = None
        TransferInstance = Transfer()
        j = 0
        shearWalls = []
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
            shearWalls.append(shearWall)
            j += 1

        self.transferPage = TransferPage(self.GridDrawClass, shearWalls)
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
    def __init__(self, GridDrawClass, shearWalls):
        super(TransferPage, self).__init__()
        # Get the screen's available geometry
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        # Apply some basic styling to the QTabWidget
        self.setStyleSheet(TabWidgetStyle)
        self.GridDrawClass = GridDrawClass
        self.shearWalls = shearWalls
        self.ShearWallSelectionInstance = []

        # Calculate the position to center the window
        window_width = 400
        window_height = 300
        pos_x = (screen_geometry.width() - window_width) // 2
        pos_y = (screen_geometry.height() - window_height) // 2

        # Set the size and position of the window
        self.resize(window_width, window_height)
        self.move(pos_x, pos_y)
        self.list_widget1 = QListWidget(self)
        self.list_widget2 = QListWidget(self)
        self.addTab(self.list_widget1, "ShearWall")
        self.addTab(self.list_widget2, "StudWall")

    def fill_tab(self, transferredData, itemName):
        if itemName == "shearWall":
            list_widget = self.list_widget1
        else:
            list_widget = self.list_widget2

        widget = QWidget()
        titleLayout = QHBoxLayout(widget)
        # Clear the list widget before filling it
        list_widget.clear()
        if transferredData:
            # Add labels
            label = QLabel("Label")
            story = QLabel("Story")
            if itemName == "shearWall":
                transferTo = QLabel("Transfer To")
                titles = [label, story, transferTo]
            else:
                titles = [label, story]
        else:
            label = QLabel(f"All {itemName}s are stack.")
            titles = [label]
        for i in titles:
            i.setStyleSheet("""
                font-family: 'Arial';
                font-size:  14pt;
                font-weight: bold;
            """)

            titleLayout.addWidget(i)
        # Create a QListWidgetItem to hold the custom widget
        list_item = QListWidgetItem(list_widget)
        list_item.setSizeHint(widget.sizeHint())

        # Set the custom widget as the item's widget
        list_widget.setItemWidget(list_item, widget)

        # Fill the list widget with custom widgets

        for item in transferredData:
            instance = ShearWallSelection(item, self.shearWalls, self.GridDrawClass, itemName)
            self.ShearWallSelectionInstance.append(instance)
            widget = instance.create_widget()
            # # Create a custom widget for each item
            # widget = QWidget()
            # layout = QHBoxLayout(widget)
            #
            # # Add labels
            # label = QLabel(item["label"])
            # story = QLabel(item["story"])
            # layout.addWidget(label)
            # layout.addWidget(story)
            # self.ShearWallSelectionInstance.chooseStory(item["transfer_to_story"], item)
            # print("transfer_to_story", item["transfer_to_story"])
            # # Add a button
            #
            # if itemName == "shearWall":
            #     if item.get("transfer_to"):
            #         button = QPushButton("Check")
            #     else:
            #         button = QPushButton("Select")
            #     button.clicked.connect(self.ShearWallSelectionInstance.run)
            #     # button.clicked.connect(self.test)
            #     layout.addWidget(button)

            # Create a QListWidgetItem to hold the custom widget
            list_item = QListWidgetItem(list_widget)
            list_item.setSizeHint(widget.sizeHint())

            # Set the custom widget as the item's widget
            list_widget.setItemWidget(list_item, widget)


class SelectionPage(QDialog):
    def __init__(self, shearWalls):
        super(SelectionPage, self).__init__()
        self.shearWalls = shearWalls
        self.currentLabel = None
        self.currentStory = None
        self.setWindowTitle("Selection Page")
        self.setGeometry(100, 100, 300, 200)
        self.show()

    def updateCurrant(self, label, story):
        self.currentLabel = label
        self.currentStory = story


class ShearWallSelection:
    def __init__(self, transferredShearWall, shearWalls, GridClass, itemName):
        print(shearWalls)
        self.view = None
        # instance = DrawShearWall()
        self.dialog = None
        self.result = None
        self.story = None
        self.transferredShearWall = None
        self.shearWallsTarget = None
        self.selectedWalls = []
        self.shearWalls = shearWalls
        self.GridClass = GridClass
        # Create a custom widget for each item
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Add labels
        label = QLabel(transferredShearWall["label"])
        story = QLabel(transferredShearWall["story"])
        layout.addWidget(label)
        layout.addWidget(story)
        self.chooseStory(transferredShearWall["transfer_to_story"], transferredShearWall)
        print("transfer_to_story", transferredShearWall["transfer_to_story"])
        # Add a button
        if itemName == "shearWall":
            if transferredShearWall.get("transfer_to"):
                self.selectedWalls = transferredShearWall["transfer_to"]
                self.button = QPushButton("Check")
                self.button.setStyleSheet(ButtonCheck)

            else:
                self.button = QPushButton("Select")
            self.button.clicked.connect(self.run)

            # button.clicked.connect(
            #     lambda row=transferredShearWall["transfer_to_story"]: print(f"Button clicked in row {row}"))
            # button.clicked.connect(self.test)
            layout.addWidget(self.button)
        self.widget = widget

        # coordinate = [i["coordinate_main"] for i in shearWalls]
        # label = shearWalls
        # bending_dcr = [i["bending_dcr"] for i in shearWalls]
        # shear_dcr = [i["shear_dcr"] for i in shearWalls]
        # deflection_dcr = [i["deflection_dcr"] for i in shearWalls]

    def create_widget(self):
        return self.widget

    def chooseStory(self, story, transferredShearWall):
        self.story = story
        self.transferredShearWall = transferredShearWall
        if story == "Roof":
            self.shearWallsTarget = self.shearWalls[0]
        else:
            storyIndex = len(self.shearWalls) - int(story)
            self.shearWallsTarget = self.shearWalls[storyIndex]

    def run(self):
        self.dialog = None
        self.dialog = DrawShearWall(self.GridClass)
        self.dialog.setTitle("Transfer Page")
        self.dialog.story(self.story)

        self.view = self.dialog.view
        for shearWall in self.shearWallsTarget:
            start = shearWall["coordinate"][0]
            end = shearWall["coordinate"][1]
            self.dialog.finalize_rectangle_copy(start, end, shearWall, shearWall["label"])

        start = self.transferredShearWall["coordinate"][0]
        end = self.transferredShearWall["coordinate"][1]
        self.dialog.finalize_rectangle_copy(start, end, self.transferredShearWall, self.transferredShearWall["label"],
                                            True)
        primarySelectedShearWalls = copy.deepcopy(self.selectedWalls)
        self.selectedWalls = self.dialog.ShowTransfer(self.selectedWalls)
        self.transferredShearWall["transfer_to"] = []
        # self.dialog.show()
        self.result = self.dialog.exec()

        if self.result == QDialog.Accepted:
            print("accepted")
            for wall in self.selectedWalls:
                self.transferredShearWall["transfer_to"].append({"label": wall["label"], "percent": wall["percent"], "pe": wall["pe"]})
        else:
            self.selectedWalls = primarySelectedShearWalls

        if self.selectedWalls:
            self.button.setText("Check")
            self.button.setStyleSheet(ButtonCheck)
        else:
            self.button.setText("Select")
            self.button.setStyleSheet(TabWidgetStyle)

        print("selected walls: ", self.selectedWalls)
        print("Run clicked.")
