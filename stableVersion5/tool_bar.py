import copy

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QGraphicsView, QToolBar, \
    QMainWindow, QMenu, QMenuBar, QDialogButtonBox, QDialog, QLabel, QSpinBox, QDoubleSpinBox, QComboBox
from PySide6.QtWidgets import QMainWindow, QGraphicsScene, QToolBar, QFileDialog, QApplication, QGraphicsView, \
    QGraphicsPixmapItem, QGraphicsItem, QSlider, QVBoxLayout, QGraphicsOpacityEffect, QStackedLayout
from PySide6.QtGui import QPixmap, QAction, QKeyEvent
from PySide6.QtCore import Qt, QPoint

from set_uniform_load import set_uniform_load
from replicate import Replicate
from delete import Delete
from save import Save
from Edit_properties import EditProperties

class ToolBar:
    def __init__(self, mainPage):
        self.mainPage = mainPage
        self.dialogPage = load_seismic_dialog(self)
        self.dialogPage2 = set_uniform_load(self)
        self.dialogPage3 = Replicate(self)
        self.dialogPage4 = Delete(self)
        self.savePage = Save(self)
        self.EditProperties = EditProperties(self)

        self.spin_values = [0.75, 2.75, 0.1, 0.1, 0.1, 8, 6.5]
        self.combo_values = ["I & II", "Y"]
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

        # Create Define Set Uniform Load Cases
        replicate = QAction('Replicate', self.mainPage)
        replicate.triggered.connect(self.dialogPage3.rep_exec)
        # replicate.triggered.connect(self.dialogPage3.rep_exec)
        tool_bar.addAction(replicate)

        # Create Define Set Uniform Load Cases
        delete = QAction('Delete', self.mainPage)
        delete.triggered.connect(self.dialogPage4.rep_exec)
        tool_bar.addAction(delete)

        # Create Save option
        save_action = QAction('Save', self.mainPage)
        save_action.triggered.connect(self.savePage.save_clicked)
        tool_bar.addAction(save_action)

        # Create Edit option
        edit_action = QAction('Edit Project', self.mainPage)
        edit_action.triggered.connect(self.EditProperties.show)
        tool_bar.addAction(edit_action)

        # saveAction.triggered.connect(self.save_tabs)


class load_seismic_dialog:
    def __init__(self, mainPage):
        self.mainPage = mainPage

    def load_seismic_parameters(self):
        dialog = QDialog()
        dialog.setWindowTitle("Seismic Parameters")

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        spin_boxes = []
        combo_boxes = []
        labels_number = ["S1", "Ss", "Fa", "Fv", "I", "T model", "R Factor"]
        # Create and add the labels and spin_boxes
        for i, label in enumerate(labels_number):
            h_layout = QHBoxLayout()
            Label = QLabel(f'{label} ')
            h_layout.addWidget(Label)

            self.create_spin_box(i, h_layout, spin_boxes)
            layout.addLayout(h_layout)

        # Create and add the labels and combo_boxes
        h_layout = QHBoxLayout()
        h_layout2 = QHBoxLayout()

        label = QLabel("Risk Category")
        label2 = QLabel("Regular Building")
        h_layout.addWidget(label)
        h_layout2.addWidget(label2)

        combobox = QComboBox()
        combobox.addItems(["I & II", "III", "IV"])
        combobox.setCurrentText(self.mainPage.combo_values[0])
        h_layout.addWidget(combobox)
        layout.addLayout(h_layout)
        combo_boxes.append(combobox)

        combobox2 = QComboBox()
        combobox2.addItems(["Y", "N"])
        combobox2.setCurrentText(self.mainPage.combo_values[1])
        h_layout2.addWidget(combobox2)
        layout.addLayout(h_layout2)
        combo_boxes.append(combobox2)

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
        spinbox = QDoubleSpinBox()
        spinbox.setValue(self.mainPage.spin_values[i])
        spinbox.setRange(0.1, 1000)
        spinbox.setDecimals(4)
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
