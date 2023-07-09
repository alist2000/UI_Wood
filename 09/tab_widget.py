from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from general_properties import Widget_button
from Information import Widget_form

from report.report import Inputs


class tabWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Inputs for Report
        reportInputs = Inputs()

        self.setWindowTitle("WOOD DESIGN APPLICATION")

        tab_widget = QTabWidget(self)

        # Information - Tab 1
        widget_form = Widget_form(reportInputs)

        # Buttons - Tab 2
        widget_buttons = Widget_button(reportInputs)

        # Add tabs to widget
        tab_widget.addTab(widget_form, "General Information")
        tab_widget.addTab(widget_buttons, "General Properties")

        layout = QVBoxLayout()
        layout.addWidget(tab_widget)

        self.setLayout(layout)
