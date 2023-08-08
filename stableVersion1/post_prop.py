from PySide6.QtWidgets import QTabWidget, QDialog, QDialogButtonBox, \
    QLabel, QWidget, QVBoxLayout, QPushButton, QComboBox, QDoubleSpinBox, QHBoxLayout, \
    QTableWidget, QAbstractItemView

# from post_new import magnification_factor
magnification_factor = 40


class PostProperties(QDialog):
    def __init__(self, rectItem, post_properties, parent=None):
        super().__init__(parent)
        self.rect = rectItem
        self.post_prop = post_properties
        self.setWindowTitle("Post Properties")
        self.setMinimumSize(200, 400)
        self.wallWidth = None
        self.wallWidth_default = post_properties[rectItem]["wall_width"]
        self.button_box = button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept_control)  # Change from dialog.accept to self.accept
        self.button_box.rejected.connect(self.reject)  # Change from dialog.reject to self.reject

        v_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setWindowTitle("Object Data")
        self.create_geometry_tab()
        self.create_assignment_tab()
        self.pointLoad = pointLoad(self.tab_widget, self.post_prop[self.rect])

        v_layout.addWidget(self.tab_widget)
        v_layout.addWidget(button_box)
        self.setLayout(v_layout)  # Change from dialog.setLayout to self.setLayout

    # Rest of the code remains the same

    # dialog.show()

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
        x = QLabel(f"{position[0] / magnification_factor}")
        label2 = QLabel("Global Y")
        y = QLabel(f"{position[1] / magnification_factor}")

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
    def accept_control(self):
        self.pointLoad.print_values()
        self.accept()

    def create_assignment_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, f"Assignments")
        label1 = QLabel("Wall Width")
        self.wallWidth = wallWidth = QComboBox()
        wallWidth.addItems(["6 in", "4 in"])
        self.wallWidth.setCurrentText(self.post_prop[self.rect]["wall_width"])
        self.button_box.accepted.connect(self.accept_control)  # Change from dialog.accept to self.accept
        self.button_box.rejected.connect(self.reject)  # Change from dialog.reject to self.reject
        self.wallWidth.currentTextChanged.connect(self.wall_width_control)

        # LAYOUT
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(label1)
        h_layout1.addWidget(wallWidth)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout1)

        tab.setLayout(v_layout)
        # return self.direction

        # SLOT

    def wall_width_control(self):
        self.thickness_default = self.wallWidth.currentText()
        self.post_prop[self.rect]["wall_width"] = self.thickness_default


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
