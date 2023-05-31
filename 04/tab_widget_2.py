from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTabWidget
from grid import GridWidget


class secondTabWidget(QWidget):
    def __init__(self, inputs):
        super().__init__()
        self.level_number = inputs.get("level_number")
        self.h_grid_number = inputs.get("h_grid_number")
        self.v_grid_number = inputs.get("v_grid_number")
        self.height_story = inputs.get("height_story")
        self.h_spacing = inputs.get("h_spacing")
        self.v_spacing = inputs.get("v_spacing")
        self.tab_widget = QTabWidget()
        self.tab_widget.setWindowTitle("Grid")
        self.tab_widget.setMinimumSize(600, 500)

        self.grid = grid = GridWidget(self.h_grid_number, self.v_grid_number, self.h_spacing, self.v_spacing)

        v_layout = QVBoxLayout()
        v_layout.addWidget(grid)
        self.v_layout = v_layout

        self.create_tab()

        print(inputs)

        # Create a QTabWidget and add tabs to it

    def create_tab(self):
        for i in range(self.level_number):
            tab = QWidget()
            self.tab_widget.addTab(tab, f"Story {i + 1}")
            self.grid = grid = GridWidget(self.h_grid_number, self.v_grid_number, self.h_spacing, self.v_spacing)

            v_layout = QVBoxLayout()
            v_layout.addWidget(grid)
            tab.setLayout(v_layout)

        # Show the QTabWidget
        self.tab_widget.show()
