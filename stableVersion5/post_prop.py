from PySide6.QtWidgets import (QTabWidget, QDialog, QDialogButtonBox, QLabel, QWidget,
                               QVBoxLayout, QPushButton, QComboBox, QDoubleSpinBox,
                               QHBoxLayout, QTableWidget, QAbstractItemView, QCheckBox,
                               QToolTip)
from PySide6.QtGui import QPen, QBrush, QColor, QIcon
from PySide6.QtCore import Qt

magnification_factor = 40


class PostProperties(QDialog):
    def __init__(self, rectItem, post_properties, timer, parent=None):
        super().__init__(parent)
        self.timer = timer
        self.rect = rectItem
        self.post_prop = post_properties
        self.setWindowTitle("Post Properties")
        self.setMinimumSize(200, 400)
        self.wallWidth = None
        self.wallWidth_default = post_properties[rectItem]["wall_width"]
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept_control)
        self.button_box.rejected.connect(self.reject_control)

        v_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setWindowTitle("Object Data")
        self.create_geometry_tab()
        self.create_assignment_tab()
        self.pointLoad = pointLoad(self.tab_widget, self.post_prop[self.rect])

        v_layout.addWidget(self.tab_widget)
        v_layout.addWidget(self.button_box)
        self.setLayout(v_layout)

    def create_geometry_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, f"Geometry")

        # Label
        print(self.post_prop)
        Post_label = self.post_prop[self.rect]["label"]
        label = QLabel("Post Label")
        post_label = QLabel(Post_label)

        # coordinate
        position = self.post_prop[self.rect]["coordinate"]
        label1 = QLabel("Global X")
        x = QLabel(f"{round(position[0] / magnification_factor, 2)}")
        label2 = QLabel("Global Y")
        y = QLabel(f"{round(position[1] / magnification_factor, 2)}")

        # label3 = QLabel("Post Exist")

        # control post existence
        # if self.position in self.Post_position_list:
        #     post_exist = QLabel("Yes")
        #     label = QLabel("Post Label")
        #     post_label = QLabel(list(self.post_label)[list(self.Post_position_list).index(self.position)])
        #     # post_label = QLabel(f"P{list(self.Post_position_list).index(self.position) + 1}")
        # else:
        #     post_exist = QLabel("No")
        #     label = QLabel("Post Label")
        #     post_label = QLabel("-")

        # LAYOUT
        h_layout0 = QHBoxLayout()
        h_layout0.addWidget(label)
        h_layout0.addWidget(post_label)
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(label1)
        h_layout1.addWidget(x)
        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(label2)
        h_layout2.addWidget(y)
        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout0)
        v_layout.addLayout(h_layout1)
        v_layout.addLayout(h_layout2)
        tab.setLayout(v_layout)

    # SLOT
    def create_assignment_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, "Assignments")

        v_layout = QVBoxLayout()

        # Wall Width
        wall_width_group = QWidget()
        h_layout1 = QHBoxLayout(wall_width_group)
        label1 = QLabel("Wall Width")
        self.wallWidth = QComboBox()
        self.wallWidth.addItems(["6 in", "4 in"])
        self.wallWidth.setCurrentText(self.post_prop[self.rect]["wall_width"])
        self.wallWidth.currentTextChanged.connect(self.wall_width_control)
        h_layout1.addWidget(label1)
        h_layout1.addWidget(self.wallWidth)
        v_layout.addWidget(wall_width_group)

        v_layout.addSpacing(20)  # Add some vertical spacing

        # Load Transfer
        load_transfer_group = QWidget()
        h_layout2 = QHBoxLayout(load_transfer_group)
        self.load_transfer_checkbox = QCheckBox("Enable Load Transfer")
        self.load_transfer_checkbox.setChecked(self.post_prop[self.rect].get("load_transfer", True))
        self.load_transfer_checkbox.stateChanged.connect(self.load_transfer_control)

        info_icon = QPushButton(icon=QIcon.fromTheme("dialog-information"))
        info_icon.setFixedSize(20, 20)
        info_icon.setToolTip("When enabled, this post will transfer loads from top to bottom. "
                             "When disabled, the post acts only as support without transferring loads.")
        info_icon.setStyleSheet("QPushButton { border: none; }")

        h_layout2.addWidget(self.load_transfer_checkbox)
        h_layout2.addWidget(info_icon)
        h_layout2.addStretch(1)  # This pushes the checkbox and icon to the left
        v_layout.addWidget(load_transfer_group)

        tab.setLayout(v_layout)

    def wall_width_control(self):
        self.thickness_default = self.wallWidth.currentText()
        self.post_prop[self.rect]["wall_width"] = self.thickness_default

    def load_transfer_control(self, state):
        self.post_prop[self.rect]["load_transfer"] = bool(state)

    def accept_control(self):
        self.pointLoad.print_values()
        self.accept()
        self.timer.stop()
        self.rect.setBrush(QBrush(QColor("#E76161"), Qt.SolidPattern))

    def reject_control(self):
        self.reject()
        self.timer.stop()
        self.rect.setBrush(QBrush(QColor("#E76161"), Qt.SolidPattern))

    def closeEvent(self, event):
        self.timer.stop()
        self.rect.setBrush(QBrush(QColor("#E76161"), Qt.SolidPattern))
        super().closeEvent(event)


