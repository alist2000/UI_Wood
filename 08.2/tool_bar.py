from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QGraphicsView, QToolBar, \
    QMainWindow, QMenu, QToolButton, QDialogButtonBox, QDialog, QLabel, QSpinBox, QDoubleSpinBox, QComboBox
from PySide6.QtGui import QKeyEvent, QAction
from PySide6.QtCore import Qt


class seismicParameters:
    def __init__(self, mainPage):
        self.mainPage = mainPage
        self.dialogPage = load_seismic_dialog(self)
        self.spin_values = [0, 0, 0, 0, 0, 0]
        self.combo_values = ["1"]
        self.create_tool_bar()

    def create_tool_bar(self):
        tool_bar = QToolBar("My Toolbar")
        self.mainPage.addToolBar(tool_bar)

        # Create a Save action
        seismic_parameters_action = QAction('Seismic Parameters', self.mainPage)
        seismic_parameters_action.triggered.connect(self.dialogPage.load_seismic_parameters)
        tool_bar.addAction(seismic_parameters_action)
        # saveAction.triggered.connect(self.save_tabs)


class load_seismic_dialog:
    def __init__(self, mainPage):
        self.mainPage = mainPage

    def load_seismic_parameters(self):
        print("hi")
        dialog = QDialog()
        dialog.setWindowTitle("Seismic Parameters")

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        spin_boxes = []
        combo_boxes = []
        labels_number = ["S1", "S2", "Fa", "Fv", "T model", "R Factor"]
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
        combobox.addItems(["1", "2", "3"])
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
