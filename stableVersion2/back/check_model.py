import sys
from abc import ABC, abstractmethod
import itertools
from PySide6 import QtWidgets
from PySide6.QtWebEngineWidgets import QWebEngineView

sys.path.append(r"D:\git\Wood\UI_Wood\11.5")
from Sync.data import Update
from post_new import magnification_factor
from back.load_control import range_intersection


class checkModel(Update):
    def __init__(self, saveFunc, grid, tabWidgetCount):
        self.saveFunc = saveFunc
        self.grid = grid
        self.tabWidgetCount = tabWidgetCount
        self.warningPage = None

    def update(self, subject):
        self.tab = subject.data["tab"]
        self.warnings = {}
        for tabNumber, tabItems in self.tab.items():
            story = int(tabNumber) + 1
            post = tabItems["post"]
            beam = tabItems["beam"]
            shearWall = tabItems["shearWall"]
            joist = tabItems["joist"]
            studWall = tabItems["studWall"]

            # INSTABILITY CHECK
            instableCheck = Instable(beam, joist, story)

            # OVERLAP CHECK
            # Post
            postCheck = overlapPoint(post, story)
            # Beam, ShearWall, StudWall
            beamCheck = overlapLine(beam, story, "Beam")
            shearWallCheck = overlapLine(shearWall, story, "ShearWall")
            studWallCheck = overlapLine(studWall, story, "StudWall")
            # Joist
            joistCheck = overlapArea(joist, story)

            self.warnings[tabNumber] = {}
            self.warnings[tabNumber]["instability"] = instableCheck.warningList
            self.warnings[tabNumber]["overlap"] = {}
            self.warnings[tabNumber]["overlap"]["post"] = postCheck.warningList
            self.warnings[tabNumber]["overlap"]["joist"] = joistCheck.warningList
            self.warnings[tabNumber]["overlap"]["beam"] = beamCheck.warningList
            self.warnings[tabNumber]["overlap"]["shearWall"] = shearWallCheck.warningList
            self.warnings[tabNumber]["overlap"]["studWall"] = studWallCheck.warningList

    # SLOT
    def check_model_run(self):
        for currentTab in range(self.tabWidgetCount):
            self.grid[currentTab].run_control()
        self.saveFunc()
        self.warningPage = warningPage(self.warnings)
        print(self.warnings)


# INSTABILITY CHECK FOR BEAM AND JOIST
class instableWaning(ABC):
    def __init__(self):
        self.warning = None
        self.warningMessage = "No Support"

    @abstractmethod
    def controlSupport(self):
        pass


class Instable:
    def __init__(self, beams, joists, story):
        self.warningList = []
        for elements in [beams, joists]:
            for item in elements:
                itemInstable = InstableBeamJoist(item, story)
                if itemInstable.warning:
                    self.warningList.append(itemInstable.warning)


class InstableBeamJoist(instableWaning):
    def __init__(self, item, story):
        super(InstableBeamJoist, self).__init__()
        self.item = item
        self.story = story
        self.support = item["support"]
        self.controlSupport()

    def controlSupport(self):
        if "J" in self.item["label"]:
            Type = "Joist"
        else:
            Type = "Beam"
        if not self.support:
            self.warning = {
                "label": self.item["label"],
                ""
                "story": self.story,
                "warning": Type + " " + self.item["label"] + " has " + self.warningMessage
            }


# END OF INSTABILITY CHECK


# OVERLAP CHECK

class overlapWaning(ABC):
    def __init__(self):
        self.warning = None
        self.warningList = []
        self.warningMessage = "OVERLAP"

    @abstractmethod
    def selfOverlap(self):
        pass


