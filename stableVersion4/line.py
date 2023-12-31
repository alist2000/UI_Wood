from UI_Wood.stableVersion4.post_new import magnification_factor

from PySide6.QtCore import Qt
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QGraphicsLineItem


class LineHandler:
    def __init__(self, x_prop, y_prop, base):
        """
        The function initializes a LineProp object based on the given base and sets the x_prop and y_prop attributes based
        on the controlStartEnd method of the LineProp object.

        :param x_prop: The x_prop parameter represents the x-coordinate property of the line. It could be the starting
        x-coordinate or the spacing between each point on the line, depending on the base parameter
        :param y_prop: The `y_prop` parameter represents the y-coordinate property of a line. It is used to specify the
        y-coordinate value for the line's start and end points
        :param base: The "base" parameter is used to determine the type of base for the line. It can have two possible
        values: "coordinate" or "spacing"
        """
        if base == "coordinate":
            self.line = LineProp()
            self.line.CoordinateBase(x_prop, y_prop)
        elif base == "spacing":
            self.line = LineProp()
            self.line.SpacingBase(x_prop, y_prop)

        self.x_prop, self.y_prop = self.line.controlStartEnd()


class LineDrawHandler:
    def __init__(self, x_prop, y_prop, scene, snapLine, snapPoint, base):
        """
        The function initializes a LineHandler object and a DrawLine object, and then draws lines based on the x_prop and
        y_prop properties.

        :param x_prop: The `x_prop` parameter is a property that represents the x-coordinate of a line. It is used in the
        `LineHandler` class to handle the logic related to the x-coordinate of the line
        :param y_prop: The `y_prop` parameter is a property that represents the y-coordinate of a line. It is used in the
        `LineHandler` class to handle the line's y-coordinate
        :param scene: The "scene" parameter is a reference to the scene or canvas where the lines will be drawn. It could be
        a graphical user interface (GUI) window or a drawing board
        :param snapLine: The "snapLine" parameter is a reference to a line that is used for snapping or aligning other
        objects. It is likely used in the "DrawLine" class to determine the position of the drawn lines relative to this
        snap line
        :param base: drawing line could be based on spacing or coordinate, this parameter represents the type of base
        """
        self.line = LineHandler(x_prop, y_prop, base)
        self.x_prop = self.line.x_prop
        self.y_prop = self.line.y_prop
        self.scene = scene
        self.snapLine = snapLine
        self.drawLine = DrawLine(scene, snapLine)

        self.drawLine.Draw(self.x_prop, "x")
        self.drawLine.Draw(self.y_prop, "y")
        # snap point control
        self.drawLine.SnapPointHandler(self.x_prop, self.y_prop, snapPoint)

    def output(self):
        return self.drawLine.lineLabels, self.drawLine.boundaryLineLabels


class LineProp:
    def __init__(self):
        """
        The above code defines a class with methods for converting spacing values to coordinate values.
        """
        self.x_prop = None
        self.y_prop = None

    def CoordinateBase(self, x_prop, y_prop):
        '''
        x_prop: [{label, position(y), start(x1), end(x2)}]
        y_prop: [{label, position(x), start(y1), end(y2)}]
        '''
        x = [i["position"] for i in x_prop]
        y = [i["position"] for i in y_prop]
        x, y = self.control_inputs(x, y)
        self.x_prop = self.convert_spacing_to_coordinate(x_prop, x)
        self.y_prop = self.convert_spacing_to_coordinate(y_prop, y)

    def SpacingBase(self, x_prop, y_prop):
        '''
        x_prop: [{label, spacing, start(x1), end(x2)}]
        y_prop: [{label, spacing, start(y1), end(y2)}]
        '''

        x = [i["spacing"] for i in x_prop]
        y = [i["spacing"] for i in y_prop]
        x, y = self.edit_spacing(x, y)
        x, y = self.control_inputs(x, y)
        self.x_prop = self.convert_spacing_to_coordinate(x_prop, x)
        self.y_prop = self.convert_spacing_to_coordinate(y_prop, y)

    def controlStartEnd(self):
        """
        The function `controlStartEnd` sets default values for the "start" and "end" properties in the `x_prop` and `y_prop`
        lists if they are not already defined.
        :return: the updated x_prop and y_prop dictionaries.
        """
        startDefaultX = 0
        endDefaultY = max([i["position"] for i in self.x_prop])
        startDefaultY = 0
        endDefaultX = max([i["position"] for i in self.y_prop])
        for x in self.x_prop:
            if not x["start"]:
                x["start"] = startDefaultX
            if not x["end"]:
                x["end"] = endDefaultX
        for y in self.y_prop:
            if not y["start"]:
                y["start"] = startDefaultY
            if not y["end"]:
                y["end"] = endDefaultY
        return self.x_prop, self.y_prop

    @staticmethod
    def convert_spacing_to_coordinate(prop, coordinate):
        newProp = []
        for i, item in enumerate(prop):
            newProp.append({
                "label": item["label"],
                "position": coordinate[i],
                "start": item["start"] * magnification_factor,
                "end": item["end"] * magnification_factor
            })
        return newProp

    @staticmethod
    def edit_spacing(x, y):
        x_list = [0]
        y_list = [0]
        for i in range(len(x)):
            x_list.append(sum(x[:i + 1]))
        for i in range(len(y)):
            y_list.append(sum(y[:i + 1]))
        return x_list, y_list

    @staticmethod
    def control_inputs(x, y):
        if x:
            # better appearance
            x = [i * magnification_factor for i in x]
        else:
            x = [400]  # 20 ft or 20 m
        if y:
            # better appearance
            y = [i * magnification_factor for i in y]
        else:
            y = [400]  # 20 ft or 20 m

        return x, y