class pointLoad(QWidget):
    def __init__(self, tab_widget, itemProp):
        super().__init__()
        self.itemProp = itemProp
        self.load_data = itemProp["load"]["point"]
        tab_widget.addTab(self, f"Point Load")
        self.distance = None

        # if self.itemProp["direction"] == "N-S":
        #     self.range_line = abs(self.itemProp["coordinate"][1][1] - self.itemProp["coordinate"][0][1])
        # else:
        #     self.range_line = abs(self.itemProp["coordinate"][1][0] - self.itemProp["coordinate"][0][0])

        self.layout = QVBoxLayout(self)
        self.buttons_layout = QHBoxLayout()

        self.buttonAdd = QPushButton("Add")
        self.buttonDelete = QPushButton("Delete")
        self.buttons_layout.addWidget(self.buttonAdd)
        self.buttons_layout.addWidget(self.buttonDelete)

        self.header_layout = QHBoxLayout(self)
        load_type = QLabel("Load Type")
        mag = QLabel("Magnitude")
        self.header_layout.addWidget(load_type, 1)
        self.header_layout.addWidget(mag, 1)

        # self.x_y_layout = QVBoxLayout(self)
        # x = QLabel("X")
        # y = QLabel("Y")
        # self.x_y_layout.addWidget(x)
        # self.x_y_layout.addWidget(y)
        self.tableWidget = QTableWidget(0, 2)
        # self.table_layout1.addWidget(x, self.tableWidget1)

        # self.table_layout2 = QHBoxLayout(self)
        # self.tableWidget2 = QTableWidget(0, 2)
        # self.table_layout2.addWidget(y, self.tableWidget2)

        # self.table_layout_vert = QVBoxLayout()
        # self.table_layout_vert.addLayout(self.table_layout1)
        # self.table_layout_vert.addLayout(self.table_layout2)

        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.horizontalHeader().setVisible(False)  # hide column headers

        self.layout.addLayout(self.buttons_layout)
        self.layout.addLayout(self.header_layout)
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
        for row_data in self.load_data:
            self.add_item(row_data)

    def add_item(self, row_data=None):
        print("row data", row_data)
        row = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row)

        comboBox = QComboBox()
        comboBox.addItem("Dead")
        comboBox.addItem("Live")
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
            comboBox.setCurrentText(row_data['type'])
            spinBox.setValue(row_data['magnitude'])

        self.tableWidget.setCellWidget(row, 0, comboBox)
        self.tableWidget.setCellWidget(row, 1, spinBox)

    def delete_item(self):
        currentRow = self.tableWidget.currentRow()
        self.tableWidget.removeRow(currentRow)

    def print_values(self):
        self.load_data.clear()  # clear the old values
        for row in range(self.tableWidget.rowCount()):
            comboBox = self.tableWidget.cellWidget(row, 0)
            spinBox = self.tableWidget.cellWidget(row, 1)
            self.load_data.append({
                'type': comboBox.currentText(),
                'magnitude': spinBox.value()
            })
            print(f"Row {row + 1}: Combo box value: {comboBox.currentText()}, Spin box value: {spinBox.value()}")
