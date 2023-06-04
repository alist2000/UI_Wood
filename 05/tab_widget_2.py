from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton
from grid import GridWidget

from post import PostButton


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

        self.create_tab()

        print(inputs)

        # Create a QTabWidget and add tabs to it

    def create_tab(self):
        for i in range(self.level_number):
            tab = QWidget()
            self.tab_widget.addTab(tab, f"Story {i + 1}")

            # ADD POST BUTTON
            post_instance = PostButton(tab)
            post_item = post_instance.post

            # ADD GRID LINES
            grid = GridWidget(self.h_grid_number, self.v_grid_number, self.h_spacing, self.v_spacing, post_instance)



            # LAYOUT
            v_layout = QHBoxLayout()
            v_layout.addWidget(grid, 15)
            v_layout.addWidget(post_item, 1)
            tab.setLayout(v_layout)

        # Show the QTabWidget
        self.tab_widget.show()
