from PySide6.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QFileDialog
import json
import sys

from tab_widget_2 import secondTabWidget


class Load:
    def __init__(self, mainPage):
        self.mainPage = mainPage
        self.data = None
        self.tabWidget = None

    def load_control(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self.mainPage, "QFileDialog.getOpenFileName()", "",
                                                  'JSON Files (*.json)', options=options)
        if fileName:
            with open(fileName, 'r') as f:
                self.data = json.load(f)

            self.create_main_tab()
            drawing(self.data, self.tabWidget.grid)
            set_toolBar(self.data, self.tabWidget.toolBar)

    def create_main_tab(self):
        general_properties = self.data["general_properties"]
        self.tabWidget = secondTabWidget(general_properties)


class drawing:
    def __init__(self, inputs, grids):
        self.tabData = inputs["tab"]
        self.grid = grids
        for i in range(len(grids)):
            grid = grids[i]
            tabData = self.tabData[str(i)]
            self.draw_post(grid, tabData)
            self.draw_beam(grid, tabData)
            self.draw_joist(grid, tabData)
            self.draw_shearWall(grid, tabData)
            self.draw_studWall(grid, tabData)
            self.draw_loadMap(grid, tabData)

    @staticmethod
    def draw_post(grid, data):
        for post in data["post"]:
            grid.post_instance.draw_post_mousePress(None, None, post)

    @staticmethod
    def draw_beam(grid, data):
        for beam in data["beam"]:
            grid.beam_instance.draw_beam_mousePress(None, None, beam)

    @staticmethod
    def draw_joist(grid, data):
        for joist in data["joist"]:
            grid.joist_instance.draw_joist_mousePress(None, None, joist)

    @staticmethod
    def draw_shearWall(grid, data):
        for shearWall in data["shearWall"]:
            grid.shearWall_instance.draw_shearWall_mousePress(None, None, shearWall)

    @staticmethod
    def draw_studWall(grid, data):
        for studWall in data["studWall"]:
            grid.studWall_instance.draw_studWall_mousePress(None, None, studWall["coordinate"])

    @staticmethod
    def draw_loadMap(grid, data):
        for loadMap in data["loadMap"]:
            grid.load_instance.draw_load_mousePress(None, None, loadMap)


class set_toolBar:
    def __init__(self, inputs, toolBar):
        self.toolBar = toolBar
        self.seismic_parameters = inputs["seismic_parameters"]
        self.load_set = inputs["load_set"]
        self.set_seismic_parameters()
        self.set_load_sets()

    def set_seismic_parameters(self):
        self.toolBar.spin_values = []
        for i, item in enumerate(self.seismic_parameters.values()):
            if i <= 6:
                self.toolBar.spin_values.append(item)
            else:
                self.toolBar.combo_values = [item]

    def set_load_sets(self):
        for name, properties in self.load_set.items():
            load_data = {"name": name, "properties": properties}
            self.toolBar.dialogPage2.all_set_load[load_data["name"]] = load_data["properties"]
            item = QListWidgetItem(load_data["name"])
            self.toolBar.dialogPage2.listWidget.addItem(item)
