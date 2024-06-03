import copy

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDoubleSpinBox, QLabel, QPushButton, \
    QTextEdit, QAbstractItemView, QTableWidget, \
    QRadioButton, QSpacerItem, QGraphicsView, QGraphicsScene

from load import Load
from tab_widget_2 import secondTabWidget

from UI_Wood.stableVersion5.grid_define import GridCoordinateDefine, GridPreview, \
    StoryCoordinateDefine


class Widget_button(QWidget):
    def __init__(self, reportInputs, parent=None):
        super().__init__(parent)
        # final values
        self.level_final = None
        self.h_grid_number_final = None
        self.v_grid_number_final = None
        self.height_story_final = None
        self.h_spacing_final = None
        self.v_spacing_final = None
        self.x_grid, self.y_grid, self.grid_base = None, None, None
        self.loadInstance = Load(self)

        # REPORT INPUTS
        self.reportInputs = reportInputs

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
        run.clicked.connect(self.run_control)
        load.clicked.connect(self.loadInstance.load_control)

        v_layout = QVBoxLayout()
        v_layout.addLayout(storyHeightLayout)
        v_layout.addWidget(self.gridInstance)
        v_layout.addWidget(run)
        v_layout.addWidget(load)
        self.setLayout(v_layout)

    # SLOT FUNCTION
    def run_control(self):
        self.previewGrid.preview()
        self.x_grid, self.y_grid, self.grid_base = self.gridInstance.output()
        self.level_final, self.height_story_final = self.storyInstance.output()

        height_story = self.height_story
        height_story.clear()
        print("run")

        self.new_window = secondTabWidget(self.result())

        # REPORT INPUTS
        self.reportInputs.General_prop(self.result())

    def result(self):
        Result = {"level_number": self.level_final, "height_story": self.height_story_final,
                  "x_grid": self.x_grid,
                  "y_grid": self.y_grid,
                  "grid_base": self.grid_base}
        return Result


def h_layout_control(*args):
    h_layout = QHBoxLayout()
    for item in args:
        h_layout.addWidget(item)
    return h_layout


def v_layout_control(layout, total_number, col, item_name, label=None):
    if label:
        layout.addWidget(label)
        total_number -= 1  # we have n - 1 spacing for grids .but we have n height for levels
    item_list = []
    for i in range(total_number):
        h_label = QLabel(f"{item_name} {i + 1} :")
        h_label.setFixedWidth(75)
        h = QDoubleSpinBox()
        h.setDecimals(3)
        h.setRange(0.1, 1000)
        h.setValue(10)
        item_list.append(h_label)
        item_list.append(h)
        if ((i + 1) % col == 0) or (i == total_number - 1):
            h_layout = h_layout_control(*item_list)
            layout.addLayout(h_layout)
            item_list.clear()


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            clear_layout(item.layout())


def spacing_reader(layout, my_list):
    for i in range(layout.count()):
        h_layout = layout.itemAt(i)
        try:
            for j in range(h_layout.count()):
                widget = h_layout.itemAt(j).widget()
                if isinstance(widget, QDoubleSpinBox):
                    my_list.append(widget.value())
        except:
            pass
    return my_list
