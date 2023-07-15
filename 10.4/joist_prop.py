from PySide6.QtWidgets import QTabWidget, QDialog, QDialogButtonBox, \
    QLabel, QWidget, QVBoxLayout, QPushButton, QComboBox, QDoubleSpinBox, QHBoxLayout, \
    QTableWidget, QAbstractItemView, QCheckBox

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QColor

from area_centroid_calculator import calculate_centroid_and_area
from post_new import magnification_factor


class JoistProperties(QDialog):
    def __init__(self, rectItem, rect_prop, center_position, joint_coordinate, image, scene, parent=None):
        super().__init__(parent)
        self.direction = None
        self.default = rect_prop[rectItem]["direction"]
        self.final_direction = rect_prop[rectItem]["direction"]
        self.rectItem = rectItem
        self.rect_prop = rect_prop
        self.joint_coordinate = joint_coordinate
        self.position = center_position
        self.loadRect = []

        # IMAGE
        self.image = image
        self.scene = scene

        self.setWindowTitle("Joist Properties")
        self.setMinimumSize(200, 400)

        v_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setWindowTitle("Object Data")
        self.button_box = button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.create_geometry_tab()
        self.create_direction_tab()
        self.load_data = self.rect_prop[self.rectItem]["load"]["total_area"]
        self.loadTab = JoistLoad(self.tab_widget, self.load_data)
        self.loadTab_custom = JoistCustomLoad(self.tab_widget, self.rect_prop[self.rectItem], self.scene)
        # self.rect_prop[self.rectItem]["load"]["total_area"] = self.loadTab.load_data
        # self.rect_prop[self.rectItem]["load"]["custom_area"] = self.loadTab_custom.load_data

        # self.create_load_tab()
        # self.direction = self.create_direction_tab()

        v_layout.addWidget(self.tab_widget)
        v_layout.addWidget(button_box)
        self.setLayout(v_layout)  # Change from dialog.setLayout to self.setLayout

    # Rest of the code remains the same

    # dialog.show()
    def closeEvent(self, event):
        self.loadRect = self.loadTab_custom.rectangleList
        for load in self.loadRect:
            if load is not None:
                print("deleting")
                self.scene.removeItem(load)
                # self.loadRect.remove(load)
        super().closeEvent(event)

    def accept_control(self):
        self.final_direction = self.default
        if self.final_direction == "N-S":
            picture_path = "images/n_s.png"
        else:
            picture_path = "images/e_w.png"
        self.image.change_image(picture_path, self.scene)
        self.rect_prop[self.rectItem]["direction"] = self.final_direction
        self.accept()
        self.loadTab.print_values()
        self.loadTab_custom.print_values()

        self.loadRect = self.loadTab_custom.rectangleList
        for load in self.loadRect:
            if load is not None:
                print("deleting")
                self.scene.removeItem(load)
                # self.loadRect.remove(load)

        print(self.rect_prop)

    def create_geometry_tab(self):
        point1 = tuple([i / magnification_factor for i in self.joint_coordinate[0]])
        point2 = tuple([i / magnification_factor for i in self.joint_coordinate[1]])
        point3 = tuple([i / magnification_factor for i in self.joint_coordinate[2]])
        point4 = tuple([i / magnification_factor for i in self.joint_coordinate[3]])
        xc, yc, area = calculate_centroid_and_area(self.joint_coordinate, magnification_factor)
        tab = QWidget()
        self.tab_widget.addTab(tab, f"Geometry")
        label0 = QLabel("Label")
        joistLabel = QLabel(self.rect_prop[self.rectItem]["label"])
        label1 = QLabel("Joint1")
        joint1 = QLabel(f"{point1}")
        label2 = QLabel("Joint2")
        joint2 = QLabel(f"{point2}")
        label3 = QLabel("Joint3")
        joint3 = QLabel(f"{point3}")
        label4 = QLabel("Joint4")
        joint4 = QLabel(f"{point4}")

        label5 = QLabel("Centroid X")
        joint5 = QLabel(f"{xc}")
        label6 = QLabel("Centroid Y")
        joint6 = QLabel(f"{yc}")
        label7 = QLabel("Total Area")
        joint7 = QLabel(f"{area}")

        label8 = QLabel("Joist Exist")

        post_exist = QLabel("Yes")

        # control post existence
        # if self.position in self.Joist_position_list:
        #     post_exist = QLabel("Yes")
        # else:
        #     post_exist = QLabel("No")

        # LAYOUT
        h_layout0 = QHBoxLayout()
        h_layout0.addWidget(label0)
        h_layout0.addWidget(joistLabel)
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(label1)
        h_layout1.addWidget(joint1)
        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(label2)
        h_layout2.addWidget(joint2)
        h_layout3 = QHBoxLayout()
        h_layout3.addWidget(label3)
        h_layout3.addWidget(joint3)
        h_layout4 = QHBoxLayout()
        h_layout4.addWidget(label4)
        h_layout4.addWidget(joint4)
        h_layout5 = QHBoxLayout()
        h_layout5.addWidget(label5)
        h_layout5.addWidget(joint5)
        h_layout6 = QHBoxLayout()
        h_layout6.addWidget(label6)
        h_layout6.addWidget(joint6)
        h_layout7 = QHBoxLayout()
        h_layout7.addWidget(label7)
        h_layout7.addWidget(joint7)
        h_layout8 = QHBoxLayout()
        h_layout8.addWidget(label8)
        h_layout8.addWidget(post_exist)
        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout0)
        v_layout.addLayout(h_layout1)
        v_layout.addLayout(h_layout2)
        v_layout.addLayout(h_layout3)
        v_layout.addLayout(h_layout4)
        v_layout.addLayout(h_layout5)
        v_layout.addLayout(h_layout6)
        v_layout.addLayout(h_layout7)
        v_layout.addLayout(h_layout8)
        tab.setLayout(v_layout)

    def create_direction_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, f"Direction")
        label1 = QLabel("Joist Direction")
        self.direction = direction = QComboBox()
        direction.addItems(["N-S", "E-W"])
        self.direction.setCurrentText(self.rect_prop[self.rectItem]["direction"])
        self.button_box.accepted.connect(self.accept_control)  # Change from dialog.accept to self.accept
        self.button_box.rejected.connect(self.reject)  # Change from dialog.reject to self.reject
        self.direction.currentTextChanged.connect(self.direction_control)

        # LAYOUT
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(label1)
        h_layout1.addWidget(direction)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout1)

        tab.setLayout(v_layout)
        # return self.direction

    # SLOT
    def direction_control(self):
        self.default = self.direction.currentText()