# POST OVERLAP CHECK
class overlapPoint(overlapWaning):
    def __init__(self, post, story):
        super(overlapPoint, self).__init__()
        self.post = post
        self.story = story
        self.selfOverlap()

    def selfOverlap(self):
        coordinates = []
        full_indexes = []
        for post in self.post:
            coordinates.append(post["coordinate"])
        for coordinate in coordinates:
            indexes = get_indexes(coordinates, coordinate)
            if indexes:
                full_indexes.append(indexes)

        full_indexes = list(set(full_indexes))
        for i in full_indexes:
            self.findItems(i)

    def findItems(self, indexes):
        labels = []
        for i in indexes:
            labels.append(self.post[i]["label"])
        post_string = ""
        for label in labels:
            post_string += label
            if labels.index(label) != len(labels) - 1:
                post_string += ", "
        self.warningMessage = f"Posts, {post_string}, overlap"
        self.warning = {
            "overlap_type": "post",
            "coordinate": (self.post[indexes[0]]["coordinate"][0] / magnification_factor,
                           self.post[indexes[0]]["coordinate"][1] / magnification_factor),
            "overlap": labels,
            "story": self.story,
            "warning": self.warningMessage
        }
        self.warningList.append(self.warning)


# BEAM, SHEAR WALL, STUD WALL OVERLAP CHECK
class overlapLine(overlapWaning):
    def __init__(self, line, story, lineType):
        super(overlapLine, self).__init__()
        self.lineType = lineType
        self.line = line
        self.story = story
        self.selfOverlap()

    def selfOverlap(self):
        equal_c_index = check_equal(range(len(self.line)), self.line, "c")
        equal_c_index = list(set(equal_c_index))

        equal_c_slope_index = check_equal(range(len(self.line)), self.line, "slope")
        equal_c_slope_index = list(set(equal_c_slope_index))

        equal_c_slope_range_index = check_equal(range(len(self.line)), self.line, "range")
        equal_c_slope_range_index = list(set(equal_c_slope_range_index))

        full_indexes = itertools.product(equal_c_index, equal_c_slope_index, equal_c_slope_range_index)
        for i in full_indexes:
            equal_c = set(i[0])
            equal_slope = set(i[1])
            equal_range = set(i[2])
            all_intersection = tuple(equal_c & equal_slope & equal_range)
            if len(all_intersection) > 1:
                all_ranges = []
                for j in all_intersection:
                    all_ranges.append(self.line[j]["line"]["properties"]["range"])
                start_list = [i[0] for i in all_ranges]
                end_list = [i[1] for i in all_ranges]
                intersection_range = (max(start_list), min(end_list))
                self.findItems(all_intersection, intersection_range)

    def findItems(self, indexes, intersections):
        labels = []
        for i in indexes:
            labels.append(self.line[i]["label"])
        line_string = ""
        for label in labels:
            line_string += label
            if labels.index(label) != len(labels) - 1:
                line_string += ", "
        self.warningMessage = f"{self.lineType}, {line_string}, overlap"
        self.warning = {
            "overlap_type": f"{self.lineType}",
            "overlap_range": (intersections[0] / magnification_factor,
                              intersections[1] / magnification_factor),
            "overlap": labels,
            "story": self.story,
            "warning": self.warningMessage
        }
        self.warningList.append(self.warning)


