import sys
from abc import ABC, abstractmethod
import itertools
from PySide6 import QtWidgets
from PySide6.QtWebEngineWidgets import QWebEngineView

from UI_Wood.stableVersion3.Sync.data import Update
from UI_Wood.stableVersion3.post_new import magnification_factor
from UI_Wood.stableVersion3.back.load_control import range_intersection


class checkModel(Update):
    def __init__(self, saveFunc, grid, tabWidgetCount):
        self.saveFunc = saveFunc
        self.grid = grid
        self.tabWidgetCount = tabWidgetCount
        self.warningPage = None
        self.warnings = {}
        self.shearWallLinesExist = {}
        self.studWalls = {}

    def update(self, subject):
        self.tab = subject.data["tab"]
        self.warnings = {}
        for tabNumber, tabItems in self.tab.items():
            self.shearWallLinesExist[tabNumber] = set()
            story = int(tabNumber) + 1
            post = tabItems["post"]
            beam = tabItems["beam"]
            shearWall = tabItems["shearWall"]
            self.find_shearWall_lines(shearWall, self.shearWallLinesExist[tabNumber])
            joist = tabItems["joist"]
            studWall = tabItems["studWall"]
            self.studWalls[tabNumber] = studWall

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

    def check_shear_wall_exist_boundary(self, lineLabels):
        for tabNumber, item in self.shearWallLinesExist.items():
            noShearWallLines = set(lineLabels) - item
            instance = noShearWallWarning()
            self.warnings[tabNumber]["shearWallBoundary"] = instance(noShearWallLines, tabNumber)

    @staticmethod
    def find_shearWall_lines(shearWall, mySet):
        for prop in shearWall:
            mySet.add(prop["line_label"])

    # SLOT
    def check_model_run(self):
        lineLabels = None
        boundaryLineLabels = None
        for currentTab in range(self.tabWidgetCount):
            midLineData, lineLabels, boundaryLineLabels = self.grid[currentTab].run_control()

        self.saveFunc()
        self.check_shear_wall_exist_boundary(boundaryLineLabels)

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
            if not self.support or len(self.support) == 1:
                self.warning = {
                    "label": self.item["label"],
                    ""
                    "story": self.story,
                    "warning": Type + " " + self.item["label"] + " is unstable"
                    # "warning": Type + " " + self.item["label"] + " is " + self.warningMessage

                }
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
        warns = story_warning.values()
        header = f"""<h2><input type="checkbox" checked onclick="toggleList('list{str(story_number)}Items')"> Story {str(story_number)} </h2><ul id="list{str(story_number)}Items" class="warningList">"""
        warningText = ""
        for item in warns:
            if type(item) == dict:
                for value in item.values():
                    for detail in value:
                        text = detail["warning"]
                        warningText += f"""
                                    <li style="list-style: linear-gradient(rgb(253, 46, 46), rgb(253, 46, 46), rgb(253, 46, 46), rgb(253, 46, 46), white);">{text}</li>"""
            else:
                for detail in item:
                    text = detail["warning"]
                    warningText += f"""
                                    <li style="list-style: linear-gradient(rgb(253, 46, 46), rgb(253, 46, 46), rgb(253, 46, 46), rgb(253, 46, 46), white);">{text}</li>"""

        if not warningText:
            warningText = "No Warning!"

        finalText = header + warningText + """</ul> """
        return finalText


class noShearWallWarning:
    def __call__(self, lineList, story):
        lineListNew = list(lineList)
        lineListNew.sort()
        lines = ""
        for i, line in enumerate(lineListNew):
            lines += line
            if i < len(lineListNew) - 1:
                lines += ", "
        if lines:
            warning = {
                "story": story,
                "warning": f'Boundary shear line "{lines}" have no shear walls. It will occur conflict.'
            }
            return [warning]
        else:
            return []


class CheckModelAfterRun:
    def __init__(self, *args):
        self.Warnings = {}
        boundaryNoShearWall = args[0]
        if boundaryNoShearWall:
            self.Warnings["shearWall"]
            pass


class SameWidthStudWall:
    def __init__(self, studWalls):
        self.sameCoordinates = sameCoordinates = []
        self.widthAll = widthAll = []
        self.storiesAll = storiesAll = []
        for story, studs in studWalls.items():
            for stud in studs:
                labels = [stud["label"]]
                widths = [stud["thickness"]]
                stories = [story]
                coordMain = stud["coordinate"]
                for story2, studs2 in studWalls.items():
                    for stud2 in studs2:
                        coord2 = stud2["coordinate"]
                        if coordMain == coord2 and story != story2:
                            labels.append(stud2["label"])
                            widths.append(stud2["thickness"])
                            stories.append(story2)

                        if len(labels) > 1:
                            sameCoordinates.append(labels)
                            widthAll.append(widths)
                            storiesAll.append(storiesAll)


