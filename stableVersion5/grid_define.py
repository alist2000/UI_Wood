from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDoubleSpinBox, QLabel, QPushButton, \
    QTextEdit, QAbstractItemView, QTableWidget, \
    QRadioButton, QGraphicsView, QGraphicsScene
from UI_Wood.stableVersion5.line import LineDrawHandler

import copy


class GridLineDefine(QWidget):
    def __init__(self, coordinateButton, spacingButton, x_or_y="x", gridData=None):
        super(GridLineDefine, self).__init__()
        self.coordinateButton = coordinateButton
        self.spacingButton = spacingButton
        self.x_or_y = x_or_y
        self.gridData = gridData
        self.grid_base = None
        self.gridBase()
        if not self.grid_base:
            self.grid_base = "coordinate"
        self.layout = QVBoxLayout(self)

        # Connect signals
        self.coordinateButton.toggled.connect(self.on_button_toggled)
        self.spacingButton.toggled.connect(self.on_button_toggled)
        self.buttonAdd = QPushButton("Add")
        self.buttonDelete = QPushButton("Delete")
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.addWidget(self.buttonAdd)
        self.buttons_layout.addWidget(self.buttonDelete)
        self.tableWidgetXGrid = QTableWidget(0, 4)
        self.tableWidgetXGrid.insertRow(0)
        nameLabel = QLabel("Name")
        coordLabel = QLabel(self.grid_base.capitalize())
        startLabel = QLabel("Start")
        endLabel = QLabel("End")
        nameLabel.setAlignment(Qt.AlignCenter)
        coordLabel.setAlignment(Qt.AlignCenter)
        startLabel.setAlignment(Qt.AlignCenter)
        endLabel.setAlignment(Qt.AlignCenter)
        self.tableWidgetXGrid.setCellWidget(0, 0, nameLabel)
        self.tableWidgetXGrid.setCellWidget(0, 1, coordLabel)
        self.tableWidgetXGrid.setCellWidget(0, 2, startLabel)
        self.tableWidgetXGrid.setCellWidget(0, 3, endLabel)
        self.layoutTable = QHBoxLayout()
        self.layoutTable.addWidget(self.tableWidgetXGrid)
        self.layoutTable.addLayout(self.buttons_layout)

        self.tableWidgetXGrid.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidgetXGrid.horizontalHeader().setVisible(False)  # hide column headers

        self.layout.addLayout(self.layoutTable)

        self.setLayout(self.layout)

        self.buttonAdd.clicked.connect(self.add_item)
        self.buttonDelete.clicked.connect(self.delete_item)
        if self.gridData:
            for row in self.gridData:
                self.add_item(row)
        self.row_values = []

    def on_button_toggled(self, checked):
        if "Coordinate" in self.sender().text() and checked:
            item = QLabel("Coordinate")
            item.setAlignment(Qt.AlignCenter)
            self.tableWidgetXGrid.setCellWidget(0, 1, item)
            self.grid_base = "coordinate"
            firstCoord = 0
            print("self.tableWidgetXGrid.rowCount()", self.tableWidgetXGrid.rowCount())
            for i in range(1, self.tableWidgetXGrid.rowCount()):
                old_value = self.tableWidgetXGrid.cellWidget(i, 1).value()
                new_value = firstCoord + old_value
                firstCoord = copy.deepcopy(new_value)
                item = QDoubleSpinBox()
                item.setAlignment(Qt.AlignCenter)
                if i == 1:
                    item.setRange(0, 10000)
                else:
                    item.setRange(1, 10000)
                item.setDecimals(4)
                item.setValue(new_value)
                self.tableWidgetXGrid.setCellWidget(i, 1, item)

        elif "Spacing" in self.sender().text() and checked:
            self.grid_base = "spacing"
            item = QLabel("Spacing")
            item.setAlignment(Qt.AlignCenter)
            self.tableWidgetXGrid.setCellWidget(0, 1, item)
            firstCoord = 0
            for i in range(1, self.tableWidgetXGrid.rowCount()):
                old_value = self.tableWidgetXGrid.cellWidget(i, 1).value()
                print(old_value)
                new_value = old_value - firstCoord
                firstCoord = copy.deepcopy(old_value)
                item = QDoubleSpinBox()
                item.setAlignment(Qt.AlignCenter)

                if i == 1:
                    item.setRange(0, 10000)
                else:
                    item.setRange(1, 10000)
                    item.setDecimals(4)
                item.setValue(new_value)
                self.tableWidgetXGrid.setCellWidget(i, 1, item)

    def add_item(self, row_data=None):
        row = self.tableWidgetXGrid.rowCount()
        self.tableWidgetXGrid.insertRow(row)
        nameText = QTextEdit()
        if self.x_or_y == "x":
            nameText.setText(get_string_value(row))
        else:
            nameText.setText(str(row))
        spinBoxPos = QDoubleSpinBox()
        spinBoxPos.setDecimals(4)
        spinBoxPos.setRange(0, 1000000)
        spinBoxStart = QDoubleSpinBox()
        spinBoxStart.setDecimals(4)
        spinBoxStart.setRange(0, 1000000)
        spinBoxEnd = QDoubleSpinBox()
        spinBoxEnd.setDecimals(4)
        spinBoxEnd.setRange(0, 1000000)

        if row_data:  # if row_data is provided
            nameText.setPlainText(row_data['label'])
            try:
                spinBoxPos.setValue(row_data['position'])
            except:
                spinBoxPos.setValue(row_data['spacing'])
            spinBoxStart.setValue(row_data['start'])
            spinBoxEnd.setValue(row_data['end'])
        nameText.setAlignment(Qt.AlignCenter)
        spinBoxPos.setAlignment(Qt.AlignCenter)
        spinBoxStart.setAlignment(Qt.AlignCenter)
        spinBoxEnd.setAlignment(Qt.AlignCenter)
        self.tableWidgetXGrid.setCellWidget(row, 0, nameText)
        self.tableWidgetXGrid.setCellWidget(row, 1, spinBoxPos)
        self.tableWidgetXGrid.setCellWidget(row, 2, spinBoxStart)
        self.tableWidgetXGrid.setCellWidget(row, 3, spinBoxEnd)

    def delete_item(self):
        currentRow = self.tableWidgetXGrid.currentRow()
        if currentRow != 0:
            self.tableWidgetXGrid.removeRow(currentRow)

    def gridBase(self):
        if self.spacingButton.isChecked():
            self.grid_base = "spacing"
        else:
            self.grid_base = "coordinate"
        if self.gridData:
            if self.gridData[0].get("position"):
                self.grid_base = "coordinate"
            else:
                self.grid_base = "spacing"

    def update_data(self, grid_data, grid_base):
        # Clear existing rows
        while self.tableWidgetXGrid.rowCount() > 1:
            self.tableWidgetXGrid.removeRow(1)

        # Update grid base
        self.grid_base = grid_base
        item = QLabel(grid_base.capitalize())
        item.setAlignment(Qt.AlignCenter)
        self.tableWidgetXGrid.setCellWidget(0, 1, item)

        # Add new rows and set values
        for item in grid_data:
            self.add_item(item)

        # Update the row labels
        if self.x_or_y == "x":
            for i in range(1, self.tableWidgetXGrid.rowCount()):
                self.tableWidgetXGrid.cellWidget(i, 0).setText(get_string_value(i))
        else:
            for i in range(1, self.tableWidgetXGrid.rowCount()):
                self.tableWidgetXGrid.cellWidget(i, 0).setText(str(i))