class JoistLoad(QWidget):
    def __init__(self, tab_widget, load_data):
        super().__init__()
        self.load_data = load_data
        tab_widget.addTab(self, f"Load")
        self.layout = QVBoxLayout(self)

        self.buttonAdd = QPushButton("Add")
        self.buttonDelete = QPushButton("Delete")
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.buttonAdd)
        self.buttons_layout.addWidget(self.buttonDelete)
        self.tableWidget = QTableWidget(0, 2)

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
        for row_data in self.load_data:
            self.add_item(row_data)

    def add_item(self, row_data=None):
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


class JoistCustomLoad(QWidget):
    def __init__(self, tab_widget, joistProp, scene):
        super().__init__()

        self.joistProp = joistProp
        self.scene = scene
        self.load_data = joistProp["load"]["custom_area"]
        tab_widget.addTab(self, f"Custom Load")
        self.layout = QVBoxLayout(self)
        self.buttons_layout = QHBoxLayout()
        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None
        self.rectangleList = []
        self.rectangleDict = {}
        self.rectangle = None
        self.x2_min = self.joistProp["coordinate"][0][0] / magnification_factor
        self.y2_min = self.joistProp["coordinate"][0][1] / magnification_factor
        self.buttonAdd = QPushButton("Add")
        self.buttonDelete = QPushButton("Delete")
        self.buttons_layout.addWidget(self.buttonAdd)
        self.buttons_layout.addWidget(self.buttonDelete)

        self.checkbox = None

        self.header_layout = QHBoxLayout(self)
        x_top_left = QLabel("X Top-Left")
        y_top_left = QLabel("Y Top-Left")
        x_bottom_right = QLabel("X Bottom-Right")
        y_bottom_right = QLabel("Y Bottom-Right")
        load_type = QLabel("Load Type")
        mag = QLabel("Magnitude")
        self.header_layout.addWidget(x_top_left, 1)
        self.header_layout.addWidget(y_top_left, 1)
        self.header_layout.addWidget(x_bottom_right, 1)
        self.header_layout.addWidget(y_bottom_right, 1)
        self.header_layout.addWidget(load_type, 1)
        self.header_layout.addWidget(mag, 1)

        # self.x_y_layout = QVBoxLayout(self)
        # x = QLabel("X")
        # y = QLabel("Y")
        # self.x_y_layout.addWidget(x)
        # self.x_y_layout.addWidget(y)
        self.tableWidget = QTableWidget(0, 7)
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

        self.x1 = x1 = QDoubleSpinBox()
        x1.setDecimals(3)
        x1.setRange(self.joistProp["coordinate"][0][0] / magnification_factor,
                    self.joistProp["coordinate"][2][0] / magnification_factor)
        x1.valueChanged.connect(self.x1_slot)

        self.x2 = x2 = QDoubleSpinBox()
        x2.setDecimals(3)

        x2.setRange(self.x2_min,
                    self.joistProp["coordinate"][2][0] / magnification_factor)
        self.y1 = y1 = QDoubleSpinBox()
        y1.setDecimals(3)

        y1.setRange(self.joistProp["coordinate"][0][1] / magnification_factor,
                    self.joistProp["coordinate"][2][1] / magnification_factor)
        y1.valueChanged.connect(self.y1_slot)

        self.y2 = y2 = QDoubleSpinBox()
        y2.setDecimals(3)

        y2.setRange(self.y2_min,
                    self.joistProp["coordinate"][2][1] / magnification_factor)
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

        checkbox = QCheckBox('Show rectangle', self)
        checkbox.setChecked(False)
        checkbox.stateChanged.connect(self.toggle_rectangle)

        if row_data:  # if row_data is provided
            comboBox.setCurrentText(row_data['type'])
            spinBox.setValue(row_data['magnitude'])
            self.x1.setValue(row_data['x1'] / magnification_factor)
            self.x2.setValue(row_data['x2'] / magnification_factor)
            self.y1.setValue(row_data['y1'] / magnification_factor)
            self.y2.setValue(row_data['y2'] / magnification_factor)

        self.tableWidget.setCellWidget(row, 0, self.x1)
        self.tableWidget.setCellWidget(row, 1, self.y1)
        self.tableWidget.setCellWidget(row, 2, self.x2)
        self.tableWidget.setCellWidget(row, 3, self.y2)
        self.tableWidget.setCellWidget(row, 4, comboBox)
        self.tableWidget.setCellWidget(row, 5, spinBox)
        self.tableWidget.setCellWidget(row, 6, checkbox)

        # self.draw_rectangle()

    def delete_item(self):
        currentRow = self.tableWidget.currentRow()
        self.tableWidget.removeRow(currentRow)

    def print_values(self):
        self.load_data.clear()  # clear the old values
        for row in range(self.tableWidget.rowCount()):
            x1 = self.tableWidget.cellWidget(row, 0)
            y1 = self.tableWidget.cellWidget(row, 1)
            x2 = self.tableWidget.cellWidget(row, 2)
            y2 = self.tableWidget.cellWidget(row, 3)
            comboBox = self.tableWidget.cellWidget(row, 4)
            spinBox = self.tableWidget.cellWidget(row, 5)
            self.load_data.append({
                'type': comboBox.currentText(),
                'magnitude': spinBox.value(),
                'x1': x1.value() * magnification_factor,
                'y1': y1.value() * magnification_factor,
                'x2': x2.value() * magnification_factor,
                'y2': y2.value() * magnification_factor
            })
            print(f"Row {row + 1}: Combo box value: {comboBox.currentText()}, Spin box value: {spinBox.value()}")

    # SLOT
    def x1_slot(self):
        self.x2_min = self.x1.value()

    # SLOT
    def y1_slot(self):
        self.y2_min = self.y1.value()

    # def draw_rectangle(self):
    #     x1 = self.x1.value()
    #     y1 = self.y1.value()
    #     x2 = self.x2.value()
    #     y2 = self.y2.value()
    #
    #     # self.scene.clear()  # clear previous drawings
    #     if self.checkbox.isChecked():
    #         self.rectangle = self.scene.addRect(
    #             QRectF(x1 * magnification_factor, y1 * magnification_factor, (x2 - x1) * magnification_factor, (
    #                     y2 - y1) * magnification_factor), QPen(QColor(255, 0, 0)))
    #         self.rectangleList.append(self.rectangle)
    #     else:
    #         try:
    #             self.rectangleList.remove(self.rectangle)
    #         except:
    #             pass
    def draw_rectangle(self, row):
        x1 = self.tableWidget.cellWidget(row, 0).value()
        y1 = self.tableWidget.cellWidget(row, 1).value()
        x2 = self.tableWidget.cellWidget(row, 2).value()
        y2 = self.tableWidget.cellWidget(row, 3).value()
        self.rectangle = self.scene.addRect(
            QRectF(x1 * magnification_factor, y1 * magnification_factor, (x2 - x1) * magnification_factor, (
                    y2 - y1) * magnification_factor), QPen(QColor(255, 0, 0)))
        self.rectangleList.append(self.rectangle)
        self.rectangleDict[f"{row}"] = self.rectangle

    def toggle_rectangle(self):
        row = self.tableWidget.currentRow()
        self.checkbox = self.tableWidget.cellWidget(row, 6)
        print("ROW:   ", row)
        if self.checkbox.isChecked():
            self.draw_rectangle(row)
            self.rectangle.setVisible(self.checkbox.isChecked())
            self.rectangleList.append(self.rectangle)

        else:
            try:
                self.rectangleList.remove(self.rectangle)
            except:
                pass
            if self.rectangleDict[f"{row}"]:
                try:
                    self.scene.removeItem(self.rectangleDict[f"{row}"])
                except:
                    print("FUCKED")

            # for load in self.rectangleList:
            #     if load is not None:
            #         print("deleting")
            #         self.scene.removeItem(load)
            #         # self.loadRect.remove(load)
