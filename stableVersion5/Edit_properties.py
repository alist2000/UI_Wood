from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
import json
import copy

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDoubleSpinBox, QLabel, QPushButton, \
    QTextEdit, QAbstractItemView, QTableWidget, \
    QRadioButton, QSpacerItem, QGraphicsView, QGraphicsScene

from UI_Wood.stableVersion5.line import LineDrawHandler

from UI_Wood.stableVersion5.grid_define import GridCoordinateDefine, GridPreview, \
    StoryCoordinateDefine


class EditProperties(QWidget):
    def __init__(self, mainPage, parent=None):
        super().__init__(parent)
        self.mainPage = mainPage
        self.data = None
        # final values
        self.level_final = None
        self.h_grid_number_final = None
        self.v_grid_number_final = None
        self.height_story_final = None
        self.h_spacing_final = None
        self.v_spacing_final = None
        self.x_grid, self.y_grid, self.grid_base = None, None, None

        # REPORT INPUTS

        # for new tab
        self.new_window = None

        self.setMinimumSize(600, 500)


        storyHeightLayout = QHBoxLayout()
        self.storyInstance = StoryCoordinateDefine()
        spacer = QSpacerItem(380, 20)
        storyHeightLayout.addWidget(self.storyInstance)
        # storyHeightLayout.addItem(spacer)

        self.gridInstance = GridCoordinateDefine()
        self.previewGrid = GridPreview(self.gridInstance)
        self.previewButton = QPushButton("PREVIEW")
        self.previewButton.clicked.connect(self.previewGrid.preview)
        previewLayout = QVBoxLayout()
        previewLayout.addWidget(self.previewGrid)
        previewLayout.addWidget(self.previewButton)
        storyHeightLayout.addLayout(previewLayout)

        # RUN Button
        self.height_story = []
        self.h_spacing_list = []
        self.v_spacing_list = []
        run = QPushButton("SUBMIT")
        load = QPushButton("LOAD")
        # run.clicked.connect(self.run_control)
        # load.clicked.connect(self.loadInstance.load_control)

        v_layout = QVBoxLayout()
        v_layout.addLayout(storyHeightLayout)
        v_layout.addWidget(self.gridInstance)
        v_layout.addWidget(run)
        v_layout.addWidget(load)
        self.setLayout(v_layout)
