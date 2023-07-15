import json
from PySide6.QtWidgets import QFileDialog, QLabel, QColorDialog, QSpinBox, QDoubleSpinBox, QComboBox, QVBoxLayout, \
    QHBoxLayout, QDialog


# MUST BE DEVELOPED . . .


class Shape:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_dict(self):
        return {'x': self.x, 'y': self.y}

    @classmethod
    def from_dict(cls, data):
        return cls(data['x'], data['y'])

    # MUST BE DEVELOPED FOR ALL SHAPE TYPES.


def save_tabs(self):
    data = []
    for tab in self.tabs():
        tab_data = {
            'shapes': [shape.to_dict() for shape in tab.shapes],
        }
        data.append(tab_data)

    with open('tabs.json', 'w') as f:
        json.dump(data, f)


def load_tabs(self):
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                              "All Files (*);;Python Files (*.py)", options=options)
    if fileName:
        with open(fileName, 'r') as f:
            data = json.load(f)

        for i, tab_data in enumerate(data):
            tab = self.tabs()[i]
            for shape_data in tab_data['shapes']:
                shape = Shape.from_dict(shape_data)
                tab.shapes.append(shape)
                tab.draw_shape(shape)

