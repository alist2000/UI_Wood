from PySide6.QtWidgets import QMainWindow, QApplication, QToolBar, QStatusBar, QVBoxLayout, QWidget, QDialog, QLabel, \
    QSpinBox, QDialogButtonBox, QListWidget, QListWidgetItem, QPushButton, QTextEdit, QTableWidgetItem
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QSpinBox, QDialogButtonBox
from PySide6.QtWidgets import QTabWidget, QDialog, QDialogButtonBox, \
    QLabel, QWidget, QVBoxLayout, QPushButton, QComboBox, QDoubleSpinBox, QHBoxLayout, \
    QTableWidget, QAbstractItemView, QCheckBox

from path import PathHandler
from UI_Wood.stableVersion5.styles import TabWidgetStyle

import uuid


class set_uniform_load(QDialog):
    def __init__(self, mainPage):
        super(set_uniform_load, self).__init__()
        self.EditLoadMapLoadSet = None
        self.loadSetId = uuid.uuid4()
        self.set_uniforms = None
        self.load_data = {"id": self.loadSetId, "name": "", "properties": [], "Reducible": True}
        self.all_set_load = {}
        self.all_set_load2 = {}
        self.mainPage = mainPage

        self.setWindowTitle("Set Uniform Load")
        # Create buttons
        self.addButton = QPushButton("Add")
        self.addButton.clicked.connect(self.open_add_dialog)
        self.deleteButton = QPushButton("Delete")
        self.deleteButton.clicked.connect(self.delete_row)
        self.modifyButton = QPushButton("Modify")
        self.modifyButton.clicked.connect(self.modify_row)

        # Create a list widget
        self.listWidget = QListWidget()

        # Layout the dialog
        layout = QVBoxLayout()
        layout.addWidget(self.addButton)
        layout.addWidget(self.deleteButton)
        layout.addWidget(self.modifyButton)
        layout.addWidget(self.listWidget)
        self.setStyleSheet(TabWidgetStyle)
        self.setLayout(layout)

    def open_add_dialog(self):
        self.EditLoadMapLoadSet = EditLoadMapLoadSet(self.mainPage.mainPage.grid)

        dialog = UniformLoadDialog(self.load_data)
        dialog.button_box.accepted.connect(dialog.accept_control)  # Change from dialog.accept to self.accept
        dialog.button_box.rejected.connect(dialog.reject_control)  # Change from dialog.accept to self.accept
        deadSuperExist = False
        if dialog.exec() == QDialog.Accepted:
            self.loadSetId = uuid.uuid4()
            name = self.load_data["name"]
            for i in self.all_set_load.keys():
                if name == i:
                    self.load_data["name"] = name + " "

            self.all_set_load[str(self.loadSetId)] = {self.load_data["name"]: self.load_data["properties"]}
            self.all_set_load2[str(self.loadSetId)] = {self.load_data["name"]: self.load_data["Reducible"]}
            for load in self.load_data["properties"]:
                loadType = load["type"]
                if loadType == "Dead Super":
                    deadSuperExist = True

            # Add a new row to the list widget if OK was clicked
            item = QListWidgetItem(self.load_data["name"])
            if not deadSuperExist:
                item.setIcon(QIcon(PathHandler("images/warning.png")))
                item.setToolTip(
                    "<html><body<h1 >Warning!</h1>"
                    "Super Dead is not defined.<ul><li>Please enter 'super dead' loads for all load sets, Or the seismic analysis will not be carried out.</li><li>In set dead loads are defined"
                    "but super dead loads are left empty, They will be assumed 10 psf greater than dead loads.</li></ul></body></html>")
            self.listWidget.addItem(item)
            self.EditLoadMapLoadSet.edit(self.all_set_load)
            # self.EditLoadMapLoadSet.edit(self.all_set_load2)

    def delete_row(self):
        # Delete the selected row
        for item in self.listWidget.selectedItems():
            name = item.text()
            for keys, items in self.all_set_load.items():
                nameItem = list(items.keys())[0]
                if nameItem == name:
                    self.all_set_load.pop(keys)
                    self.all_set_load2.pop(keys)
                    self.listWidget.takeItem(self.listWidget.row(item))
                    break

    def modify_row(self):
        self.EditLoadMapLoadSet = EditLoadMapLoadSet(self.mainPage.mainPage.grid)
        deadSuperExist = False
        # Open the add dialog with the values of the selected row
        for item in self.listWidget.selectedItems():
            name = item.text()
            mainId = "0"
            for keys, items in self.all_set_load.items():
                nameItem = list(items.keys())[0]
                if nameItem == name:
                    load_data = list(self.all_set_load[keys].values())[0]
                    reducible = list(self.all_set_load2[keys].values())[0]
                    load_data_dict = {"name": name, "properties": load_data, "Reducible": reducible}
                    dialog = UniformLoadDialog(load_data_dict)
                    dialog.button_box.accepted.connect(
                        dialog.accept_control)  # Change from dialog.accept to self.accept
                    mainId = keys
                    break

            if dialog.exec() == QDialog.Accepted:
                self.all_set_load.pop(mainId)
                self.all_set_load2.pop(mainId)

                name = dialog.uniform_load.load_data["name"]
                for i in self.all_set_load.keys():
                    if name == i:
                        dialog.uniform_load.load_data["name"] = name + " "

                self.all_set_load[mainId] = {
                    dialog.uniform_load.load_data["name"]: dialog.uniform_load.load_data["properties"]}
                self.all_set_load2[mainId] = {
                    dialog.uniform_load.load_data["name"]: dialog.uniform_load.load_data["Reducible"]}

                # Delete
                self.listWidget.takeItem(self.listWidget.row(item))

                for load in dialog.uniform_load.load_data["properties"]:
                    loadType = load["type"]
                    if loadType == "Dead Super":
                        deadSuperExist = True

                # Add a new row to the list widget if OK was clicked
                item = QListWidgetItem(dialog.uniform_load.load_data["name"])
                if not deadSuperExist:
                    item.setIcon(QIcon(PathHandler("images/warning.png")))
                    item.setToolTip(
                        "<html><body><h1>Warning!</h1>Super Dead is not defined.<li>Please enter 'super dead' loads for all load sets, Or the seismic analysis will not be carried out.</li><li>In set dead loads are defined"
                        "but super dead loads are left empty, They will be assumed 10 psf greater than dead loads.</li></body></html>")

                self.listWidget.addItem(item)
                self.load_data = dialog.uniform_load.load_data
                self.EditLoadMapLoadSet.edit(self.all_set_load)
                # self.EditLoadMapLoadSet.edit(self.all_set_load2)

    # SLOT
    def uniform_load_exe(self):
        self.exec()


