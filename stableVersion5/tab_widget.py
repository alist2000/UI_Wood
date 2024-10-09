from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QApplication
from general_properties import Widget_button
from Information import Widget_form
from UI_Wood.stableVersion5.styles import TabWidgetStyle
from report.report import Inputs


class tabWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Inputs for Report
        reportInputs = Inputs()

        self.setWindowTitle("WOOD STRUCTURE DESIGN APPLICATION")

        tab_widget = QTabWidget(self)
        self.setStyleSheet(TabWidgetStyle)

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

    def showEvent(self, event):
        # Get the screen size
        screen_geometry = QApplication.primaryScreen().availableGeometry()

        # Calculate the center of the screen
        center = screen_geometry.center()

        # Calculate the position of the tab widget to place it in the center of the screen
        rect = self.frameGeometry()
        rect.moveCenter(center)

        # Move the tab widget to the calculated position
        self.move(rect.topLeft())

        super().showEvent(event)
