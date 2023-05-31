from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTabWidget, QPushButton, QLabel, QLineEdit, QSpacerItem
from general_properties import Widget_button
from Information import Widget_form


class tabWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WOOD DESIGN APPLICATION")

        tab_widget = QTabWidget(self)

        # Information - Tab 1
        widget_form = Widget_form()

        # Buttons - Tab 2
        widget_buttons = Widget_button()

        # Add tabs to widget
        tab_widget.addTab(widget_form, "General Information")
        tab_widget.addTab(widget_buttons, "General Properties")

        layout = QVBoxLayout()
        layout.addWidget(tab_widget)

        self.setLayout(layout)
