from PySide6.QtWidgets import QTabWidget, QDialog, QDialogButtonBox, \
    QLabel, QWidget, QVBoxLayout, QPushButton, QComboBox, QDoubleSpinBox, QHBoxLayout, \
    QTableWidget, QAbstractItemView

from post_new import magnification_factor


class BeamProperties(QDialog):
    def __init__(self, rectItem, rect_prop, scene, parent=None):
        super().__init__(parent)
        self.direction = None
        self.rectItem = rectItem
        self.rect_prop = rect_prop
        self.beamDepth = None

        # IMAGE
        self.scene = scene

        self.setWindowTitle("Beam Properties")
        self.setMinimumSize(200, 400)

        v_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setWindowTitle("Object Data")
        self.button_box = button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept_control)  # Change from dialog.accept to self.accept
        self.button_box.rejected.connect(self.reject)  # Change from dialog.reject to self.reject

        self.create_geometry_tab()
        self.create_assignment_tab()
        self.lineLoad = lineLoad(self.tab_widget, self.rect_prop[self.rectItem])
        self.pointLoad = pointLoad_line(self.tab_widget, self.rect_prop[self.rectItem])

        v_layout.addWidget(self.tab_widget)
        v_layout.addWidget(button_box)
        self.setLayout(v_layout)  # Change from dialog.setLayout to self.setLayout

    # Rest of the code remains the same

    # dialog.show()

    def accept_control(self):
        self.lineLoad.print_values()
        self.pointLoad.print_values()
        self.accept()

        print(self.rect_prop)

    def create_geometry_tab(self):
        start = tuple([i / magnification_factor for i in self.rect_prop[self.rectItem]["coordinate"][0]])
        end = tuple([i / magnification_factor for i in self.rect_prop[self.rectItem]["coordinate"][1]])
        tab = QWidget()
        self.tab_widget.addTab(tab, f"Geometry")
        label0 = QLabel("Label")
        joistLabel = QLabel(self.rect_prop[self.rectItem]["label"])
        label1 = QLabel("Start")
        start_point = QLabel(f"{start}")
        label2 = QLabel("End")
        end_point = QLabel(f"{end}")

        # calc length
        l = self.length(start, end)
        label3 = QLabel("Length")
        length = QLabel(f"{l}")

        # LAYOUT
        h_layout0 = QHBoxLayout()
        h_layout0.addWidget(label0)
        h_layout0.addWidget(joistLabel)
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(label1)
        h_layout1.addWidget(start_point)
        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(label2)
        h_layout2.addWidget(end_point)
        h_layout3 = QHBoxLayout()
        h_layout3.addWidget(label3)
        h_layout3.addWidget(length)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout0)
        v_layout.addLayout(h_layout1)
        v_layout.addLayout(h_layout2)
        v_layout.addLayout(h_layout3)
        tab.setLayout(v_layout)

    def create_assignment_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, f"Assignments")
        label1 = QLabel("Beam Depth")
        self.beamDepth = beamDepth = QComboBox()
        beamDepth.addItems(["10 in", "12 in"])
        floor = self.rect_prop[self.rectItem]["floor"]
        if floor:
            floorText = "12 in"
        else:
            floorText = "10 in"

        self.beamDepth.setCurrentText(floorText)
        self.button_box.accepted.connect(self.accept_control)  # Change from dialog.accept to self.accept
        self.button_box.rejected.connect(self.reject)  # Change from dialog.reject to self.reject
        self.beamDepth.currentTextChanged.connect(self.beam_depth_control)

        # LAYOUT
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(label1)
        h_layout1.addWidget(beamDepth)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout1)

        tab.setLayout(v_layout)
        # return self.direction

        # SLOT

    def beam_depth_control(self):
        depth = self.beamDepth.currentText()
        if "10" in depth:
            floor = False
        else:
            floor = True
        self.rect_prop[self.rectItem]["floor"] = floor

    @staticmethod
    def length(start, end):
        x1 = start[0]
        x2 = end[0]
        y1 = start[1]
        y2 = end[1]
        l = (((y2 - y1) ** 2) + ((x2 - x1) ** 2)) ** 0.5
        return round(l, 2)


