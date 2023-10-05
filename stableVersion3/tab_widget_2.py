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
from back.check_model import checkModel
from Sync.mainSync import mainSync
from Sync.mainSync2 import mainSync2
from InformationSaver import InformationSaver
from UI_Wood.stableVersion3.run.grid import GridDraw


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
        self.setWindowTitle("Grid")

        self.tabWidget.setMinimumSize(600, 500)
        GridDrawClass = GridDraw(self.h_grid_number, self.v_grid_number, self.h_spacing,
                                 self.v_spacing)
        # INFORMATION PROPERTIES
        self.information_properties = information_properties()

        self.setCentralWidget(self.tabWidget)
        self.toolBar = ToolBar(self)
        self.checkModel = checkModel(self.toolBar.savePage.save_data, self.grid, self.level_number)
        self.mainSync = mainSync(self.toolBar.savePage.save_data, self.grid, self.level_number)
        self.mainSync2 = mainSync2(self.toolBar.savePage.save_data, self.grid, self.level_number,
                                   GridDrawClass)

        self.toolBar.savePage.add_subscriber(self.mainSync)
        self.toolBar.savePage.add_subscriber(self.mainSync2)
        self.toolBar.savePage.add_subscriber(self.checkModel)
        self.show()

        self.create_tab()

        print(inputs)

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
            # runButton = QPushButton("RUN")

            # ADD GRID LINES
            grid = GridWidget(self.h_grid_number, self.v_grid_number, self.h_spacing, self.v_spacing, post_instance,
                              joist_instance, beam_instance, shearWall_instance, studWall_instance,
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
            # v_layout.addWidget(runButton)

            h_layout.addLayout(v_layout2, 1)
            h_layout.addLayout(v_layout, 1)

            v_main_layout.addLayout(h_layout, 25)

            tab.setLayout(v_main_layout)

        tool_bar = QToolBar("RunToolBar")
        self.addToolBar(tool_bar)
        report_generator = QAction('Report Generator', self)
        report_generator.setEnabled(False)
        self.mainSync.send_report_generator(report_generator)
        self.mainSync2.send_report_generator(report_generator)


        run = QAction('RUN', self)
        check_model = QAction('Check Model', self)
        run.triggered.connect(self.mainSync.Run_and_Analysis)
        check_model.triggered.connect(self.checkModel.check_model_run)

        tool_bar.addAction(check_model)
        tool_bar.addAction(run)
        tool_bar.addAction(report_generator)

        # Run element by element.
        self.addToolBarBreak(Qt.TopToolBarArea)  # or self.addToolBarBreak()
        JoistRun = QAction('JOIST RUN', self)
        BeamRun = QAction('BEAM RUN', self)
        PostRun = QAction('POST RUN', self)
        ShearWallRun = QAction('SHEAR WALL RUN', self)
        StudWallRun = QAction('STUD WALL RUN', self)
        PostRun.triggered.connect(self.mainSync2.Run_and_Analysis_Post)
        BeamRun.triggered.connect(self.mainSync2.Run_and_Analysis_Beam)
        JoistRun.triggered.connect(self.mainSync2.Run_and_Analysis_Joist)
        ShearWallRun.triggered.connect(self.mainSync2.Run_and_Analysis_ShearWall)
        StudWallRun.triggered.connect(self.mainSync2.Run_and_Analysis_StudWall)
        tool_bar2 = QToolBar("RunToolBar2")
        self.addToolBar(tool_bar2)

        tool_bar2.addAction(JoistRun)
        tool_bar2.addAction(BeamRun)
        tool_bar2.addAction(PostRun)
        tool_bar2.addAction(ShearWallRun)
        tool_bar2.addAction(StudWallRun)

        # Show the QTabWidget
        self.tabWidget.show()

    def tabs(self):
        return [self.tabWidget.widget(i) for i in range(self.tabWidget.count())]


def information_properties():
    information_prop = {"project_name": InformationSaver.line_edit_projectTitle.text(),
                        "company": InformationSaver.line_edit_company.text(),
                        "designer": InformationSaver.line_edit_designer.text(),
                        "client": InformationSaver.line_edit_client.text(),
                        "comment": InformationSaver.line_edit_comment.text(),
                        "unit_system": InformationSaver.unit_combo.currentText().upper()}
    return information_prop
