from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QGraphicsView, QToolBar, \
    QMainWindow, QMenu, QToolButton, QSlider, QMenuBar, QGraphicsItem
from PySide6.QtGui import QKeyEvent, QAction
from PySide6.QtCore import Qt

from grid import GridWidget

from post_new import PostButton
from joist_new import JoistButton
from load_map import LoadButton
from Beam import BeamButton
from ShearWall import ShearWallButton
from StudWall import StudWallButton
from action import save_tabs, load_tabs
from tool_bar import ToolBar
from menuBar import Image


class secondTabWidget(QMainWindow):
    def __init__(self, inputs):
        super().__init__()
        self.slider = None
        self.tabWidget = QTabWidget()
        self.shapes = []
        self.grid = []
        self.inputs = inputs
        self.level_number = inputs.get("level_number")
        self.h_grid_number = inputs.get("h_grid_number")
        self.v_grid_number = inputs.get("v_grid_number")
        self.height_story = inputs.get("height_story")
        self.h_spacing = inputs.get("h_spacing")
        self.v_spacing = inputs.get("v_spacing")
        self.tabWidget.setWindowTitle("Grid")
        self.tabWidget.setMinimumSize(600, 500)
        # toolBar = QToolBar("ToolBar", self)
        # self.addToolBar(toolBar)
        # save_action = QAction('Save', self)
        # # save_action.triggered.connect(lambda: save_tabs(self))
        #
        # load_action = QAction('Load', self)
        # # load_action.triggered.connect(lambda: load_tabs(self))
        #
        # menu = QMenu('My Menu', self)
        # menu.addAction(save_action)
        # menu.addAction(load_action)
        # toolButton = QToolButton()
        # toolButton.setMenu(menu)
        # toolButton.setText("File")
        # toolButton.setPopupMode(QToolButton.InstantPopup)
        # toolBar.addWidget(toolButton)

        self.setCentralWidget(self.tabWidget)
        self.toolBar = ToolBar(self)
        # self.create_tool_bar()
        self.show()
        # self.tab_widget = QTabWidget()
        # self.tab_widget.setWindowTitle("Grid")
        # self.tab_widget.setMinimumSize(600, 500)

        self.create_tab()

        print(inputs)

        # Create a QTabWidget and add tabs to it

    # def create_tool_bar(self):
    #     tool_bar = QToolBar("My Toolbar")
    #     self.addToolBar(tool_bar)
    #
    #     # Create a Save action
    #     seismic_parameters_action = QAction('Seismic Parameters', self)
    #     seismic_parameters_action.triggered.connect(load_seismic_parameters)
    #     tool_bar.addAction(seismic_parameters_action)
    #     # saveAction.triggered.connect(self.save_tabs)

    def create_tab(self):
        for i in range(self.level_number):
            self.shapes = []

            tab = QWidget()
            self.tabWidget.addTab(tab, f"Story {i + 1}")
            # self.tab_widget.addTab(tab, f"Story {i + 1}")

            # OPACITY SLIDER
            self.slider = QSlider(Qt.Vertical)
            self.slider.setRange(0, 100)
            self.slider.setValue(100)

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

            # ADD JOIST BUTTON
            load_instance = LoadButton(tab)
            load_item = load_instance.load

            # ADD RUN (NOW IT IS FOR TEST)
            runButton = QPushButton("RUN")

            # ADD GRID LINES
            grid = GridWidget(self.h_grid_number, self.v_grid_number, self.h_spacing, self.v_spacing, post_instance,
                              joist_instance, beam_instance, shearWall_instance, studWall_instance, runButton,
                              self.shapes, self.slider, load_instance, self.toolBar)

            self.grid.append(grid)
            menu = grid.menu
            visual_setting = grid.visual_setting
            # menu = Image(grid, self.slider)
            # menu = TabContent(f"number {i}")

            # image = Image(grid, self.slider)
            menu_layout = QHBoxLayout()
            menu_layout.addWidget(menu)
            menu_layout.addWidget(visual_setting)
            v_main_layout = QVBoxLayout()
            v_main_layout.addLayout(menu_layout, 1)

            # LAYOUT
            h_layout = QHBoxLayout()
            grid_layout = QVBoxLayout()

            grid_layout.addWidget(grid)
            h_layout.addLayout(grid_layout, 15)

            v_layout2 = QVBoxLayout()

            v_layout2.addWidget(self.slider)
            v_layout = QVBoxLayout()
            v_layout.addWidget(post_item)
            v_layout.addWidget(joist_item)
            v_layout.addWidget(beam_item)
            v_layout.addWidget(shearWall_item)
            v_layout.addWidget(studWall_item)
            v_layout.addWidget(load_item)
            v_layout.addWidget(runButton)

            h_layout.addLayout(v_layout2, 1)
            h_layout.addLayout(v_layout, 1)

            v_main_layout.addLayout(h_layout, 25)

            tab.setLayout(v_main_layout)

        # Show the QTabWidget
        self.tabWidget.show()
        # self.tab_widget.show()

    def tabs(self):
        return [self.tabWidget.widget(i) for i in range(self.tabWidget.count())]