class lineLoad(QWidget):
    def __init__(self, tab_widget, itemProp):
        super().__init__()
        self.itemProp = itemProp
        self.load_data = itemProp["load"]["line"]
        tab_widget.addTab(self, f"Line Load")
        self.distance = None
        self.distance_value = 0

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
        distance = QLabel("Distance from Start")
        load_length = QLabel("length")
        load_type = QLabel("Load Type")
        mag = QLabel("Magnitude")
        self.header_layout.addWidget(distance, 1)
        self.header_layout.addWidget(load_length, 1)
        self.header_layout.addWidget(load_type, 1)
        self.header_layout.addWidget(mag, 1)

        # self.x_y_layout = QVBoxLayout(self)
        # x = QLabel("X")
        # y = QLabel("Y")
        # self.x_y_layout.addWidget(x)
        # self.x_y_layout.addWidget(y)
        self.tableWidget = QTableWidget(0, 4)
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

        self.distance = distance = QDoubleSpinBox()
        distance.setDecimals(3)
        distance.setRange(0, self.itemProp["length"] / magnification_factor)
        distance.valueChanged.connect(self.distance_slot)
        length = QDoubleSpinBox()
        length.setDecimals(3)

        length.setRange(0,
                        (self.itemProp["length"] / magnification_factor))
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
            distance.setValue(row_data['distance'] / magnification_factor)
            length.setValue(row_data['length'] / magnification_factor)

        self.tableWidget.setCellWidget(row, 0, distance)
        self.tableWidget.setCellWidget(row, 1, length)
        self.tableWidget.setCellWidget(row, 2, comboBox)
        self.tableWidget.setCellWidget(row, 3, spinBox)

    def delete_item(self):
        currentRow = self.tableWidget.currentRow()
        self.tableWidget.removeRow(currentRow)

    def print_values(self):
        self.load_data.clear()  # clear the old values
        for row in range(self.tableWidget.rowCount()):
            distance = self.tableWidget.cellWidget(row, 0)
            length = self.tableWidget.cellWidget(row, 1)
            comboBox = self.tableWidget.cellWidget(row, 2)
            spinBox = self.tableWidget.cellWidget(row, 3)
            self.load_data.append({
                'type': comboBox.currentText(),
                'magnitude': spinBox.value(),
                'distance': distance.value() * magnification_factor,
                'length': length.value() * magnification_factor
            })
            print(f"Row {row + 1}: Combo box value: {comboBox.currentText()}, Spin box value: {spinBox.value()}")

    # SLOT
    def distance_slot(self):
        self.distance_value = self.distance.value()


class pointLoad_line(QWidget):
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
        distance = QLabel("Distance from Start")
        load_type = QLabel("Load Type")
        mag = QLabel("Magnitude")
        self.header_layout.addWidget(distance, 1)
        self.header_layout.addWidget(load_type, 1)
        self.header_layout.addWidget(mag, 1)

        # self.x_y_layout = QVBoxLayout(self)
        # x = QLabel("X")
        # y = QLabel("Y")
        # self.x_y_layout.addWidget(x)
        # self.x_y_layout.addWidget(y)
        self.tableWidget = QTableWidget(0, 3)
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

        self.distance = distance = QDoubleSpinBox()
        distance.setDecimals(3)
        print("adfasfasfasfaf", self.itemProp)
        distance.setRange(0, self.itemProp["length"] / magnification_factor)
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
            distance.setValue(row_data['distance'] / magnification_factor)

        self.tableWidget.setCellWidget(row, 0, distance)
        self.tableWidget.setCellWidget(row, 1, comboBox)
        self.tableWidget.setCellWidget(row, 2, spinBox)

    def delete_item(self):
        currentRow = self.tableWidget.currentRow()
        self.tableWidget.removeRow(currentRow)

    def print_values(self):
        self.load_data.clear()  # clear the old values
        for row in range(self.tableWidget.rowCount()):
            distance = self.tableWidget.cellWidget(row, 0)
            comboBox = self.tableWidget.cellWidget(row, 1)
            spinBox = self.tableWidget.cellWidget(row, 2)
            self.load_data.append({
                'type': comboBox.currentText(),
                'magnitude': spinBox.value(),
                'distance': distance.value() * magnification_factor
            })
