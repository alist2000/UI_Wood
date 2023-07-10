from joist_prop import JoistLoad
from PySide6.QtWidgets import QMainWindow, QApplication, QToolBar, QStatusBar, QVBoxLayout, QWidget, QDialog, QLabel, \
    QSpinBox, QDialogButtonBox, QListWidget, QListWidgetItem, QPushButton, QTextEdit
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QSpinBox, QDialogButtonBox
from PySide6.QtWidgets import QTabWidget, QDialog, QDialogButtonBox, \
    QLabel, QWidget, QVBoxLayout, QPushButton, QComboBox, QDoubleSpinBox, QHBoxLayout, \
    QTableWidget, QAbstractItemView, QCheckBox

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QColor


class set_uniform_load(QDialog):
    def __init__(self, mainPage):
        super(set_uniform_load, self).__init__()
        self.set_uniforms = None
        self.load_data = {"name": "", "properties": []}
        self.all_set_load = {}

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
        self.setLayout(layout)

    def open_add_dialog(self):

        dialog = UniformLoadDialog(self.load_data)
        dialog.button_box.accepted.connect(dialog.accept_control)  # Change from dialog.accept to self.accept

        if dialog.exec() == QDialog.Accepted:
            name = self.load_data["name"]
            for i in self.all_set_load.keys():
                if name == i:
                    self.load_data["name"] = name + " "

            self.all_set_load[self.load_data["name"]] = self.load_data["properties"]
            # Add a new row to the list widget if OK was clicked
            item = QListWidgetItem(self.load_data["name"])
            self.listWidget.addItem(item)

    def delete_row(self):
        # Delete the selected row
        for item in self.listWidget.selectedItems():
            name = item.text()
            self.all_set_load.pop(name)
            self.listWidget.takeItem(self.listWidget.row(item))


    def modify_row(self):
        # Open the add dialog with the values of the selected row
        for item in self.listWidget.selectedItems():
            name = item.text()
            load_data = self.all_set_load[name]
            load_data_dict = {"name": name, "properties": load_data}
            dialog = UniformLoadDialog(load_data_dict)
            dialog.button_box.accepted.connect(dialog.accept_control)  # Change from dialog.accept to self.accept

            if dialog.exec() == QDialog.Accepted:
                self.all_set_load.pop(name)

                name = dialog.uniform_load.load_data["name"]
                for i in self.all_set_load.keys():
                    if name == i:
                        dialog.uniform_load.load_data["name"] = name + " "

                self.all_set_load[dialog.uniform_load.load_data["name"]] = dialog.uniform_load.load_data["properties"]

                # Delete
                self.listWidget.takeItem(self.listWidget.row(item))

                # Create a new one
                item = QListWidgetItem(dialog.uniform_load.load_data["name"])
                self.listWidget.addItem(item)

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
        self.setLayout(v_layout)

    # SLOT
    def accept_control(self):
        self.uniform_load.print_values()
        self.accept()


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

        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.horizontalHeader().setVisible(False)  # hide column headers

        self.layout.addLayout(self.buttons_layout)
        self.layout.addWidget(self.tableWidget)

        self.setLayout(self.layout)

        self.buttonAdd.clicked.connect(self.add_item)
        self.buttonDelete.clicked.connect(self.delete_item)
        self.row_values = []

        # self.buttonOK = QPushButton("OK")
        # self.layout.addWidget(self.buttonOK)

        # self.buttonOK.clicked.connect(self.print_values)

        self.populate_table()

    def populate_table(self):
        print("jslkjfja", self.load_data["properties"])
        print(self.load_data)
        for i, row_data in enumerate(self.load_data["properties"]):
            loadName = self.load_data["name"]
            # print(loadName)
            self.add_item(loadName, row_data, i)

    def add_item(self, name=None, row_data=None, i=0):
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
        spinBox.setRange(0, 1000000)

        if row_data:  # if row_data is provided
            if i == 0:
                self.tableWidget.setCellWidget(0, 0, QLabel("Name"))
                self.tableWidget.setCellWidget(0, 1, QTextEdit(name))
            comboBox.setCurrentText(row_data['type'])
            spinBox.setValue(row_data['magnitude'])

        self.tableWidget.setCellWidget(row, 0, comboBox)
        self.tableWidget.setCellWidget(row, 1, spinBox)

    def delete_item(self):
        currentRow = self.tableWidget.currentRow()
        if currentRow != 0:
            self.tableWidget.removeRow(currentRow)

    def print_values(self):
        self.load_data.clear()  # clear the old values

        self.load_data["name"] = self.tableWidget.cellWidget(0, 1).toPlainText()
        self.load_data["properties"] = []
        for row in range(1, self.tableWidget.rowCount()):
            comboBox = self.tableWidget.cellWidget(row, 0)
            spinBox = self.tableWidget.cellWidget(row, 1)
            self.load_data["properties"].append({
                'type': comboBox.currentText(),
                'magnitude': spinBox.value()
            })
            print(f"Row {row + 1}: Combo box value: {comboBox.currentText()}, Spin box value: {spinBox.value()}")