class StoryDefine(QWidget):
    def __init__(self, coordinateButton, spacingButton, gridData=None):
        super(StoryDefine, self).__init__()
        self.coordinateButton = coordinateButton
        self.spacingButton = spacingButton
        self.gridData = gridData
        self.grid_base = None
        self.gridBase()
        if not self.grid_base:
            self.grid_base = "coordinate"
        self.finalLayout = QHBoxLayout()

        self.layout = QVBoxLayout(self)

        # Connect signals
        self.coordinateButton.toggled.connect(self.on_button_toggled)
        self.spacingButton.toggled.connect(self.on_button_toggled)
        self.buttonAdd = QPushButton("Add")
        self.buttonDelete = QPushButton("Delete")
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.addWidget(self.buttonAdd)
        self.buttons_layout.addWidget(self.buttonDelete)
        self.tableWidgetXGrid = QTableWidget(0, 2)
        self.tableWidgetXGrid.insertRow(0)
        storyLabel = QLabel("Story")
        storyLabel.setAlignment(Qt.AlignCenter)
        self.tableWidgetXGrid.setCellWidget(0, 0, storyLabel)
        heightLabel = QLabel(f"Height ({self.grid_base.capitalize()})")
        heightLabel.setAlignment(Qt.AlignCenter)
        self.tableWidgetXGrid.setCellWidget(0, 1, heightLabel)
        self.tableWidgetXGrid.setColumnWidth(1, 180)
        # self.tableWidgetXGrid.setCellWidget(0, 1, QTextEdit())
        self.layoutTable = QHBoxLayout()
        self.layoutTable.addWidget(self.tableWidgetXGrid)
        self.layoutTable.addLayout(self.buttons_layout)

        self.tableWidgetXGrid.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidgetXGrid.horizontalHeader().setVisible(False)  # hide column headers

        self.layout.addLayout(self.layoutTable)

        self.setLayout(self.layout)

        self.buttonAdd.clicked.connect(self.add_item)
        self.buttonDelete.clicked.connect(self.delete_item)
        if self.gridData:
            for row in self.gridData:
                self.add_item(row)
        self.row_values = []

    def on_button_toggled(self, checked):
        if "Coordinate" in self.sender().text() and checked:
            item = QLabel("Height (Coordinate)")
            item.setAlignment(Qt.AlignCenter)
            self.tableWidgetXGrid.setCellWidget(0, 1, item)
            self.grid_base = "coordinate"
            firstCoord = 0
            print("self.tableWidgetXGrid.rowCount()", self.tableWidgetXGrid.rowCount())
            for i in range(1, self.tableWidgetXGrid.rowCount()):
                old_value = self.tableWidgetXGrid.cellWidget(i, 1).value()
                new_value = firstCoord + old_value
                firstCoord = copy.deepcopy(new_value)
                item = QDoubleSpinBox()
                item.setAlignment(Qt.AlignCenter)
                item.setRange(1, 10000)
                item.setDecimals(4)
                item.setValue(new_value)
                self.tableWidgetXGrid.setCellWidget(i, 1, item)

        elif "Spacing" in self.sender().text() and checked:
            self.grid_base = "spacing"
            item = QLabel("Height (Spacing)")
            item.setAlignment(Qt.AlignCenter)
            self.tableWidgetXGrid.setCellWidget(0, 1, item)
            firstCoord = 0
            for i in range(1, self.tableWidgetXGrid.rowCount()):
                old_value = self.tableWidgetXGrid.cellWidget(i, 1).value()
                print(old_value)
                new_value = old_value - firstCoord
                firstCoord = copy.deepcopy(old_value)
                item = QDoubleSpinBox()
                item.setAlignment(Qt.AlignCenter)
                if i == 1:
                    item.setRange(0, 10000)
                else:
                    item.setRange(1, 10000)
                    item.setDecimals(4)
                item.setValue(new_value)
                self.tableWidgetXGrid.setCellWidget(i, 1, item)

    def add_item(self, row_data=None):
        row = self.tableWidgetXGrid.rowCount()
        self.tableWidgetXGrid.insertRow(row)
        nameText = QLabel()
        nameText.setAlignment(Qt.AlignCenter)
        nameText.setText(str(row))
        spinBoxPos = QDoubleSpinBox()
        spinBoxPos.setAlignment(Qt.AlignCenter)
        spinBoxPos.setDecimals(4)
        spinBoxPos.setRange(0, 1000000)

        if row_data:  # if row_data is provided
            nameText.setText(row_data['label'])

            try:
                spinBoxPos.setValue(row_data['position'])
            except:
                spinBoxPos.setValue(row_data['spacing'])
        self.tableWidgetXGrid.setCellWidget(row, 0, nameText)
        self.tableWidgetXGrid.setCellWidget(row, 1, spinBoxPos)

    def delete_item(self):
        currentRow = self.tableWidgetXGrid.currentRow()
        if currentRow != 0:
            self.tableWidgetXGrid.removeRow(currentRow)
        row = self.tableWidgetXGrid.rowCount()
        for i in range(1, row):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)
            self.tableWidgetXGrid.setCellWidget(i, 0, label)

    def gridBase(self):
        if self.spacingButton.isChecked():
            self.grid_base = "spacing"
        else:
            self.grid_base = "coordinate"
        if self.gridData:
            if self.gridData[0].get("position"):
                self.grid_base = "coordinate"
            else:
                self.grid_base = "spacing"

    def update_data(self, story_number, story_height, gridBase):
        # Clear existing rows
        while self.tableWidgetXGrid.rowCount() > 1:
            self.tableWidgetXGrid.removeRow(1)

        # Add new rows
        for i in range(story_number):
            self.add_item()

        # Set values
        total_height = 0
        for i, height in enumerate(story_height, start=1):
            if gridBase == "coordinate":
                total_height += height
                self.tableWidgetXGrid.cellWidget(i, 1).setValue(total_height)
            else:
                self.tableWidgetXGrid.cellWidget(i, 1).setValue(height)