# JOIST OVERLAP CHECK
class overlapArea(overlapWaning):
    def __init__(self, joist, story):
        super(overlapArea, self).__init__()
        self.joist = joist
        self.story = story
        self.selfOverlap()

    def selfOverlap(self):
        full_indexes_y = []
        full_indexes_x = []
        range_y = []
        range_x = []
        for joist in self.joist:
            range_y.append(joist["line"]["properties"][0]["range"])
            range_x.append(joist["line"]["properties"][1]["range"])
        for y in range_y:
            indexes_y = get_indexes_range_base(range_y, y)
            if indexes_y:
                full_indexes_y.append(indexes_y)
        full_indexes_y_set = set(full_indexes_y)
        for x in range_x:
            indexes_x = get_indexes_range_base(range_x, x)
            if indexes_x:
                full_indexes_x.append(indexes_x)
        full_indexes_x_set = set(full_indexes_x)
        full_indexes = itertools.product(full_indexes_x_set, full_indexes_y_set)
        for i in full_indexes:
            x_equal = set(i[0])
            y_equal = set(i[1])
            intersection_index = tuple(x_equal & y_equal)
            if len(intersection_index) > 1:
                self.findItems(intersection_index)


    def findItems(self, indexes):
        labels = []
        range_x = []
        range_y = []
        for i in indexes:
            labels.append(self.joist[i]["label"])
            range_x.append(self.joist[i]["line"]["properties"][1]["range"])
            range_y.append(self.joist[i]["line"]["properties"][0]["range"])
        start_x = [i[0] for i in range_x]
        end_x = [i[1] for i in range_x]
        final_range_x = (max(start_x), min(end_x))
        start_y = [i[0] for i in range_y]
        end_y = [i[1] for i in range_y]
        final_range_y = (max(start_y), min(end_y))

        line_string = ""
        for label in labels:
            line_string += label
            if labels.index(label) != len(labels) - 1:
                line_string += ", "
        self.warningMessage = f"Joists, {line_string}, overlap"
        self.warning = {
            "overlap_range_x": (final_range_x[0] / magnification_factor,
                                final_range_x[1] / magnification_factor),
            "overlap_range_y": (final_range_y[0] / magnification_factor,
                                final_range_y[1] / magnification_factor),
            "overlap": labels,
            "story": self.story,
            "warning": self.warningMessage
        }
        self.warningList.append(self.warning)


def get_indexes(input_list, target):
    indexes = [index for index, item in enumerate(input_list) if item == target]
    if len(indexes) > 1:
        return tuple(indexes)
    else:
        return []


def get_indexes_range_base(input_list, target):
    indexes = []
    for index, item in enumerate(input_list):
        intersection = range_intersection(item, target)
        if intersection:
            indexes.append(index)
            target = intersection
    if len(indexes) > 1:
        return tuple(indexes)
    else:
        return []


def check_equal(indexList, mainList, checkBase):
    """
    :param indexList:
    :param mainList:
    :param checkBase: could be range, c, slope
    :return:  indexes are equal
    """
    controlList = []
    full_indexes = []
    for i in indexList:
        controlList.append(mainList[i]["line"]["properties"][f"{checkBase}"])

    if checkBase == "range":
        for item in controlList:
            indexes = get_indexes_range_base(controlList, item)
            if indexes:
                full_indexes.append(indexes)
    else:

        for item in controlList:
            indexes = get_indexes(controlList, item)
            if indexes:
                full_indexes.append(indexes)
    return full_indexes


class warningPage(QtWidgets.QMainWindow):
    def __init__(self, warnings):
        super().__init__()
        self.warnings = warnings

        self.setWindowTitle("Warning")

        # Create QTextBrowser widget
        self.browser = QWebEngineView()
        mainText = """<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Title</title>
                </head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                    }
                
                    input[type="checkbox"] {
                        margin-left: 10px;
                        width: 15px;
                        height: 15px;
                    }
                
                </style>
                <script>
                    function toggleList(listId) {
                        var list = document.getElementById(listId);
                        if (list.style.display === "none") {
                            list.style.display = "block";
                        } else {
                            list.style.display = "none";
                        }
                    }
                </script>
            <body>
            """
        listText = ""
        for i, item in warnings.items():
            text = self.storyWarnings(item, int(i + 1))
            listText += text

        html = mainText + listText + """</body></html>"""

        # Create QPushButton and connect it to the close method
        self.button = QtWidgets.QPushButton("OK")
        self.button.clicked.connect(self.close)

        # Create a QVBoxLayout to hold the QTextBrowser and QPushButton
        self.layout = QtWidgets.QVBoxLayout()

        # Add QTextBrowser and QPushButton to the QVBoxLayout
        self.layout.addWidget(self.browser)
        self.layout.addWidget(self.button)

        self.window = QtWidgets.QWidget()
        self.window.setLayout(self.layout)

        # Set the HTML content to the QTextBrowser widget
        self.browser.setHtml(html)

        # Set the QVBoxLayout as the central widget of the QMainWindow
        self.setCentralWidget(self.window)
        self.browser.show()
        self.show()

    @staticmethod
    def storyWarnings(story_warning, story_number):
        instability = story_warning["instability"]
        overlap = story_warning["overlap"]
        header = f"""<h2><input type="checkbox" checked onclick="toggleList('list{str(story_number)}Items')"> Story {str(story_number)} </h2><ul id="list{str(story_number)}Items" class="warningList">"""

        instability_error_text = ""
        overlap_error_text = ""

        for item in instability:
            text = item["warning"]
            instability_error_text += f"""
                                    <li style="list-style: linear-gradient(rgb(253, 46, 46), rgb(253, 46, 46), rgb(253, 46, 46), rgb(253, 46, 46), white);">{text}</li>"""

        for item in overlap.values():
            for detail in item:
                text = detail["warning"]
                overlap_error_text += f"""
                                    <li style="list-style: linear-gradient(rgb(242, 146, 29),rgb(242, 146, 29), rgb(242, 146, 29), rgb(242, 146, 29), white);">{text}</li>"""

        if not instability_error_text and not overlap_error_text:
            instability_error_text = "No Warning!"

        finalText = header + instability_error_text + overlap_error_text + """</ul> """
        return finalText
