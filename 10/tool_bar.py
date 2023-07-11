import copy

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QGraphicsView, QToolBar, \
    QMainWindow, QMenu, QMenuBar, QDialogButtonBox, QDialog, QLabel, QSpinBox, QDoubleSpinBox, QComboBox
from PySide6.QtWidgets import QMainWindow, QGraphicsScene, QToolBar, QFileDialog, QApplication, QGraphicsView, \
    QGraphicsPixmapItem, QGraphicsItem, QSlider, QVBoxLayout, QGraphicsOpacityEffect, QStackedLayout
from PySide6.QtGui import QPixmap, QAction, QKeyEvent
from PySide6.QtCore import Qt, QPoint

from set_uniform_load import set_uniform_load


class ToolBar:
    def __init__(self, mainPage):
        self.mainPage = mainPage
        self.dialogPage = load_seismic_dialog(self)
        self.dialogPage2 = set_uniform_load(self)

        self.spin_values = [0, 0, 0, 0, 0, 0]
        self.combo_values = ["1"]
        self.create_tool_bar()

    def create_tool_bar(self):
        tool_bar = QToolBar("My Toolbar")
        self.mainPage.addToolBar(tool_bar)

        # Create a Seismic Parameter Action
        seismic_parameters_action = QAction('Seismic Parameters', self.mainPage)
        seismic_parameters_action.triggered.connect(self.dialogPage.load_seismic_parameters)
        tool_bar.addAction(seismic_parameters_action)

        # Create Define Set Uniform Load Cases
        seismic_parameters_action = QAction('Define Set Uniform Load', self.mainPage)
        seismic_parameters_action.triggered.connect(self.dialogPage2.uniform_load_exe)
        tool_bar.addAction(seismic_parameters_action)

        # saveAction.triggered.connect(self.save_tabs)


class load_seismic_dialog:
    def __init__(self, mainPage):
        self.mainPage = mainPage

    def load_seismic_parameters(self):
        joistProp = list(self.mainPage.mainPage.grid[0].joist_instance.rect_prop.values())
        self.mainPage.mainPage.grid[1].joist_instance.draw_joist_mousePress(None, None, joistProp[0]["coordinate"])
        # tabIndex = self.mainPage.mainPage.tabWidget.currentIndex()
        # # NOW FIND GRID OF THIS TAB.
        #
        # print(self.mainPage.mainPage.tabWidget.currentIndex())
        # print(self.mainPage.mainPage.tabWidget.currentWidget())
        #
        # source_tab_index = self.mainPage.mainPage.tabWidget.currentIndex()
        # target_tab_index = source_tab_index + 1
        # # Get the source and target tabs
        # source_tab = self.mainPage.mainPage.tabWidget.widget(source_tab_index)
        # target_tab = self.mainPage.mainPage.tabWidget.widget(target_tab_index)
        # print(source_tab)
        # widget_to_copy = target_tab.layout().itemAt(1).itemAt(0)
        # print("klalkdsjf", widget_to_copy)
        # # clear_layout(widget_to_copy)
        # # Add new widget to layout
        # new_button = QPushButton("New Button")
        # # add_widget_to_layout(widget_to_copy, self.mainPage.mainPage.grid[0])
        # key = list(self.mainPage.mainPage.grid[0].joist_instance.rect_prop.keys())
        # key1 = copy.deepcopy(key[0])
        # print("key", key)
        # self.mainPage.mainPage.grid[1].scene.addItem(key1)
        # add_widget_to_layout(widget_to_copy, self.mainPage.mainPage.grid[1])
        # source_tab = self.mainPage.mainPage.tabWidget.currentWidget()
        # target_tab = self.mainPage.mainPage.tabWidget.widget(target_tab_index)

        # Get the widget from the source tab
        # print("lkjk", source_tab)
        # print("s2", self.mainPage.mainPage.tabWidget.currentWidget())
        # for i in range(10):
        # widget_to_copy = source_tab.layout().itemAt(1)
        # lay = QStackedLayout()
        # lay.addWidget(widget_to_copy.itemAt(0).widget())
        # print("kaklfjajsf", widget_to_copy)
        # print("ksajfkasjg", source_tab.layout().itemAt(1))
        # source_tab.layout().itemAt(1).itemAt(0).setLayout(QVBoxLayout())
        # widget_to_copy = source_tab.layout()
        # print(source_tab.layout())
        # print(widget_to_copy)
        # # Create a new tab and layout
        # print(1)
        # new_tab = QWidget()
        # new_layout = QVBoxLayout(new_tab)
        # new_tab.setLayout(new_layout)
        #
        # print(2)
        # try:
        #     # Duplicate the widgets from the existing tab
        #     for i in range(widget_to_copy.count()):
        #         widget = widget_to_copy.itemAt(i).widget()
        #         if widget:
        #             new_layout.addWidget(widget)
        #         # new_layout.addWidget(widget)
        #     print(new_layout)
        # except:
        #     print("YOU FUCKED")

        # Create a new widget to hold the copied widget
        # copied_widget = QWidget()
        # a = source_tab.layout()
        #
        # # Copy the layout from the source widget to the new widget
        # copied_widget.setLayout(a)

        # Move widget1 to Tab 2
        # index = self.mainPage.mainPage.tabWidget.indexOf(target_tab)
        # print("index", index)
        # self.mainPage.mainPage.tabWidget.removeTab(index)
        # self.mainPage.mainPage.tabWidget.addTab(new_tab, "Tab 2")

        # Insert the new widget into the target tab
        # target_tab.layout().insertWidget(0, copied_widget)
        # # target_tab.setLayout(source_tab.layout)
        #
        # # Set the current index of the QTabWidget to the target tab
        # self.mainPage.mainPage.tabWidget.setCurrentIndex(target_tab_index)
        print("hi")
        dialog = QDialog()
        dialog.setWindowTitle("Seismic Parameters")

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        spin_boxes = []
        combo_boxes = []
        labels_number = ["S1", "Ss", "Fa", "Fv", "T model", "R Factor"]
        # Create and add the labels and spin_boxes
        for i, label in enumerate(labels_number):
            h_layout = QHBoxLayout()
            Label = QLabel(f'{label} ')
            h_layout.addWidget(Label)

            self.create_spin_box(i, h_layout, spin_boxes)
            layout.addLayout(h_layout)

        # Create and add the labels and combo_boxes
        h_layout = QHBoxLayout()

        label = QLabel("Risk Category")
        h_layout.addWidget(label)

        combobox = QComboBox()
        combobox.addItems(["I & II", "III", "IV"])
        combobox.setCurrentText(self.mainPage.combo_values[0])
        h_layout.addWidget(combobox)
        layout.addLayout(h_layout)
        combo_boxes.append(combobox)

        # Create and add the OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)

        button_box.accepted.connect(lambda: self.save_values(spin_boxes, combo_boxes, dialog))
        button_box.rejected.connect(dialog.reject)

        dialog.exec_()

    def save_values(self, spin_boxes, combo_boxes, dialog):
        self.mainPage.spin_values = [spinbox.value() for spinbox in spin_boxes]
        self.mainPage.combo_values = [combobox.currentText() for combobox in combo_boxes]
        dialog.accept()

    def create_spin_box(self, i, layout, spin_boxes):
        spinbox = QSpinBox()
        spinbox.setValue(self.mainPage.spin_values[i])
        layout.addWidget(spinbox)
        spin_boxes.append(spinbox)


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            clear_layout(item.layout())


def add_widget_to_layout(layout, widget):
    layout.addWidget(widget)
