from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSpinBox, QDoubleSpinBox, QLabel, QPushButton, \
    QTabWidget
from tab_widget_2 import secondTabWidget


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

        # REPORT INPUTS
        self.reportInputs = reportInputs

        # for new tab
        self.new_window = None

        self.setMinimumSize(600, 500)

        # level number
        levelLabel = QLabel("Number of Level :")
        levelLabel.setFixedWidth(150)
        self.level = level = QSpinBox()
        level.setRange(1, 100)
        level.setFixedHeight(30)
        h_l1 = h_layout_control(levelLabel, level)

        self.height_story_layout = height_story_layout = QVBoxLayout()
        level.valueChanged.connect(self.story_height_control)

        # Grid numbers
        h_gridLabel = QLabel("Horizontal Grid Number :")
        h_gridLabel.setFixedWidth(200)
        self.h_grid = h_grid = QSpinBox()
        h_grid.setRange(2, 100)
        h_grid.setFixedHeight(30)

        v_gridLabel = QLabel("Vertical Grid Number :")
        v_gridLabel.setFixedWidth(200)
        self.v_grid = v_grid = QSpinBox()
        v_grid.setRange(2, 100)
        v_grid.setFixedHeight(30)

        # RUN Button
        self.height_story = []
        self.h_spacing_list = []
        self.v_spacing_list = []
        run = QPushButton("SUBMIT")
        run.clicked.connect(self.run_control)

        h_l2 = h_layout_control(h_gridLabel, h_grid, v_gridLabel, v_grid)

        grid_spacing_layout = QHBoxLayout()
        self.h_grid_spacing_layout = h_grid_spacing_layout = QVBoxLayout()
        self.v_grid_spacing_layout = v_grid_spacing_layout = QVBoxLayout()
        h_grid.valueChanged.connect(self.h_grid_control)
        v_grid.valueChanged.connect(self.v_grid_control)
        grid_spacing_layout.addLayout(h_grid_spacing_layout)
        grid_spacing_layout.addLayout(v_grid_spacing_layout)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_l1)
        v_layout.addLayout(height_story_layout)

        v_layout.addLayout(h_l2)
        v_layout.addLayout(grid_spacing_layout)
        v_layout.addWidget(run)
        self.setLayout(v_layout)

    # SLOT FUNCTION
    def story_height_control(self):
        v_layout = self.height_story_layout
        clear_layout(v_layout)
        level_number = self.level.value()
        v_layout_control(v_layout, level_number, 4, "Height")

    # SLOT FUNCTION
    def h_grid_control(self):
        v_layout = self.h_grid_spacing_layout
        clear_layout(v_layout)
        label = QLabel("Horizontal Grid Spacing")
        label.setFixedHeight(20)
        grid_number = self.h_grid.value()
        v_layout_control(v_layout, grid_number, 2, "H Spacing", label)

    # SLOT FUNCTION
    def v_grid_control(self):
        v_layout = self.v_grid_spacing_layout
        clear_layout(v_layout)
        label = QLabel("Vertical Grid Spacing")
        label.setFixedHeight(20)
        grid_number = self.v_grid.value()
        v_layout_control(v_layout, grid_number, 2, "V Spacing", label)

    # SLOT FUNCTION
    def run_control(self):
        height_story = self.height_story
        h_spacing = self.h_spacing_list
        v_spacing = self.v_spacing_list
        height_story.clear()
        h_spacing.clear()
        v_spacing.clear()
        print("run")
        self.level_final = level = self.level.value()
        self.h_grid_number_final = h_grid_number = self.h_grid.value()
        self.v_grid_number_final = v_grid_number = self.v_grid.value()

        self.h_spacing_final = h_spacing = spacing_reader(self.h_grid_spacing_layout, h_spacing)
        self.v_spacing_final = v_spacing = spacing_reader(self.v_grid_spacing_layout, v_spacing)
        self.height_story_final = height_story = spacing_reader(self.height_story_layout, height_story)

        self.new_window = secondTabWidget(self.result())

        # REPORT INPUTS
        self.reportInputs.General_prop(self.result())

    def result(self):
        Result = {"level_number": self.level_final, "h_grid_number": self.h_grid_number_final,
                  "v_grid_number": self.v_grid_number_final,
                  "height_story": self.height_story_final, "h_spacing": self.h_spacing_final,
                  "v_spacing": self.v_spacing_final}
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
        h.setRange(0.1, 1000)
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
