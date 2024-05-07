from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QMainWindow, QLabel, QGraphicsProxyWidget

from UI_Wood.stableVersion5.layout.grid import GridWidget
from UI_Wood.stableVersion5.layout.PointDraw import PointDraw
from UI_Wood.stableVersion5.layout.LineDraw import LineDraw
from UI_Wood.stableVersion5.layout.AreaDraw import AreaDraw
from UI_Wood.stableVersion5.layout.Draw import InputDraw


class secondTabWidgetLayout(QMainWindow):
    def __init__(self, inputs):
        super().__init__()
        self.slider = None
        self.tabWidget = QTabWidget()
        self.grid = []
        self.inputs = inputs
        self.x_grid = inputs.get("x_grid")
        self.y_grid = inputs.get("y_grid")
        self.grid_base = inputs.get("grid_base")
        self.level_number = inputs.get("level_number")
        self.height_story = inputs.get("height_story")
        self.setWindowTitle("Grid")
        self.tabWidget.setMinimumSize(600, 500)

        self.setCentralWidget(self.tabWidget)
        # self.show()

        # self.PostList, self.BeamList, self.JoistList, self.ShearWallList, self.StudWallList = ReportData.LayoutOutput()
        #
        # self.create_tab()

        print(inputs)

    def create_tab(self, PostList, BeamList, JoistList, ShearWallList, StudWallList, opacity, imagePath, reportTypes):
        for i in range(self.level_number):
            tab = QWidget()
            self.tabWidget.addTab(tab, f"Story {i + 1}")
            story = i + 1
            storyWall = i + 1
            if storyWall == self.level_number:
                storyWall = "Roof"

            # OPACITY SLIDER
            grid = GridWidget(self.x_grid, self.y_grid, self.grid_base)

            # constant input data
            inputDraw = InputDraw(grid.scene, i, grid.x_grid, grid.y_grid, opacity[i], imagePath[i], reportTypes)

            self.grid.append(grid)
            v_main_layout = QVBoxLayout()

            # LAYOUT
            h_layout = QHBoxLayout()
            grid_layout = QVBoxLayout()

            grid_layout.addWidget(grid)
            h_layout.addLayout(grid_layout, 15)

            v_main_layout.addLayout(h_layout, 25)

            try:
                postLabels, postCoordinate = PostList[str(story)]["label"], PostList[str(story)]["coordinate"]
                # STORY NUMBER
                label = StoryLabel(i, -110)
                grid.scene.addItem(label)
                inputDraw.get_prob(PostList[str(story)])
                # Post Image
                PointDraw(inputDraw)
            except KeyError:
                pass
            try:

                beamLabels, beamCoordinate = BeamList[str(story)]["label"], BeamList[str(story)]["coordinate"]
                # STORY NUMBER
                label = StoryLabel(i, -50)
                grid = GridWidget(self.x_grid, self.y_grid, self.grid_base)
                grid.scene.addItem(label)
                inputDraw.get_prob(BeamList[str(story)])
                inputDraw.get_line_type("beam")
                LineDraw(inputDraw)
            except KeyError:
                pass

            try:
                shearWallLabels, shearWallCoordinate = ShearWallList[str(storyWall)]["label"], \
                                                       ShearWallList[str(storyWall)]["coordinate"]
                editedLabel = []
                for label in shearWallLabels:
                    new = "SW" + label
                    editedLabel.append(new)
                # STORY NUMBER
                label = StoryLabel(i, -50)
                grid = GridWidget(self.x_grid, self.y_grid, self.grid_base)
                grid.scene.addItem(label)
                inputDraw.get_prob(ShearWallList[str(storyWall)])
                inputDraw.get_line_type("shearWall")
                LineDraw(inputDraw)
            except KeyError:
                pass

            try:
                studWallLabels, studWallCoordinate = StudWallList[str(storyWall)]["label"], \
                                                     StudWallList[str(storyWall)]["coordinate"]
                editedLabel = []
                for label in studWallLabels:
                    new = "ST" + label
                    editedLabel.append(new)
                # STORY NUMBER
                label = StoryLabel(i, -50)
                grid = GridWidget(self.x_grid, self.y_grid, self.grid_base)
                grid.scene.addItem(label)
                inputDraw.get_prob(StudWallList[str(storyWall)])
                inputDraw.get_line_type("studWall")
                LineDraw(inputDraw)

            except KeyError:
                pass

            try:
                joistLabels, joistCoordinate, joistOrientations = JoistList[str(story)]["label"], \
                                                                  JoistList[str(story)]["coordinate"], \
                                                                  JoistList[str(story)]["direction"]
                # STORY NUMBER
                label = StoryLabel(i, -50)
                grid = GridWidget(self.x_grid, self.y_grid, self.grid_base)
                grid.scene.addItem(label)
                inputDraw.get_prob(JoistList[str(story)])
                AreaDraw(inputDraw)
            except KeyError:
                pass

    def tabs(self):
        return [self.tabWidget.widget(i) for i in range(self.tabWidget.count())]


def StoryLabel(i, pos=-100):
    label = QLabel(f"Story{i + 1}")
    label.setStyleSheet("QLabel { background-color : rgba(255, 255, 255, 0); color : black; font-size:20px;}")
    labelProxy = QGraphicsProxyWidget()

    labelProxy.setWidget(label)
    labelProxy.setPos(0, pos)
    return labelProxy