class StoryCoordinateDefine(QWidget):
    def __init__(self, storyProp=None, gridBase=None):
        super(StoryCoordinateDefine, self).__init__()
        self.gridBase = gridBase
        self.finalLayout = QHBoxLayout()
        self.layout = QVBoxLayout(self)
        self.coordinateButton = QRadioButton("Display Story Height as Coordinate")
        self.spacingButton = QRadioButton("Display Story Height as Spacing")
        self.layoutBase = QHBoxLayout()
        self.layoutBase.addWidget(self.coordinateButton)
        self.layoutBase.addWidget(self.spacingButton)
        storyLabel = QLabel("Story Properties")
        self.storyData = StoryDefine(self.coordinateButton, self.spacingButton, storyProp)
        self.layout.addWidget(storyLabel)
        self.layout.addLayout(self.layoutBase)
        self.layout.addWidget(self.storyData)

    def output(self):
        if self.coordinateButton.isChecked():
            self.gridBase = "coordinate"
        else:
            self.gridBase = "spacing"

        if self.storyData.tableWidgetXGrid.rowCount() < 2:  # make default grid
            storyNumber = 1
            storyHeight = [10]
        else:
            storyNumber = self.storyData.tableWidgetXGrid.rowCount() - 1
            storyHeight = []
            start = 0
            for i in range(1, self.storyData.tableWidgetXGrid.rowCount()):
                if self.gridBase == "coordinate":
                    currentCoord = self.storyData.tableWidgetXGrid.cellWidget(i, 1).value()
                    storyHeight.append(currentCoord - start)
                    start = copy.deepcopy(currentCoord)
                else:
                    storyHeight.append(self.storyData.tableWidgetXGrid.cellWidget(i, 1).value())
        return storyNumber, storyHeight

    def update_data(self, story_number, story_height, gridBase):
        # Update the radio buttons
        self.coordinateButton.setChecked(gridBase == "coordinate")
        self.spacingButton.setChecked(gridBase == "spacing")

        # Update the story data
        self.storyData.update_data(story_number, story_height, gridBase)


