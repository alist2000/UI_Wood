from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QGraphicsView
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt

from grid import GridWidget

from post_new import PostButton
from joist_new import JoistButton
from Beam import BeamButton
from ShearWall import ShearWallButton
from StudWall import StudWallButton


class secondTabWidget(QTabWidget):
    def __init__(self, inputs):
        super().__init__()
        self.level_number = inputs.get("level_number")
        self.h_grid_number = inputs.get("h_grid_number")
        self.v_grid_number = inputs.get("v_grid_number")
        self.height_story = inputs.get("height_story")
        self.h_spacing = inputs.get("h_spacing")
        self.v_spacing = inputs.get("v_spacing")
        self.setWindowTitle("Grid")
        self.setMinimumSize(600, 500)
        # self.tab_widget = QTabWidget()
        # self.tab_widget.setWindowTitle("Grid")
        # self.tab_widget.setMinimumSize(600, 500)

        self.create_tab()

        print(inputs)

        # Create a QTabWidget and add tabs to it

    def create_tab(self):
        for i in range(self.level_number):
            tab = QWidget()
            self.addTab(tab, f"Story {i + 1}")
            # self.tab_widget.addTab(tab, f"Story {i + 1}")

            # ADD POST BUTTON
            post_instance = PostButton(tab)
            post_item = post_instance.post

            # ADD JOIST BUTTON
            joist_instance = JoistButton(tab)
            joist_item = joist_instance.joist

            # ADD BEAM BUTTON
            beam_instance = BeamButton(tab)
            beam_item = beam_instance.beam

            # ADD SHEAR WALL BUTTON
            shearWall_instance = ShearWallButton(tab)
            shearWall_item = shearWall_instance.shearWall

            # ADD STUD WALL BUTTON
            studWall_instance = StudWallButton(tab)
            studWall_item = studWall_instance.studWall

            # ADD GRID LINES
            grid = GridWidget(self.h_grid_number, self.v_grid_number, self.h_spacing, self.v_spacing, post_instance,
                              joist_instance, beam_instance, shearWall_instance, studWall_instance)

            # LAYOUT
            h_layout = QHBoxLayout()
            h_layout.addWidget(grid, 15)
            v_layout = QVBoxLayout()
            v_layout.addWidget(post_item)
            v_layout.addWidget(joist_item)
            v_layout.addWidget(beam_item)
            v_layout.addWidget(shearWall_item)
            v_layout.addWidget(studWall_item)

            h_layout.addLayout(v_layout, 1)

            tab.setLayout(h_layout)

        # Show the QTabWidget
        self.show()
        # self.tab_widget.show()