class UniformLoadDialog(QDialog):
    def __init__(self, loadData):
        super(UniformLoadDialog, self).__init__()

        self.setWindowTitle("Set Uniform Load")
        self.button_box = button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.uniform_load = UniformLoad(loadData)
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.uniform_load)
        v_layout.addWidget(self.button_box)
        self.setStyleSheet(TabWidgetStyle)
        self.setLayout(v_layout)

    # SLOT
    def accept_control(self):
        self.uniform_load.print_values()
        self.accept()

    def reject_control(self):
        print("reject")
        self.reject()


class UniformLoad(QWidget):
    def __init__(self, load_data):
        super().__init__()
        self.load_data = load_data
        # tab_widget.addTab(self, f"Load")
        self.layout = QVBoxLayout(self)

        self.buttonAdd = QPushButton("Add")
        self.buttonDelete = QPushButton("Delete")
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.buttonAdd)
        self.buttons_layout.addWidget(self.buttonDelete)
        self.tableWidget = QTableWidget(0, 2)
        self.tableWidget.insertRow(0)
        self.tableWidget.setCellWidget(0, 0, QLabel("Name"))
        self.tableWidget.setCellWidget(0, 1, QTextEdit())
        self.tableWidget.insertRow(1)
        self.tableWidget.setCellWidget(1, 0, QLabel("Reducible Live?"))
        self.combo = QComboBox()
        self.combo.addItems(["Yes", "No"])
        self.tableWidget.setCellWidget(1, 1, self.combo)

        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.horizontalHeader().setVisible(False)  # hide column headers

        self.layout.addLayout(self.buttons_layout)
        self.layout.addWidget(self.tableWidget)

        self.setLayout(self.layout)

        self.buttonAdd.clicked.connect(self.add_item)
        self.buttonDelete.clicked.connect(self.delete_item)
        self.row_values = []

        self.populate_table()

    def populate_table(self):
        print(self.load_data)
        for i, row_data in enumerate(self.load_data["properties"]):
            loadName = self.load_data["name"]
            reducible = self.load_data["Reducible"]
            self.add_item(loadName, reducible, row_data, i)

    def add_item(self, name=None, reducible=None, row_data=None, i=0):
        print("row data", row_data)
        row = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row)

        comboBox = QComboBox()
        comboBox.addItem("Dead")
        comboBox.addItem("Live")
        comboBox.addItem("Dead Super")
        comboBox.addItem("Live Roof")
        comboBox.addItem("Snow")
        comboBox.setStyleSheet("""
                            QComboBox {
                                border: 1px solid gray;
                                margin: 2px;
                                padding: 1px;
                            }
                            QComboBox::down-arrow, QComboBox::drop-down {
                                border-radius: 5px;  # add this line
                            }
                        """)

        spinBox = QDoubleSpinBox()
        spinBox.setDecimals(4)
        spinBox.setRange(0, 1000000)

        if row_data:  # if row_data is provided
            if i == 0:
                self.tableWidget.setCellWidget(0, 0, QLabel("Name"))
                self.tableWidget.setCellWidget(0, 1, QTextEdit(name))
                # self.tableWidget.setCellWidget(1, 0, QLabel("Reducible Live?"))
                # combo = QComboBox()
                if reducible is True:
                    name1 = "Yes"
                    name2 = "No"
                else:
                    name1 = "No"
                    name2 = "Yes"
                self.combo.setCurrentText(name1)
                # combo.addItems([name2, name1])
                # combo.setCurrentText(name1)
                # self.tableWidget.setCellWidget(1
                #                                , 1, combo)
            comboBox.setCurrentText(row_data['type'])
            spinBox.setValue(row_data['magnitude'])

        self.tableWidget.setCellWidget(row, 0, comboBox)
        self.tableWidget.setCellWidget(row, 1, spinBox)

    def delete_item(self):
        currentRow = self.tableWidget.currentRow()
        if currentRow != 0 and currentRow != 1:
            self.tableWidget.removeRow(currentRow)

    def print_values(self):
        self.load_data.clear()  # clear the old values

        self.load_data["name"] = self.tableWidget.cellWidget(0, 1).toPlainText()
        reducible = self.tableWidget.cellWidget(1, 1).currentText()
        if reducible == "Yes":
            reducible = True
        else:
            reducible = False
        self.load_data["Reducible"] = reducible
        self.load_data["properties"] = []
        for row in range(2, self.tableWidget.rowCount()):
            comboBox = self.tableWidget.cellWidget(row, 0)
            spinBox = self.tableWidget.cellWidget(row, 1)
            loadType = comboBox.currentText()
            self.load_data["properties"].append({
                'type': loadType,
                'magnitude': spinBox.value()
            })
            print(f"Row {row + 1}: Combo box value: {comboBox.currentText()}, Spin box value: {spinBox.value()}")


class EditLoadMapLoadSet:
    def __init__(self, grid):
        loadMaps = []
        for items in grid:
            loads = items.load_instance
            loadMaps.append(list(loads.rect_prop.values()))
            # for load in loads["rect_prop"].values():
            #     loadID = load["id"]
            # loadMaps.append(items[])

        self.loadMaps = loadMaps

    def edit(self, loadSets):
        print("LOAD SET IN EDIT FUNCTION", loadSets)
        for loads in self.loadMaps:
            for load in loads:
                loadID = load["id"]
                if not loadID:
                    loadID = list(loadSets.keys())[0]
                loadSetTarget = loadSets[loadID]
                loadSetEdited = self.EditLoadSet(loadSetTarget)
                load["load"] = loadSetEdited
                load["label"] = list(loadSetTarget.keys())[0]

                # ADD ALL LOAD SET NAMES FOR PROPERTIES.
                load["load_set"] = [list(loadSet.keys())[0] for loadSet in loadSets.values()]

    # EDIT LOAD SET
    @staticmethod
    def EditLoadSet(loadSet):
        newLoadSet = list(loadSet.values())[0]
        print(newLoadSet)
        return newLoadSet