class GridCoordinateDefine(QWidget):
    def __init__(self, xGrid=None, yGrid=None, gridBase=None):
        super(GridCoordinateDefine, self).__init__()
        self.gridBase = gridBase
        self.layout = QVBoxLayout(self)
        self.coordinateButton = QRadioButton("Display Grid Data as Coordinate")
        self.spacingButton = QRadioButton("Display Grid Data as Spacing")
        self.layoutBase = QHBoxLayout()
        self.layoutBase.addWidget(self.coordinateButton)
        self.layoutBase.addWidget(self.spacingButton)
        xGridLabel = QLabel("X Grid")
        yGridLabel = QLabel("Y Grid")
        xGridLayout = QVBoxLayout()
        yGridLayout = QVBoxLayout()
        xGridLayout.addWidget(xGridLabel)
        yGridLayout.addWidget(yGridLabel)
        self.xGrids = GridLineDefine(self.coordinateButton, self.spacingButton, "x", xGrid)
        xGridLayout.addWidget(self.xGrids)
        self.yGrids = GridLineDefine(self.coordinateButton, self.spacingButton, "y", yGrid)
        yGridLayout.addWidget(self.yGrids)
        gridsLayouts = QHBoxLayout()
        gridsLayouts.addLayout(xGridLayout)
        gridsLayouts.addLayout(yGridLayout)

        self.layout.addLayout(self.layoutBase)
        self.layout.addLayout(gridsLayouts)

    def output(self):
        if self.coordinateButton.isChecked():
            self.gridBase = "coordinate"
            posOrSpace = "position"
        else:
            self.gridBase = "spacing"
            posOrSpace = "spacing"

        xGrid = []
        if self.xGrids.tableWidgetXGrid.rowCount() < 3:  # make default grid
            xGrid = [{"label": "A", f"{posOrSpace}": 0, "start": 0, "end": 0},
                     {"label": "B", f"{posOrSpace}": 10, "start": 0, "end": 0}]
        else:
            for i in range(1, self.xGrids.tableWidgetXGrid.rowCount()):
                xGrid.append({
                    "label": self.xGrids.tableWidgetXGrid.cellWidget(i, 0).toPlainText(),
                    f"{posOrSpace}": self.xGrids.tableWidgetXGrid.cellWidget(i, 1).value(),
                    "start": self.xGrids.tableWidgetXGrid.cellWidget(i, 2).value(),
                    "end": self.xGrids.tableWidgetXGrid.cellWidget(i, 3).value()
                })

        yGrid = []
        if self.yGrids.tableWidgetXGrid.rowCount() < 3:  # make default grid
            yGrid = [{"label": "1", f"{posOrSpace}": 0, "start": 0, "end": 0},
                     {"label": "2", f"{posOrSpace}": 10, "start": 0, "end": 0}]

        else:
            for i in range(1, self.yGrids.tableWidgetXGrid.rowCount()):
                yGrid.append({
                    "label": self.yGrids.tableWidgetXGrid.cellWidget(i, 0).toPlainText(),
                    f"{posOrSpace}": self.yGrids.tableWidgetXGrid.cellWidget(i, 1).value(),
                    "start": self.yGrids.tableWidgetXGrid.cellWidget(i, 2).value(),
                    "end": self.yGrids.tableWidgetXGrid.cellWidget(i, 3).value()
                })

        # check sort
        if self.gridBase == "coordinate":
            xGrid = self.sortCoordinate(xGrid)
            yGrid = self.sortCoordinate(yGrid)
        return xGrid, yGrid, self.gridBase

    @staticmethod
    def sortCoordinate(grid):
        sortedGrid = []
        baseNumber = -float("inf")
        for data in grid:
            if data["position"] >= baseNumber:
                baseNumber = data["position"]
                sortedGrid.append(data)
            else:
                for i in range(len(sortedGrid)):
                    if data["position"] < sortedGrid[i]["position"]:
                        sortedGrid.insert(i, data)
                        break

        return sortedGrid

    def update_data(self, x_grid, y_grid, grid_base):
        self.gridBase = grid_base
        self.coordinateButton.setChecked(grid_base == "coordinate")
        self.spacingButton.setChecked(grid_base == "spacing")

        self.xGrids.update_data(x_grid, grid_base)
        self.yGrids.update_data(y_grid, grid_base)


class GridPreview(QGraphicsView):
    def __init__(self, gridData):
        super(GridPreview, self).__init__()
        self.gridData = gridData
        self.x_grid, self.y_grid, self.grid_base = None, None, None
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

    def preview(self):
        self.scene.clear()
        self.x_grid, self.y_grid, self.grid_base = self.gridData.output()

        line = LineDrawHandler(self.x_grid, self.y_grid, self.scene, "", "", self.grid_base)
        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)


def get_string_value(num):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = ''
    while num > 0:
        num, remainder = divmod(num - 1, 26)
        result = alphabet[remainder] + result
    return result
