from PySide6.QtWidgets import QTabWidget, QDialog, QDialogButtonBox, \
    QLabel, QWidget, QVBoxLayout, QPushButton, QComboBox, QDoubleSpinBox, QHBoxLayout, \
    QTableWidget, QAbstractItemView, QCheckBox

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QColor

from area_centroid_calculator import calculate_centroid_and_area
from post_new import magnification_factor


class LoadProperties(QDialog):
    def __init__(self, rectItem, rect_prop, center_position, joint_coordinate, all_load, scene, parent=None):
        super().__init__(parent)
        self.uniformLoad = None
        self.defaultLoad = rect_prop[rectItem]["label"]
        self.rectItem = rectItem
        self.rect_prop = rect_prop
        self.joint_coordinate = joint_coordinate
        self.position = center_position
        self.all_load = all_load

        self.scene = scene

        self.setWindowTitle("Load Properties")
        self.setMinimumSize(200, 400)

        v_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setWindowTitle("Object Data")
        self.button_box = button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.create_geometry_tab()
        self.set_uniform_load_tab()
        # self.load_data = self.rect_prop[self.rectItem]["load"]["total_area"]
        # self.loadTab = LoadLoad(self.tab_widget, self.load_data)
        # self.loadTab_custom = LoadCustomLoad(self.tab_widget, self.rect_prop[self.rectItem], self.scene)
        # self.rect_prop[self.rectItem]["load"]["total_area"] = self.loadTab.load_data
        # self.rect_prop[self.rectItem]["load"]["custom_area"] = self.loadTab_custom.load_data

        # self.create_load_tab()
        # self.direction = self.create_direction_tab()

        v_layout.addWidget(self.tab_widget)
        v_layout.addWidget(button_box)
        self.setLayout(v_layout)  # Change from dialog.setLayout to self.setLayout

    # Rest of the code remains the same

    # dialog.show()
    # def closeEvent(self, event):
    #     self.loadRect = self.loadTab_custom.rectangleList
    #     for load in self.loadRect:
    #         if load is not None:
    #             print("deleting")
    #             self.scene.removeItem(load)
    #             # self.loadRect.remove(load)
    #     super().closeEvent(event)

    def accept_control(self):
        if self.uniformLoad.currentText():
            self.rect_prop[self.rectItem]["label"] = self.uniformLoad.currentText()
            for loadLabel, loads in self.all_load.items():
                if loadLabel == self.rect_prop[self.rectItem]["label"]:
                    self.rect_prop[self.rectItem]["load"] = loads
                    break
        else:
            self.rect_prop[self.rectItem]["label"] = ""
            self.rect_prop[self.rectItem]["load"] = []

        self.accept()
        # self.loadTab.print_values()
        # self.loadTab_custom.print_values()

        # # self.loadRect = self.loadTab_custom.rectangleList
        # for load in self.loadRect:
        #     if load is not None:
        #         print("deleting")
        #         self.scene.removeItem(load)
        #         # self.loadRect.remove(load)

        print(self.rect_prop)

    def create_geometry_tab(self):
        point1 = tuple([round(i / magnification_factor, 2) for i in self.joint_coordinate[0]])
        point2 = tuple([round(i / magnification_factor, 2) for i in self.joint_coordinate[1]])
        point3 = tuple([round(i / magnification_factor, 2) for i in self.joint_coordinate[2]])
        point4 = tuple([round(i / magnification_factor, 2) for i in self.joint_coordinate[3]])
        xc, yc, area = calculate_centroid_and_area(self.joint_coordinate, magnification_factor)
        tab = QWidget()
        self.tab_widget.addTab(tab, f"Geometry")
        label0 = QLabel("Label")
        loadLabel = QLabel(self.rect_prop[self.rectItem]["label"])
        label1 = QLabel("Joint1")
        joint1 = QLabel(f"{point1}")
        label2 = QLabel("Joint2")
        joint2 = QLabel(f"{point2}")
        label3 = QLabel("Joint3")
        joint3 = QLabel(f"{point3}")
        label4 = QLabel("Joint4")
        joint4 = QLabel(f"{point4}")

        # label5 = QLabel("Centroid X")
        # joint5 = QLabel(f"{xc}")
        # label6 = QLabel("Centroid Y")
        # joint6 = QLabel(f"{yc}")
        label7 = QLabel("Total Area")
        joint7 = QLabel(f"{round(area, 2)}")

        # label8 = QLabel("Load Exist")
        # 
        # post_exist = QLabel("Yes")

        # control post existence
        # if self.position in self.Load_position_list:
        #     post_exist = QLabel("Yes")
        # else:
        #     post_exist = QLabel("No")

        # LAYOUT
        h_layout0 = QHBoxLayout()
        h_layout0.addWidget(label0)
        h_layout0.addWidget(loadLabel)
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
        # h_layout5 = QHBoxLayout()
        # h_layout5.addWidget(label5)
        # h_layout5.addWidget(joint5)
        # h_layout6 = QHBoxLayout()
        # h_layout6.addWidget(label6)
        # h_layout6.addWidget(joint6)
        h_layout7 = QHBoxLayout()
        h_layout7.addWidget(label7)
        h_layout7.addWidget(joint7)
        # h_layout8 = QHBoxLayout()
        # h_layout8.addWidget(label8)
        # h_layout8.addWidget(post_exist)
        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout0)
        v_layout.addLayout(h_layout1)
        v_layout.addLayout(h_layout2)
        v_layout.addLayout(h_layout3)
        v_layout.addLayout(h_layout4)
        # v_layout.addLayout(h_layout5)
        # v_layout.addLayout(h_layout6)
        v_layout.addLayout(h_layout7)
        # v_layout.addLayout(h_layout8)
        tab.setLayout(v_layout)

    def set_uniform_load_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, f"Set Uniform Load")
        label1 = QLabel("Uniform Load")
        self.uniformLoad = uniformLoad = QComboBox()
        try:
            uniformLoad.addItems(self.rect_prop[self.rectItem]["load_set"])
        except KeyError:
            uniformLoad.addItems(list(self.all_load.keys()))
        # for load in self.rect_prop.values():
        #     uniformLoad.addItem(load["label"])
        self.uniformLoad.setCurrentText(self.rect_prop[self.rectItem]["label"])
        self.button_box.accepted.connect(self.accept_control)  # Change from dialog.accept to self.accept
        self.button_box.rejected.connect(self.reject)  # Change from dialog.reject to self.reject
        self.uniformLoad.currentTextChanged.connect(self.uniformLoad_control)

        # LAYOUT
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(label1)
        h_layout1.addWidget(uniformLoad)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout1)

        tab.setLayout(v_layout)
        # return self.direction

    # SLOT
    def uniformLoad_control(self):
        self.defaultLoad = self.uniformLoad.currentText()
