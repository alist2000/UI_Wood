from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QMainWindow, QLabel, QGraphicsProxyWidget
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtCore import QRectF, Qt

from UI_Wood.stableVersion5.layout.grid import GridWidget
from UI_Wood.stableVersion5.layout.PointDraw import PointDraw
from UI_Wood.stableVersion5.layout.LineDraw import LineDraw
from UI_Wood.stableVersion5.layout.AreaDraw import AreaDraw


class secondTabWidgetLayout(QMainWindow):
    def __init__(self, inputs, ReportData):
        super().__init__()
        self.slider = None
        self.tabWidget = QTabWidget()
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

        self.setCentralWidget(self.tabWidget)
        # self.show()

        self.PostList, self.BeamList, self.JoistList, self.ShearWallList, self.StudWallList = ReportData.LayoutOutput()

        self.create_tab()

        print(inputs)

    def create_tab(self):
        for i in range(self.level_number):
            tab = QWidget()
            self.tabWidget.addTab(tab, f"Story {i + 1}")
            story = i + 1
            storyWall = i + 1
            if storyWall == self.level_number:
                storyWall = "Roof"

            # OPACITY SLIDER
            grid = GridWidget(self.h_grid_number, self.v_grid_number, self.h_spacing, self.v_spacing)

            self.grid.append(grid)
            v_main_layout = QVBoxLayout()

            # LAYOUT
            h_layout = QHBoxLayout()
            grid_layout = QVBoxLayout()

            grid_layout.addWidget(grid)
            h_layout.addLayout(grid_layout, 15)

            v_main_layout.addLayout(h_layout, 25)

            try:
                postLabels, postCoordinate = self.PostList[str(story)]["label"], self.PostList[str(story)]["coordinate"]
                # STORY NUMBER
                label = StoryLabel(i, -110)
                grid.scene.addItem(label)
                # Post Image
                PointDraw(self.PostList[str(story)], grid.scene, i)
            except KeyError:
                pass
            try:
                beamLabels, beamCoordinate = self.BeamList[str(story)]["label"], self.BeamList[str(story)]["coordinate"]
                # STORY NUMBER
                label = StoryLabel(i, -50)
                grid.scene.addItem(label)
                LineDraw(self.BeamList[str(story)], grid.scene, i, "beam")
            except KeyError:
                pass

            try:
                shearWallLabels, shearWallCoordinate = self.ShearWallList[str(storyWall)]["label"], \
                                                       self.ShearWallList[str(storyWall)]["coordinate"]
                editedLabel = []
                for label in shearWallLabels:
                    new = "SW" + label
                    editedLabel.append(new)
                # STORY NUMBER
                label = StoryLabel(i, -50)
                grid.scene.addItem(label)
                LineDraw(self.ShearWallList[str(storyWall)], grid.scene, i, "shearWall")
            except KeyError:
                pass

            try:
                studWallLabels, studWallCoordinate = self.StudWallList[str(storyWall)]["label"], \
                                                     self.StudWallList[str(storyWall)]["coordinate"]
                editedLabel = []
                for label in studWallLabels:
                    new = "ST" + label
                    editedLabel.append(new)
                # STORY NUMBER
                label = StoryLabel(i, -50)
                grid.scene.addItem(label)
                LineDraw(self.StudWallList[str(storyWall)], grid.scene, i, "studWall")
            except KeyError:
                pass

            try:
                joistLabels, joistCoordinate, joistOrientations = self.JoistList[str(story)]["label"], \
                                                                  self.JoistList[str(story)]["coordinate"], \
                                                                  self.JoistList[str(story)]["direction"]
                # STORY NUMBER
                label = StoryLabel(i, -50)
                grid.scene.addItem(label)
                AreaDraw(self.JoistList[str(story)], grid.scene, i)
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