# beams = [{'label': 'B2', 'coordinate': [(221.0, 70.0), (76.0, 70.0)],
#           'load': {'point': [], 'line': [], 'joist_load': {'assignment': [], 'load_map': []}}, 'length': 145.0,
#           'line': {'properties': {'slope': True, 'c': 70.0, 'range': (76.0, 221.0)}}, 'direction': 'E-W',
#           'support': [{'label': 'P1', 'type': 'post', 'coordinate': (221.0, 70.0), 'range': 'start'}],
#           'joist': [{'label': 'J1', 'intersection_range': (76.0, 216.0), 'tributary_depth': (70.0, 110.0)}]},
#          {'label': 'B3', 'coordinate': [(76.0, 70.0), (76.0, 0.0)],
#           'load': {'point': [], 'line': [], 'joist_load': {'assignment': [], 'load_map': []}}, 'length': 70.0,
#           'line': {'properties': {'slope': False, 'c': 76.0, 'range': (0.0, 70.0)}}, 'direction': 'N-S',
#           'support': [{'label': 'B2', 'type': 'beam_end_support', 'coordinate': (76.0, 70.0), 'range': 'start'}],
#           'joist': []},
#          {'label': 'B4', 'coordinate': [(76.0, 70.0), (76.0, 335.0)],
#           'load': {'point': [], 'line': [], 'joist_load': {'assignment': [], 'load_map': []}},
#           'length': 265.0, 'line': {'properties': {'slope': False, 'c': 76.0, 'range': (70.0, 335.0)}},
#           'direction': 'N-S', 'support': [
#              {'label': 'B2', 'type': 'beam_end_support', 'coordinate': (76.0, 70.0), 'range': 'start'},
#              {'label': 'B3', 'type': 'beam_start_support', 'coordinate': (76.0, 70.0), 'range': 'start'}], 'joist': [
#              {'label': 'J1', 'intersection_range': (70.0, 274.0), 'tributary_depth': (76.0, 146.0)},
#              {'label': 'J2', 'intersection_range': (274.0, 335.0), 'tributary_depth': (76.0, 116.0)}]},
#          {'label': 'B5', 'coordinate': [(344.0, 70.0), (344.0, 192.0)],
#           'load': {'point': [], 'line': [], 'joist_load': {'assignment': [], 'load_map': []}}, 'length': 122.0,
#           'line': {'properties': {'slope': False, 'c': 344.0, 'range': (70.0, 192.0)}}, 'direction': 'N-S',
#           'support': [], 'joist': []},
#          {'label': 'B6', 'coordinate': [(344.0, 169.0), (344.0, 105.0)],
#           'load': {'point': [], 'line': [], 'joist_load': {'assignment': [], 'load_map': []}}, 'length': 64.0,
#           'line': {'properties': {'slope': False, 'c': 344.0, 'range': (105.0, 169.0)}}, 'direction': 'N-S',
#           'support': [{'label': 'B5', 'type': 'beam_mid_support', 'coordinate': (344.0, 169.0), 'range': 'start'},
#                       {'label': 'B5', 'type': 'beam_mid_support', 'coordinate': (344.0, 105.0), 'range': 'end'}],
#           'joist': []},
#          {'label': 'B7', 'coordinate': [(76.0, 213.0), (261.0, 213.0)],
#           'load': {'point': [], 'line': [], 'joist_load': {'assignment': [], 'load_map': []}}, 'length': 185.0,
#           'line': {'properties': {'slope': True, 'c': 213.0, 'range': (76.0, 261.0)}}, 'direction': 'E-W',
#           'support': [{'label': 'B4', 'type': 'beam_mid_support', 'coordinate': (76.0, 213.0), 'range': 'start'}],
#           'joist': []},
#          {'label': 'B8', 'coordinate': [(144.0, 213.0), (144.0, 25.0)],
#           'load': {'point': [], 'line': [], 'joist_load': {'assignment': [], 'load_map': []}}, 'length': 188.0,
#           'line': {'properties': {'slope': False, 'c': 144.0, 'range': (25.0, 213.0)}}, 'direction': 'N-S',
#           'support': [{'label': 'B7', 'type': 'beam_mid_support', 'coordinate': (144.0, 213.0), 'range': 'start'}],
#           'joist': []}
#
#          ]
#
# joists = [
#     {'label': 'J1', 'coordinate': [(76.0, 70.0), (76.0, 274.0), (216.0, 274.0), (216.0, 70.0)], 'direction': 'E-W',
#      'load': {'total_area': [], 'custom_area': [], 'load_map': []}, 'line': {
#         'point': [((76.0, 70.0), (76.0, 274.0)), ((76.0, 274.0), (216.0, 274.0)), ((216.0, 274.0), (216.0, 70.0)),
#                   ((216.0, 70.0), (76.0, 70.0))], 'properties': [{'slope': False, 'c': 76.0, 'range': (70.0, 274.0)},
#                                                                  {'slope': True, 'c': 274.0, 'range': (76.0, 216.0)},
#                                                                  {'slope': False, 'c': 216.0, 'range': (70.0, 274.0)},
#                                                                  {'slope': True, 'c': 70.0, 'range': (76.0, 216.0)}]},
#      'support': [{'label': 'B4', 'type': 'beam', 'intersection_range': (70.0, 274.0)}]},
#     {'label': 'J2', 'coordinate': [(76.0, 274.0), (76.0, 363.0), (253.0, 363.0), (253.0, 274.0)], 'direction': 'N-S',
#      'load': {'total_area': [], 'custom_area': [], 'load_map': []}, 'line': {
#         'point': [((76.0, 274.0), (76.0, 363.0)), ((76.0, 363.0), (253.0, 363.0)), ((253.0, 363.0), (253.0, 274.0)),
#                   ((253.0, 274.0), (76.0, 274.0))], 'properties': [{'slope': False, 'c': 76.0, 'range': (274.0, 363.0)},
#                                                                    {'slope': True, 'c': 363.0, 'range': (76.0, 253.0)},
#                                                                    {'slope': False, 'c': 253.0,
#                                                                     'range': (274.0, 363.0)},
#                                                                    {'slope': True, 'c': 274.0,
#                                                                     'range': (76.0, 253.0)}]}, 'support': []},
#     {'label': 'J3', 'coordinate': [(287.0, 229.0), (287.0, 303.0), (380.0, 303.0), (380.0, 229.0)], 'direction': 'N-S',
#      'load': {'total_area': [], 'custom_area': [], 'load_map': []}, 'line': {
#         'point': [((287.0, 229.0), (287.0, 303.0)), ((287.0, 303.0), (380.0, 303.0)), ((380.0, 303.0), (380.0, 229.0)),
#                   ((380.0, 229.0), (287.0, 229.0))],
#         'properties': [{'slope': False, 'c': 287.0, 'range': (229.0, 303.0)},
#                        {'slope': True, 'c': 303.0, 'range': (287.0, 380.0)},
#                        {'slope': False, 'c': 380.0, 'range': (229.0, 303.0)},
#                        {'slope': True, 'c': 229.0, 'range': (287.0, 380.0)}]}, 'support': []}]
# joists2 = {"<joist_new.joistRectangle(0x1ff456a4f60, pos=0,0) at 0x000001FF4803C400>": {'label': 'J1',
#                                                                                         'coordinate': [(207.0, 131.0),
#                                                                                                        (207.0, 251.0),
#                                                                                                        (323.0, 251.0),
#                                                                                                        (323.0, 131.0)],
#                                                                                         'direction': 'N-S',
#                                                                                         'load': {'total_area': [],
#                                                                                                  'custom_area': [],
#                                                                                                  'load_map': []},
#                                                                                         'line': {'point': [((207.0,
#                                                                                                              131.0), (
#                                                                                                                 207.0,
#                                                                                                                 251.0)),
#                                                                                                            ((
#                                                                                                                 207.0,
#                                                                                                                 251.0),
#                                                                                                             (
#                                                                                                                 323.0,
#                                                                                                                 251.0)),
#                                                                                                            ((323.0,
#                                                                                                              251.0), (
#                                                                                                                 323.0,
#                                                                                                                 131.0)),
#                                                                                                            ((
#                                                                                                                 323.0,
#                                                                                                                 131.0),
#                                                                                                             (
#                                                                                                                 207.0,
#                                                                                                                 131.0))],
#                                                                                                  'properties': [
#                                                                                                      {'slope': False,
#                                                                                                       'c': 207.0,
#                                                                                                       'range': (
#                                                                                                           131.0,
#                                                                                                           251.0)},
#                                                                                                      {'slope': True,
#                                                                                                       'c': 251.0,
#                                                                                                       'range': (
#                                                                                                           207.0,
#                                                                                                           323.0)},
#                                                                                                      {'slope': False,
#                                                                                                       'c': 323.0,
#                                                                                                       'range': (
#                                                                                                           131.0,
#                                                                                                           251.0)},
#                                                                                                      {'slope': True,
#                                                                                                       'c': 131.0,
#                                                                                                       'range': (
#                                                                                                           207.0,
#                                                                                                           323.0)}]},
#                                                                                         'support': [{'label': 'B3',
#                                                                                                      'type': 'beam',
#                                                                                                      'intersection_range': (
#                                                                                                          207.0,
#                                                                                                          269.0)}]},
#            " <joist_new.joistRectangle(0x1ff456a48e0, pos=0,0) at 0x000001FF4803E200>": {'label': 'J2',
#                                                                                          'coordinate': [(8.0, 38.0),
#                                                                                                         (8.0, 251.0),
#                                                                                                         (207.0, 251.0),
#                                                                                                         (207.0, 38.0)],
#                                                                                          'direction': 'N-S',
#                                                                                          'load': {'total_area': [],
#                                                                                                   'custom_area': [],
#                                                                                                   'load_map': []},
#                                                                                          'line': {'point': [(
#                                                                                              (8.0, 38.0),
#                                                                                              (8.0,
#                                                                                               251.0)), ((
#                                                                                                             8.0,
#                                                                                                             251.0),
#                                                                                                         (
#                                                                                                             207.0,
#                                                                                                             251.0)),
#                                                                                              ((207.0,
#                                                                                                251.0), (
#                                                                                                   207.0,
#                                                                                                   38.0)), ((
#                                                                                                                207.0,
#                                                                                                                38.0),
#                                                                                                            (
#                                                                                                                8.0,
#                                                                                                                38.0))],
#                                                                                              'properties': [
#                                                                                                  {'slope': False,
#                                                                                                   'c': 8.0,
#                                                                                                   'range': (
#                                                                                                       38.0, 251.0)},
#                                                                                                  {'slope': True,
#                                                                                                   'c': 251.0,
#                                                                                                   'range': (
#                                                                                                       8.0, 207.0)},
#                                                                                                  {'slope': False,
#                                                                                                   'c': 207.0,
#                                                                                                   'range': (
#                                                                                                       38.0, 251.0)},
#                                                                                                  {'slope': True,
#                                                                                                   'c': 38.0,
#                                                                                                   'range': (
#                                                                                                       8.0, 207.0)}]},
#                                                                                          'support': [{'label': 'B3',
#                                                                                                       'type': 'beam',
#                                                                                                       'intersection_range': (
#                                                                                                           89.0,
#                                                                                                           207.0)}]},
#            "<joist_new.joistRectangle(0x1ff456a5120, pos=0,0) at 0x000001FF4803E6C0>": {'label': 'J3',
#                                                                                         'coordinate': [(113.0, 178.0),
#                                                                                                        (113.0, 342.0),
#                                                                                                        (260.0, 342.0),
#                                                                                                        (260.0, 178.0)],
#                                                                                         'direction': 'N-S',
#                                                                                         'load': {'total_area': [],
#                                                                                                  'custom_area': [],
#                                                                                                  'load_map': []},
#                                                                                         'line': {'point': [((113.0,
#                                                                                                              178.0), (
#                                                                                                                 113.0,
#                                                                                                                 342.0)),
#                                                                                                            ((
#                                                                                                                 113.0,
#                                                                                                                 342.0),
#                                                                                                             (
#                                                                                                                 260.0,
#                                                                                                                 342.0)),
#                                                                                                            ((260.0,
#                                                                                                              342.0), (
#                                                                                                                 260.0,
#                                                                                                                 178.0)),
#                                                                                                            ((
#                                                                                                                 260.0,
#                                                                                                                 178.0),
#                                                                                                             (
#                                                                                                                 113.0,
#                                                                                                                 178.0))],
#                                                                                                  'properties': [
#                                                                                                      {'slope': False,
#                                                                                                       'c': 113.0,
#                                                                                                       'range': (
#                                                                                                           178.0,
#                                                                                                           342.0)},
#                                                                                                      {'slope': True,
#                                                                                                       'c': 342.0,
#                                                                                                       'range': (
#                                                                                                           113.0,
#                                                                                                           260.0)},
#                                                                                                      {'slope': False,
#                                                                                                       'c': 260.0,
#                                                                                                       'range': (
#                                                                                                           178.0,
#                                                                                                           342.0)},
#                                                                                                      {'slope': True,
#                                                                                                       'c': 178.0,
#                                                                                                       'range': (
#                                                                                                           113.0,
#                                                                                                           260.0)}]},
#                                                                                         'support': []}
#            }
#
# beams2 = [{'label': 'B1', 'coordinate': [(89.0, 80.0), (217.0, 80.0)],
#            'load': {'point': [], 'line': [], 'joist_load': {'assignment': [], 'load_map': []}}, 'length': 128.0,
#            'line': {'properties': {'slope': True, 'c': 80.0, 'range': (89.0, 217.0)}}, 'direction': 'E-W',
#            'support': [{'label': 'P1', 'type': 'post', 'coordinate': (89.0, 80.0), 'range': 'start'}], 'joist': []},
#           {'label': 'B2', 'coordinate': [(89.0, 80.0), (89.0, 324.0)],
#            'load': {'point': [], 'line': [], 'joist_load': {'assignment': [], 'load_map': []}}, 'length': 244.0,
#            'line': {'properties': {'slope': False, 'c': 89.0, 'range': (80.0, 324.0)}}, 'direction': 'N-S',
#            'support': [{'label': 'P1', 'type': 'post', 'coordinate': (89.0, 80.0), 'range': 'start'}], 'joist': []},
#           {'label': 'B3', 'coordinate': [(89.0, 251.0), (269.0, 251.0)],
#            'load': {'point': [], 'line': [], 'joist_load': {'assignment': [], 'load_map': []}}, 'length': 180.0,
#            'line': {'properties': {'slope': True, 'c': 251.0, 'range': (89.0, 269.0)}}, 'direction': 'E-W',
#            'support': [{'label': 'B2', 'type': 'beam_mid_support', 'coordinate': (89.0, 251.0), 'range': 'start'}],
#            'joist': []},
#           {'label': 'B4', 'coordinate': [(89.0, 151.0), (89.0, 229.0)],
#            'load': {'point': [], 'line': [], 'joist_load': {'assignment': [], 'load_map': []}},
#            'length': 78.0, 'line': {'properties': {'slope': False, 'c': 89.0, 'range': (151.0, 229.0)}},
#            'direction': 'N-S', 'support': [
#               {'label': 'B2', 'type': 'beam_mid_support', 'coordinate': (89.0, 151.0), 'range': 'start'},
#               {'label': 'B2', 'type': 'beam_mid_support', 'coordinate': (89.0, 229.0), 'range': 'end'}], 'joist': []}
#           ]
#
# shearWall = [{'label': 'SW1', 'coordinate': [(400.0, 67.0), (400.0, 257.0)], 'length': 190.0,
#               'post': {'label_start': 'SWP1', 'label_end': 'SWP2',
#                        'start_rect_item': "<PySide6.QtWidgets.QGraphicsRectItem(0x1ff456993e0, pos=0,0) at 0x000001FF48005600>",
#                        'end_rect_item': "<PySide6.QtWidgets.QGraphicsRectItem(0x1ff45699e20, pos=0,0) at 0x000001FF48005640>",
#                        'start_center': (400.0, 77.0), 'end_center': (400.0, 247.0)}, 'direction': 'N-S',
#               'interior_exterior': 'exterior', 'line_label': 'B', 'thickness': '4 in',
#               'load': {'point': [], 'line': [], 'joist_load': {'assignment': [], 'load_map': []}},
#               'line': {'properties': {'slope': False, 'c': 400.0, 'range': (67.0, 257.0)}}, 'joist': [], 'beam': [],
#               'shearWall_intersection': []},
#              {'label': 'SW2', 'coordinate': [(404.0, 77.0), (404.0, 247.0)], 'length': 170.0,
#               'post': {'label_start': 'SWP3', 'label_end': 'SWP4',
#                        'start_rect_item': "<PySide6.QtWidgets.QGraphicsRectItem(0x1ff45699ae0, pos=0,0) at 0x000001FF48006180>",
#                        'end_rect_item': "<PySide6.QtWidgets.QGraphicsRectItem(0x1ff45699f60, pos=0,0) at 0x000001FF480061C0>",
#                        'start_center': (404.0, 87.0), 'end_center': (404.0, 237.0)}, 'direction': 'N-S',
#               'interior_exterior': 'exterior', 'line_label': 'B', 'thickness': '4 in',
#               'load': {'point': [], 'line': [], 'joist_load': {'assignment': [], 'load_map': []}},
#               'line': {'properties': {'slope': False, 'c': 404.0, 'range': (77.0, 247.0)}}, 'joist': [], 'beam': []},
#              {'label': 'SW3', 'coordinate': [(404.0, 77.0), (404.0, 213.0)], 'length': 136.0,
#               'post': {'label_start': 'SWP5', 'label_end': 'SWP6',
#                        'start_rect_item': "<PySide6.QtWidgets.QGraphicsRectItem(0x1ff456a43e0, pos=0,0) at 0x000001FF48005E40>",
#                        'end_rect_item': "<PySide6.QtWidgets.QGraphicsRectItem(0x1ff456a4e20, pos=0,0) at 0x000001FF48005BC0>",
#                        'start_center': (404.0, 87.0), 'end_center': (404.0, 203.0)}, 'direction': 'N-S',
#               'interior_exterior': 'exterior', 'line_label': 'B', 'thickness': '4 in',
#               'load': {'point': [], 'line': [], 'joist_load': {'assignment': [], 'load_map': []}},
#               'line': {'properties': {'slope': False, 'c': 404.0, 'range': (77.0, 213.0)}}, 'joist': [], 'beam': [],
#               'shearWall_intersection': []}
#              ]
# a = overlapLine(beams2, 1, "Beam")
# b = overlapLine(shearWall, 1, "ShearWall")
# print(a.warningList)
# print(b.warningList)
# c = overlapArea(list(joists2.values()), 1)
# print(c.warningList)
#
# a = Instable(beams, joists, 1)
# print(a.warningList)