studs = {
    0: [
        {'label': 'ST1', 'coordinate': [(1240.0, 728.0), (1834.1781320826294, 728.0)], 'length': 594.18,
         'direction': 'E-W',
         'interior_exterior': 'interior', 'thickness': '4 in', 'load': {'point': [], 'line': [], 'reaction': [],
                                                                        'joist_load': {'assignment': [], 'load_map': [
                                                                            {'from': 'J9', 'label': 'Floor',
                                                                             'load': [
                                                                                 {'type': 'Dead', 'magnitude': 0.215},
                                                                                 {'type': 'Live', 'magnitude': 0.172},
                                                                                 {'type': 'Dead Super',
                                                                                  'magnitude': 0.258}],
                                                                             'start': 1312.0809220966387,
                                                                             'end': 1832.0},
                                                                            {'from': 'J18', 'label': 'Corridor',
                                                                             'load': [
                                                                                 {'type': 'Dead',
                                                                                  'magnitude': 0.09753522528740803},
                                                                                 {'type': 'Live',
                                                                                  'magnitude': 0.19507045057481606},
                                                                                 {'type': 'Dead Super',
                                                                                  'magnitude': 0.11704227034488963}],
                                                                             'start': 1240.0, 'end': 1309.828262591694},
                                                                            {'from': 'J18', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.35746477471259197},
                                                                                {'type': 'Live',
                                                                                 'magnitude': 0.2859718197700736},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.4289577296551103}],
                                                                             'start': 1240.0, 'end': 1309.828262591694},
                                                                            {'from': 'J18', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.45499999999999996},
                                                                                {'type': 'Live', 'magnitude': 0.364},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.546}],
                                                                             'start': 1312.0809220966387,
                                                                             'end': 1752.0},
                                                                            {'from': 'J19', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.45499999999999996},
                                                                                {'type': 'Live', 'magnitude': 0.364},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.546}],
                                                                             'start': 1752.0, 'end': 1832.0},
                                                                            {'from': 'J21', 'label': 'Corridor',
                                                                             'load': [
                                                                                 {'type': 'Dead', 'magnitude': 0.215},
                                                                                 {'type': 'Live', 'magnitude': 0.43},
                                                                                 {'type': 'Dead Super',
                                                                                  'magnitude': 0.258}],
                                                                             'start': 1240.0,
                                                                             'end': 1309.828262591694}]}},
         'line': {'properties': {'slope': True, 'c': 728.0, 'range': (1240.0, 1834.1781320826294)}},
         'joist': [
             {'label': 'J9', 'intersection_range': (1312.0809220966387, 1832.0), 'tributary_depth': (728.0, 900.0)},
             {'label': 'J18', 'intersection_range': (1240.0, 1752.0), 'tributary_depth': (364.0, 728.0)},
             {'label': 'J19', 'intersection_range': (1752.0, 1832.0), 'tributary_depth': (364.0, 728.0)},
             {'label': 'J21', 'intersection_range': (1240.0, 1312.0809220966387),
              'tributary_depth': (728.0, 900.0)}]},
        {'label': 'ST2', 'coordinate': [(1240.0, 654.9942848069184), (506.3660279514156, 654.9942848069184)],
         'length': 733.63, 'direction': 'E-W', 'interior_exterior': 'interior', 'thickness': '4 in',
         'load': {'point': [], 'line': [], 'reaction': [], 'joist_load': {'assignment': [], 'load_map': [
             {'from': 'J11', 'label': 'Corridor', 'load': [{'type': 'Dead', 'magnitude': 0.16312857199567604},
                                                           {'type': 'Live', 'magnitude': 0.3262571439913521},
                                                           {'type': 'Dead Super', 'magnitude': 0.19575428639481124}],
              'start': 717.513305817537, 'end': 1026.0}, {'from': 'J11', 'label': 'Floor',
                                                          'load': [{'type': 'Dead', 'magnitude': 0.16312857199567604},
                                                                   {'type': 'Live', 'magnitude': 0.13050285759654084},
                                                                   {'type': 'Dead Super',
                                                                    'magnitude': 0.19575428639481124}],
                                                          'start': 506.3660279514156, 'end': 718.1177806742272},
             {'from': 'J12', 'label': 'Corridor', 'load': [{'type': 'Dead', 'magnitude': 0.006278081296055974},
                                                           {'type': 'Live', 'magnitude': 0.012556162592111947},
                                                           {'type': 'Dead Super', 'magnitude': 0.007533697555267167}],
              'start': 1028.0, 'end': 1240.0}, {'from': 'J12', 'label': 'Corridor',
                                                'load': [{'type': 'Dead', 'magnitude': 0.006278081296055974},
                                                         {'type': 'Live', 'magnitude': 0.012556162592111947},
                                                         {'type': 'Dead Super', 'magnitude': 0.007533697555267167}],
                                                'start': 717.513305817537, 'end': 1028.0},
             {'from': 'J12', 'label': 'Floor',
              'load': [{'type': 'Dead',
                        'magnitude': 0.403093346708268},
                       {'type': 'Live',
                        'magnitude': 0.3224746773666144},
                       {'type': 'Dead Super',
                        'magnitude': 0.48371201604992164}],
              'start': 506.3660279514156,
              'end': 1240.0},
             {'from': 'J12', 'label': 'Floor', 'load': [{'type': 'Dead', 'magnitude': 0.006278081296055974},
                                                        {'type': 'Live', 'magnitude': 0.005022465036844778},
                                                        {'type': 'Dead Super', 'magnitude': 0.007533697555267167}],
              'start': 506.3660279514156, 'end': 718.1177806742272}, {'from': 'J20', 'label': 'Corridor', 'load': [
                 {'type': 'Dead', 'magnitude': 0.2606285719956761}, {'type': 'Live', 'magnitude': 0.5212571439913521},
                 {'type': 'Dead Super', 'magnitude': 0.31275428639481123}], 'start': 1028.0, 'end': 1240.0},
             {'from': 'J20', 'label': 'Corridor',
              'load': [{'type': 'Dead', 'magnitude': 0.2606285719956761},
                       {'type': 'Live', 'magnitude': 0.5212571439913521},
                       {'type': 'Dead Super', 'magnitude': 0.31275428639481123}], 'start': 1026.0, 'end': 1028.0}]}},
         'line': {'properties': {'slope': True, 'c': 654.9942848069184, 'range': (506.3660279514156, 1240.0)}},
         'joist': [
             {'label': 'J11', 'intersection_range': (506.3660279514156, 1026.0),
              'tributary_depth': (654.9942848069184, 785.4971424034592)},
             {'label': 'J12', 'intersection_range': (506.3660279514156, 1240.0),
              'tributary_depth': (327.4971424034592, 654.9942848069184)},
             {'label': 'J20', 'intersection_range': (1026.0, 1240.0),
              'tributary_depth': (654.9942848069184, 863.4971424034592)}]},
        {'label': 'ST3', 'coordinate': [(1423.0, 0.0), (2593.6509454272286, 0.0)], 'length': 1170.65,
         'direction': 'E-W',
         'interior_exterior': 'exterior', 'thickness': '6 in', 'load': {'point': [], 'line': [], 'reaction': [],
                                                                        'joist_load': {'assignment': [], 'load_map': [
                                                                            {'from': 'J13', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.37875000000000003},
                                                                                {'type': 'Live',
                                                                                 'magnitude': 0.30300000000000005},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.4545}], 'start': 2264.0,
                                                                             'end': 2593.6509454272286},
                                                                            {'from': 'J17', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.46174479692049913},
                                                                                {'type': 'Live',
                                                                                 'magnitude': 0.36939583753639926},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.5540937563045989}],
                                                                             'start': 1832.0, 'end': 2264.0},
                                                                            {'from': 'J18', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.45499999999999996},
                                                                                {'type': 'Live', 'magnitude': 0.364},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.546}],
                                                                             'start': 1423.0, 'end': 1752.0},
                                                                            {'from': 'J19', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.45499999999999996},
                                                                                {'type': 'Live', 'magnitude': 0.364},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.546}],
                                                                             'start': 1752.0, 'end': 1832.0}]}},
         'line': {'properties': {'slope': True, 'c': 0.0, 'range': (1423.0, 2593.6509454272286)}},
         'joist': [
             {'label': 'J13', 'intersection_range': (2264.0, 2593.6509454272286), 'tributary_depth': (0.0, 303.0)},
             {'label': 'J17', 'intersection_range': (1832.0, 2264.0), 'tributary_depth': (0.0, 369.39583753639926)},
             {'label': 'J18', 'intersection_range': (1423.0, 1752.0), 'tributary_depth': (0.0, 364.0)},
             {'label': 'J19', 'intersection_range': (1752.0, 1832.0), 'tributary_depth': (0.0, 364.0)}]}], 1: [
        {'label': 'ST1', 'coordinate': [(1240.0, 728.0), (1834.1781320826294, 728.0)], 'length': 594.18,
         'direction': 'E-W',
         'interior_exterior': 'interior', 'thickness': '4 in', 'load': {'point': [], 'line': [], 'reaction': [],
                                                                        'joist_load': {'assignment': [], 'load_map': [
                                                                            {'from': 'J9', 'label': 'Floor',
                                                                             'load': [
                                                                                 {'type': 'Dead', 'magnitude': 0.215},
                                                                                 {'type': 'Live', 'magnitude': 0.172},
                                                                                 {'type': 'Dead Super',
                                                                                  'magnitude': 0.258}],
                                                                             'start': 1312.0809220966387,
                                                                             'end': 1832.0},
                                                                            {'from': 'J18', 'label': 'Corridor',
                                                                             'load': [
                                                                                 {'type': 'Dead',
                                                                                  'magnitude': 0.09753522528740803},
                                                                                 {'type': 'Live',
                                                                                  'magnitude': 0.19507045057481606},
                                                                                 {'type': 'Dead Super',
                                                                                  'magnitude': 0.11704227034488963}],
                                                                             'start': 1240.0, 'end': 1309.828262591694},
                                                                            {'from': 'J18', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.35746477471259197},
                                                                                {'type': 'Live',
                                                                                 'magnitude': 0.2859718197700736},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.4289577296551103}],
                                                                             'start': 1240.0, 'end': 1309.828262591694},
                                                                            {'from': 'J18', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.45499999999999996},
                                                                                {'type': 'Live', 'magnitude': 0.364},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.546}],
                                                                             'start': 1312.0809220966387,
                                                                             'end': 1752.0},
                                                                            {'from': 'J19', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.45499999999999996},
                                                                                {'type': 'Live', 'magnitude': 0.364},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.546}],
                                                                             'start': 1752.0, 'end': 1832.0},
                                                                            {'from': 'J21', 'label': 'Corridor',
                                                                             'load': [
                                                                                 {'type': 'Dead', 'magnitude': 0.215},
                                                                                 {'type': 'Live', 'magnitude': 0.43},
                                                                                 {'type': 'Dead Super',
                                                                                  'magnitude': 0.258}],
                                                                             'start': 1240.0,
                                                                             'end': 1309.828262591694}]}},
         'line': {'properties': {'slope': True, 'c': 728.0, 'range': (1240.0, 1834.1781320826294)}},
         'joist': [
             {'label': 'J9', 'intersection_range': (1312.0809220966387, 1832.0), 'tributary_depth': (728.0, 900.0)},
             {'label': 'J18', 'intersection_range': (1240.0, 1752.0), 'tributary_depth': (364.0, 728.0)},
             {'label': 'J19', 'intersection_range': (1752.0, 1832.0), 'tributary_depth': (364.0, 728.0)},
             {'label': 'J21', 'intersection_range': (1240.0, 1312.0809220966387),
              'tributary_depth': (728.0, 900.0)}]},
        {'label': 'ST2', 'coordinate': [(1240.0, 654.9942848069184), (506.3660279514156, 654.9942848069184)],
         'length': 733.63, 'direction': 'E-W', 'interior_exterior': 'interior', 'thickness': '4 in',
         'load': {'point': [], 'line': [], 'reaction': [], 'joist_load': {'assignment': [], 'load_map': [
             {'from': 'J11', 'label': 'Corridor', 'load': [{'type': 'Dead', 'magnitude': 0.16312857199567604},
                                                           {'type': 'Live', 'magnitude': 0.3262571439913521},
                                                           {'type': 'Dead Super', 'magnitude': 0.19575428639481124}],
              'start': 717.513305817537, 'end': 1026.0}, {'from': 'J11', 'label': 'Floor',
                                                          'load': [{'type': 'Dead', 'magnitude': 0.16312857199567604},
                                                                   {'type': 'Live', 'magnitude': 0.13050285759654084},
                                                                   {'type': 'Dead Super',
                                                                    'magnitude': 0.19575428639481124}],
                                                          'start': 506.3660279514156, 'end': 718.1177806742272},
             {'from': 'J12', 'label': 'Corridor', 'load': [{'type': 'Dead', 'magnitude': 0.006278081296055974},
                                                           {'type': 'Live', 'magnitude': 0.012556162592111947},
                                                           {'type': 'Dead Super', 'magnitude': 0.007533697555267167}],
              'start': 1028.0, 'end': 1240.0}, {'from': 'J12', 'label': 'Corridor',
                                                'load': [{'type': 'Dead', 'magnitude': 0.006278081296055974},
                                                         {'type': 'Live', 'magnitude': 0.012556162592111947},
                                                         {'type': 'Dead Super', 'magnitude': 0.007533697555267167}],
                                                'start': 717.513305817537, 'end': 1028.0},
             {'from': 'J12', 'label': 'Floor',
              'load': [{'type': 'Dead',
                        'magnitude': 0.403093346708268},
                       {'type': 'Live',
                        'magnitude': 0.3224746773666144},
                       {'type': 'Dead Super',
                        'magnitude': 0.48371201604992164}],
              'start': 506.3660279514156,
              'end': 1240.0},
             {'from': 'J12', 'label': 'Floor', 'load': [{'type': 'Dead', 'magnitude': 0.006278081296055974},
                                                        {'type': 'Live', 'magnitude': 0.005022465036844778},
                                                        {'type': 'Dead Super', 'magnitude': 0.007533697555267167}],
              'start': 506.3660279514156, 'end': 718.1177806742272}, {'from': 'J20', 'label': 'Corridor', 'load': [
                 {'type': 'Dead', 'magnitude': 0.2606285719956761}, {'type': 'Live', 'magnitude': 0.5212571439913521},
                 {'type': 'Dead Super', 'magnitude': 0.31275428639481123}], 'start': 1028.0, 'end': 1240.0},
             {'from': 'J20', 'label': 'Corridor',
              'load': [{'type': 'Dead', 'magnitude': 0.2606285719956761},
                       {'type': 'Live', 'magnitude': 0.5212571439913521},
                       {'type': 'Dead Super', 'magnitude': 0.31275428639481123}], 'start': 1026.0, 'end': 1028.0}]}},
         'line': {'properties': {'slope': True, 'c': 654.9942848069184, 'range': (506.3660279514156, 1240.0)}},
         'joist': [
             {'label': 'J11', 'intersection_range': (506.3660279514156, 1026.0),
              'tributary_depth': (654.9942848069184, 785.4971424034592)},
             {'label': 'J12', 'intersection_range': (506.3660279514156, 1240.0),
              'tributary_depth': (327.4971424034592, 654.9942848069184)},
             {'label': 'J20', 'intersection_range': (1026.0, 1240.0),
              'tributary_depth': (654.9942848069184, 863.4971424034592)}]},
        {'label': 'ST3', 'coordinate': [(1423.0, 0.0), (2593.6509454272286, 0.0)], 'length': 1170.65,
         'direction': 'E-W',
         'interior_exterior': 'exterior', 'thickness': '6 in', 'load': {'point': [], 'line': [], 'reaction': [],
                                                                        'joist_load': {'assignment': [], 'load_map': [
                                                                            {'from': 'J13', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.37875000000000003},
                                                                                {'type': 'Live',
                                                                                 'magnitude': 0.30300000000000005},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.4545}], 'start': 2264.0,
                                                                             'end': 2593.6509454272286},
                                                                            {'from': 'J17', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.46174479692049913},
                                                                                {'type': 'Live',
                                                                                 'magnitude': 0.36939583753639926},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.5540937563045989}],
                                                                             'start': 1832.0, 'end': 2264.0},
                                                                            {'from': 'J18', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.45499999999999996},
                                                                                {'type': 'Live', 'magnitude': 0.364},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.546}],
                                                                             'start': 1423.0, 'end': 1752.0},
                                                                            {'from': 'J19', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.45499999999999996},
                                                                                {'type': 'Live', 'magnitude': 0.364},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.546}],
                                                                             'start': 1752.0, 'end': 1832.0}]}},
         'line': {'properties': {'slope': True, 'c': 0.0, 'range': (1423.0, 2593.6509454272286)}},
         'joist': [
             {'label': 'J13', 'intersection_range': (2264.0, 2593.6509454272286), 'tributary_depth': (0.0, 303.0)},
             {'label': 'J17', 'intersection_range': (1832.0, 2264.0), 'tributary_depth': (0.0, 369.39583753639926)},
             {'label': 'J18', 'intersection_range': (1423.0, 1752.0), 'tributary_depth': (0.0, 364.0)},
             {'label': 'J19', 'intersection_range': (1752.0, 1832.0), 'tributary_depth': (0.0, 364.0)}]}], 2: [
        {'label': 'ST1', 'coordinate': [(1240.0, 728.0), (1834.1781320826294, 728.0)], 'length': 594.18,
         'direction': 'E-W',
         'interior_exterior': 'interior', 'thickness': '4 in', 'load': {'point': [], 'line': [], 'reaction': [],
                                                                        'joist_load': {'assignment': [], 'load_map': [
                                                                            {'from': 'J9', 'label': 'Floor',
                                                                             'load': [
                                                                                 {'type': 'Dead', 'magnitude': 0.215},
                                                                                 {'type': 'Live', 'magnitude': 0.172},
                                                                                 {'type': 'Dead Super',
                                                                                  'magnitude': 0.258}],
                                                                             'start': 1312.0809220966387,
                                                                             'end': 1832.0},
                                                                            {'from': 'J18', 'label': 'Corridor',
                                                                             'load': [
                                                                                 {'type': 'Dead',
                                                                                  'magnitude': 0.09753522528740803},
                                                                                 {'type': 'Live',
                                                                                  'magnitude': 0.19507045057481606},
                                                                                 {'type': 'Dead Super',
                                                                                  'magnitude': 0.11704227034488963}],
                                                                             'start': 1240.0, 'end': 1309.828262591694},
                                                                            {'from': 'J18', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.35746477471259197},
                                                                                {'type': 'Live',
                                                                                 'magnitude': 0.2859718197700736},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.4289577296551103}],
                                                                             'start': 1240.0, 'end': 1309.828262591694},
                                                                            {'from': 'J18', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.45499999999999996},
                                                                                {'type': 'Live', 'magnitude': 0.364},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.546}],
                                                                             'start': 1312.0809220966387,
                                                                             'end': 1752.0},
                                                                            {'from': 'J19', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.45499999999999996},
                                                                                {'type': 'Live', 'magnitude': 0.364},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.546}],
                                                                             'start': 1752.0, 'end': 1832.0},
                                                                            {'from': 'J21', 'label': 'Corridor',
                                                                             'load': [
                                                                                 {'type': 'Dead', 'magnitude': 0.215},
                                                                                 {'type': 'Live', 'magnitude': 0.43},
                                                                                 {'type': 'Dead Super',
                                                                                  'magnitude': 0.258}],
                                                                             'start': 1240.0,
                                                                             'end': 1309.828262591694}]}},
         'line': {'properties': {'slope': True, 'c': 728.0, 'range': (1240.0, 1834.1781320826294)}},
         'joist': [
             {'label': 'J9', 'intersection_range': (1312.0809220966387, 1832.0), 'tributary_depth': (728.0, 900.0)},
             {'label': 'J18', 'intersection_range': (1240.0, 1752.0), 'tributary_depth': (364.0, 728.0)},
             {'label': 'J19', 'intersection_range': (1752.0, 1832.0), 'tributary_depth': (364.0, 728.0)},
             {'label': 'J21', 'intersection_range': (1240.0, 1312.0809220966387),
              'tributary_depth': (728.0, 900.0)}]},
        {'label': 'ST2', 'coordinate': [(1240.0, 654.9942848069184), (506.3660279514156, 654.9942848069184)],
         'length': 733.63, 'direction': 'E-W', 'interior_exterior': 'interior', 'thickness': '4 in',
         'load': {'point': [], 'line': [], 'reaction': [], 'joist_load': {'assignment': [], 'load_map': [
             {'from': 'J11', 'label': 'Corridor', 'load': [{'type': 'Dead', 'magnitude': 0.16312857199567604},
                                                           {'type': 'Live', 'magnitude': 0.3262571439913521},
                                                           {'type': 'Dead Super', 'magnitude': 0.19575428639481124}],
              'start': 717.513305817537, 'end': 1026.0}, {'from': 'J11', 'label': 'Floor',
                                                          'load': [{'type': 'Dead', 'magnitude': 0.16312857199567604},
                                                                   {'type': 'Live', 'magnitude': 0.13050285759654084},
                                                                   {'type': 'Dead Super',
                                                                    'magnitude': 0.19575428639481124}],
                                                          'start': 506.3660279514156, 'end': 718.1177806742272},
             {'from': 'J12', 'label': 'Corridor', 'load': [{'type': 'Dead', 'magnitude': 0.006278081296055974},
                                                           {'type': 'Live', 'magnitude': 0.012556162592111947},
                                                           {'type': 'Dead Super', 'magnitude': 0.007533697555267167}],
              'start': 1028.0, 'end': 1240.0}, {'from': 'J12', 'label': 'Corridor',
                                                'load': [{'type': 'Dead', 'magnitude': 0.006278081296055974},
                                                         {'type': 'Live', 'magnitude': 0.012556162592111947},
                                                         {'type': 'Dead Super', 'magnitude': 0.007533697555267167}],
                                                'start': 717.513305817537, 'end': 1028.0},
             {'from': 'J12', 'label': 'Floor',
              'load': [{'type': 'Dead',
                        'magnitude': 0.403093346708268},
                       {'type': 'Live',
                        'magnitude': 0.3224746773666144},
                       {'type': 'Dead Super',
                        'magnitude': 0.48371201604992164}],
              'start': 506.3660279514156,
              'end': 1240.0},
             {'from': 'J12', 'label': 'Floor', 'load': [{'type': 'Dead', 'magnitude': 0.006278081296055974},
                                                        {'type': 'Live', 'magnitude': 0.005022465036844778},
                                                        {'type': 'Dead Super', 'magnitude': 0.007533697555267167}],
              'start': 506.3660279514156, 'end': 718.1177806742272}, {'from': 'J20', 'label': 'Corridor', 'load': [
                 {'type': 'Dead', 'magnitude': 0.2606285719956761}, {'type': 'Live', 'magnitude': 0.5212571439913521},
                 {'type': 'Dead Super', 'magnitude': 0.31275428639481123}], 'start': 1028.0, 'end': 1240.0},
             {'from': 'J20', 'label': 'Corridor',
              'load': [{'type': 'Dead', 'magnitude': 0.2606285719956761},
                       {'type': 'Live', 'magnitude': 0.5212571439913521},
                       {'type': 'Dead Super', 'magnitude': 0.31275428639481123}], 'start': 1026.0, 'end': 1028.0}]}},
         'line': {'properties': {'slope': True, 'c': 654.9942848069184, 'range': (506.3660279514156, 1240.0)}},
         'joist': [
             {'label': 'J11', 'intersection_range': (506.3660279514156, 1026.0),
              'tributary_depth': (654.9942848069184, 785.4971424034592)},
             {'label': 'J12', 'intersection_range': (506.3660279514156, 1240.0),
              'tributary_depth': (327.4971424034592, 654.9942848069184)},
             {'label': 'J20', 'intersection_range': (1026.0, 1240.0),
              'tributary_depth': (654.9942848069184, 863.4971424034592)}]},
        {'label': 'ST3', 'coordinate': [(1423.0, 0.0), (2593.6509454272286, 0.0)], 'length': 1170.65,
         'direction': 'E-W',
         'interior_exterior': 'exterior', 'thickness': '6 in', 'load': {'point': [], 'line': [], 'reaction': [],
                                                                        'joist_load': {'assignment': [], 'load_map': [
                                                                            {'from': 'J13', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.37875000000000003},
                                                                                {'type': 'Live',
                                                                                 'magnitude': 0.30300000000000005},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.4545}], 'start': 2264.0,
                                                                             'end': 2593.6509454272286},
                                                                            {'from': 'J17', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.46174479692049913},
                                                                                {'type': 'Live',
                                                                                 'magnitude': 0.36939583753639926},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.5540937563045989}],
                                                                             'start': 1832.0, 'end': 2264.0},
                                                                            {'from': 'J18', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.45499999999999996},
                                                                                {'type': 'Live', 'magnitude': 0.364},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.546}],
                                                                             'start': 1423.0, 'end': 1752.0},
                                                                            {'from': 'J19', 'label': 'Floor', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.45499999999999996},
                                                                                {'type': 'Live', 'magnitude': 0.364},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.546}],
                                                                             'start': 1752.0, 'end': 1832.0}]}},
         'line': {'properties': {'slope': True, 'c': 0.0, 'range': (1423.0, 2593.6509454272286)}},
         'joist': [
             {'label': 'J13', 'intersection_range': (2264.0, 2593.6509454272286), 'tributary_depth': (0.0, 303.0)},
             {'label': 'J17', 'intersection_range': (1832.0, 2264.0), 'tributary_depth': (0.0, 369.39583753639926)},
             {'label': 'J18', 'intersection_range': (1423.0, 1752.0), 'tributary_depth': (0.0, 364.0)},
             {'label': 'J19', 'intersection_range': (1752.0, 1832.0), 'tributary_depth': (0.0, 364.0)}]}], 3: [
        {'label': 'ST1', 'coordinate': [(1240.0, 728.0), (1834.1781320826294, 728.0)], 'length': 594.18,
         'direction': 'E-W',
         'interior_exterior': 'interior', 'thickness': '4 in', 'load': {'point': [], 'line': [], 'reaction': [],
                                                                        'joist_load': {'assignment': [], 'load_map': [
                                                                            {'from': 'J10', 'label': 'solar', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.07051054236505752},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.03525527118252876},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.08813817795632191}],
                                                                             'start': 1312.0809220966387,
                                                                             'end': 1832.0},
                                                                            {'from': 'J10', 'label': 'Roof', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.10148945763494248},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.05074472881747124},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.1268618220436781}],
                                                                             'start': 1312.0809220966387,
                                                                             'end': 1832.0},
                                                                            {'from': 'J19', 'label': 'solar', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.33389215156045976},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.16694607578022988},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.4173651894505747}],
                                                                             'start': 1240.0, 'end': 1752.0},
                                                                            {'from': 'J19', 'label': 'solar', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.030107848439540248},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.015053924219770124},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.037634810549425315}],
                                                                             'start': 1240.0, 'end': 1752.0},
                                                                            {'from': 'J20', 'label': 'solar', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.33389215156045976},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.16694607578022988},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.4173651894505747}],
                                                                             'start': 1752.0, 'end': 1832.0},
                                                                            {'from': 'J20', 'label': 'solar', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.030107848439540248},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.015053924219770124},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.037634810549425315}],
                                                                             'start': 1752.0, 'end': 1832.0},
                                                                            {'from': 'J22', 'label': 'solar', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.07051054236505752},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.03525527118252876},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.08813817795632191}],
                                                                             'start': 1240.0,
                                                                             'end': 1312.0809220966387},
                                                                            {'from': 'J22', 'label': 'Roof', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.10148945763494248},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.05074472881747124},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.1268618220436781}],
                                                                             'start': 1240.0,
                                                                             'end': 1312.0809220966387}]}},
         'line': {'properties': {'slope': True, 'c': 728.0, 'range': (1240.0, 1834.1781320826294)}},
         'joist': [
             {'label': 'J10', 'intersection_range': (1312.0809220966387, 1832.0), 'tributary_depth': (728.0, 900.0)},
             {'label': 'J19', 'intersection_range': (1240.0, 1752.0), 'tributary_depth': (364.0, 728.0)},
             {'label': 'J20', 'intersection_range': (1752.0, 1832.0), 'tributary_depth': (364.0, 728.0)},
             {'label': 'J22', 'intersection_range': (1240.0, 1312.0809220966387),
              'tributary_depth': (728.0, 900.0)}]},
        {'label': 'ST2', 'coordinate': [(1240.0, 654.9942848069184), (506.3660279514156, 654.9942848069184)],
         'length': 733.63, 'direction': 'E-W', 'interior_exterior': 'interior', 'thickness': '6 in',
         'load': {'point': [], 'line': [], 'reaction': [], 'joist_load': {'assignment': [], 'load_map': [
             {'from': 'J12', 'label': 'solar', 'load': [{'type': 'Dead', 'magnitude': 0.04289786675354139},
                                                        {'type': 'Live Roof', 'magnitude': 0.021448933376770694},
                                                        {'type': 'Dead Super', 'magnitude': 0.05362233344192674}],
              'start': 961.3975976590955, 'end': 1026.0}, {'from': 'J12', 'label': 'Roof',
                                                           'load': [{'type': 'Dead', 'magnitude': 0.08760499084299943},
                                                                    {'type': 'Live Roof',
                                                                     'magnitude': 0.043802495421499714},
                                                                    {'type': 'Dead Super',
                                                                     'magnitude': 0.10950623855374927}],
                                                           'start': 506.3660279514156, 'end': 1026.0},
             {'from': 'J12', 'label': 'Roof', 'load': [{'type': 'Dead', 'magnitude': 0.04289786675354139},
                                                       {'type': 'Live Roof', 'magnitude': 0.021448933376770694},
                                                       {'type': 'Dead Super', 'magnitude': 0.05362233344192674}],
              'start': 506.3660279514156, 'end': 961.3975976590955}, {'from': 'J13', 'label': 'mechanical', 'load': [
                 {'type': 'Dead', 'magnitude': 0.8441714688311102},
                 {'type': 'Live Roof', 'magnitude': 0.12059592411873002},
                 {'type': 'Dead Super', 'magnitude': 0.9044694308904753}], 'start': 556.6372528315096,
                                                                      'end': 799.9508160499008},
             {'from': 'J13', 'label': 'solar', 'load': [{'type': 'Dead', 'magnitude': 0.3252739723269172},
                                                        {'type': 'Live Roof', 'magnitude': 0.1626369861634586},
                                                        {'type': 'Dead Super', 'magnitude': 0.40659246540864646}],
              'start': 961.3975976590955, 'end': 1240.0}, {'from': 'J13', 'label': 'Roof',
                                                           'load': [
                                                               {'type': 'Dead', 'magnitude': 0.0022231700765420327},
                                                               {'type': 'Live Roof',
                                                                'magnitude': 0.0011115850382710164},
                                                               {'type': 'Dead Super',
                                                                'magnitude': 0.002778962595677541}],
                                                           'start': 961.3975976590955, 'end': 1240.0},
             {'from': 'J13', 'label': 'Roof', 'load': [{'type': 'Dead', 'magnitude': 0.24119184823746004},
                                                       {'type': 'Live Roof', 'magnitude': 0.12059592411873002},
                                                       {'type': 'Dead Super', 'magnitude': 0.30148981029682503}],
              'start': 799.9508160499008, 'end': 961.3975976590955}, {'from': 'J13', 'label': 'Roof', 'load': [
                 {'type': 'Dead', 'magnitude': 0.08630529416599916},
                 {'type': 'Live Roof', 'magnitude': 0.04315264708299958},
                 {'type': 'Dead Super', 'magnitude': 0.10788161770749896}], 'start': 506.3660279514156,
                                                                      'end': 961.3975976590955},
             {'from': 'J13', 'label': 'Roof', 'load': [{'type': 'Dead', 'magnitude': 0.24119184823746004},
                                                       {'type': 'Live Roof', 'magnitude': 0.12059592411873002},
                                                       {'type': 'Dead Super', 'magnitude': 0.30148981029682503}],
              'start': 506.3660279514156, 'end': 556.6372528315096}, {'from': 'J21', 'label': 'solar', 'load': [
                 {'type': 'Dead', 'magnitude': 0.04289786675354139},
                 {'type': 'Live Roof', 'magnitude': 0.021448933376770694},
                 {'type': 'Dead Super', 'magnitude': 0.05362233344192674}], 'start': 1026.0, 'end': 1240.0},
             {'from': 'J21', 'label': 'solar', 'load': [{'type': 'Dead', 'magnitude': 0.10061839080459775},
                                                        {'type': 'Live Roof', 'magnitude': 0.050309195402298876},
                                                        {'type': 'Dead Super', 'magnitude': 0.1257729885057472}],
              'start': 1210.6567930613946, 'end': 1240.0}, {'from': 'J21', 'label': 'Roof',
                                                            'load': [{'type': 'Dead', 'magnitude': 0.06498660003840166},
                                                                     {'type': 'Live Roof',
                                                                      'magnitude': 0.03249330001920083},
                                                                     {'type': 'Dead Super',
                                                                      'magnitude': 0.08123325004800208}],
                                                            'start': 1026.0,
                                                            'end': 1240.0}, {'from': 'J21', 'label': 'Roof', 'load': [
                 {'type': 'Dead', 'magnitude': 0.10061839080459775},
                 {'type': 'Live Roof', 'magnitude': 0.050309195402298876},
                 {'type': 'Dead Super', 'magnitude': 0.1257729885057472}], 'start': 1026.0,
                                                                             'end': 1210.6567930613946}]}},
         'line': {'properties': {'slope': True, 'c': 654.9942848069184, 'range': (506.3660279514156, 1240.0)}},
         'joist': [
             {'label': 'J12', 'intersection_range': (506.3660279514156, 1026.0),
              'tributary_depth': (654.9942848069184, 785.4971424034592)},
             {'label': 'J13', 'intersection_range': (506.3660279514156, 1240.0),
              'tributary_depth': (327.4971424034592, 654.9942848069184)},
             {'label': 'J21', 'intersection_range': (1026.0, 1240.0),
              'tributary_depth': (654.9942848069184, 863.4971424034592)}]},
        {'label': 'ST3', 'coordinate': [(1423.0, 0.0), (2593.6509454272286, 0.0)], 'length': 1170.65,
         'direction': 'E-W',
         'interior_exterior': 'exterior', 'thickness': '6 in', 'load': {'point': [], 'line': [], 'reaction': [],
                                                                        'joist_load': {'assignment': [], 'load_map': [
                                                                            {'from': 'J14', 'label': 'Roof', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.30300000000000005},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.15150000000000002},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.37875000000000003}],
                                                                             'start': 2264.0,
                                                                             'end': 2593.6509454272286},
                                                                            {'from': 'J18', 'label': 'solar', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.03967552505639804},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.01983776252819902},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.04959440632049756}],
                                                                             'start': 1832.0, 'end': 2264.0},
                                                                            {'from': 'J18', 'label': 'Roof', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.3297203124800012},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.1648601562400006},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.4121503906000015}],
                                                                             'start': 1832.0, 'end': 2264.0},
                                                                            {'from': 'J19', 'label': 'solar', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.03427968751999878},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.01713984375999939},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.04284960939999849}],
                                                                             'start': 1423.0, 'end': 1752.0},
                                                                            {'from': 'J19', 'label': 'Roof', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.3297203124800012},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.1648601562400006},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.4121503906000015}],
                                                                             'start': 1423.0, 'end': 1752.0},
                                                                            {'from': 'J20', 'label': 'solar', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.03427968751999878},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.01713984375999939},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.04284960939999849}],
                                                                             'start': 1752.0, 'end': 1832.0},
                                                                            {'from': 'J20', 'label': 'Roof', 'load': [
                                                                                {'type': 'Dead',
                                                                                 'magnitude': 0.3297203124800012},
                                                                                {'type': 'Live Roof',
                                                                                 'magnitude': 0.1648601562400006},
                                                                                {'type': 'Dead Super',
                                                                                 'magnitude': 0.4121503906000015}],
                                                                             'start': 1752.0, 'end': 1832.0}]}},
         'line': {'properties': {'slope': True, 'c': 0.0, 'range': (1423.0, 2593.6509454272286)}},
         'joist': [
             {'label': 'J14', 'intersection_range': (2264.0, 2593.6509454272286), 'tributary_depth': (0.0, 303.0)},
             {'label': 'J18', 'intersection_range': (1832.0, 2264.0), 'tributary_depth': (0.0, 369.39583753639926)},
             {'label': 'J19', 'intersection_range': (1423.0, 1752.0), 'tributary_depth': (0.0, 364.0)},
             {'label': 'J20', 'intersection_range': (1752.0, 1832.0), 'tributary_depth': (0.0, 364.0)}]}]}
# a = SameWidthStudWall(studs)
# print(a)