class DrawLine:
    def __init__(self, scene, snapLines):
        self.scene = scene
        self.snapLine = snapLines
        self.boundaryLineLabels = []
        self.lineLabels = []

    def Draw(self, prop, x_or_y):
        """
        The Draw function adds selectable lines to a scene based on the given properties and orientation, and also updates
        the boundary line labels.

        :param prop: The "prop" parameter is a list of dictionaries. Each dictionary represents a line and contains the
        following keys:
        :param x_or_y: The parameter "x_or_y" is used to determine whether to draw horizontal lines ("x") or vertical lines
        ("y")
        """
        labelInOneSide = []
        positionInOneSide = []
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        for i in range(len(prop)):
            if x_or_y == "x":
                line = SelectableLineItem(prop[i]["start"], prop[i]["position"], prop[i]["end"],
                                          prop[i]["position"])  # horizontal line
                # snap
                self.snapLine.add_line((prop[i]["start"], prop[i]["position"]), (prop[i]["end"], prop[i]["position"]))
            else:
                line = SelectableLineItem(prop[i]["position"], prop[i]["start"], prop[i]["position"],
                                          prop[i]["end"])  # vertical line
                # snap
                self.snapLine.add_line((prop[i]["position"], prop[i]["start"]), (prop[i]["position"], prop[i]["end"]))

            line.setPen(pen)
            self.scene.addItem(line)
            self.lineLabels.append(prop[i]["label"])
            positionInOneSide.append(prop[i]["position"])
            labelInOneSide.append(prop[i]["label"])
        firstLineCoordinateIndex = positionInOneSide.index(min(positionInOneSide))
        firstLine = labelInOneSide[firstLineCoordinateIndex]
        lastLineCoordinateIndex = positionInOneSide.index(max(positionInOneSide))
        lastLine = labelInOneSide[lastLineCoordinateIndex]
        self.boundaryLineLabels.extend([firstLine, lastLine])

    @staticmethod
    def SnapPointHandler(x_prop, y_prop, snapPoint):
        # snap point
        for x in y_prop:  # position of y grid is in x direct
            for y in x_prop:  # position of  grid is in y direct
                snapPoint.add_point(x["position"], y["position"])

        for y1 in y_prop:  # position of y grid is in x direct
            snapPoint.add_point(y1["position"], y1["start"])
            snapPoint.add_point(y1["position"], y1["end"])
        for x1 in x_prop:  # position of y grid is in x direct
            snapPoint.add_point(x1["start"], x1["position"])
            snapPoint.add_point(x1["end"], x1["position"])


class SelectableLineItem(QGraphicsLineItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mouseMoveEvent(self, event):
        if self.isSelected():
            self.setPen(QPen(Qt.blue, 2, Qt.SolidLine))  # Set pen on the SelectableLineItem object
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setSelected(False)
            self.setPen(QPen(Qt.black, 1, Qt.SolidLine))  # Set pen on the SelectableLineItem object
        super().mouseReleaseEvent(event)
