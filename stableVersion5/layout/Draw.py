from abc import ABC, abstractmethod


class Draw(ABC):
    @abstractmethod
    def saveImage(self):
        pass


class InputDraw:
    def __init__(self, story, x_grid, y_grid, opacity, imagePath, reportTypes):
        self.properties = None
        self.scene = None
        self.story = story
        self.x_grid = x_grid
        self.y_grid = y_grid
        self.opacity = opacity
        self.imagePath = imagePath
        self.reportTypes = reportTypes
        self.lineType = None

    def get_scene(self, scene):
        self.scene = scene

    def get_prob(self, properties):
        self.properties = properties

    def get_line_type(self, lineType):
        self.lineType = lineType
