import sys
import time
from abc import ABC, abstractmethod
import itertools
from PySide6 import QtWidgets
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PySide6.QtCore import QThread, Signal, Slot, QTimer

from UI_Wood.stableVersion5.Sync.data import Update
from UI_Wood.stableVersion5.post_new import magnification_factor
from UI_Wood.stableVersion5.back.load_control import range_intersection
from UI_Wood.stableVersion5.styles import TabWidgetStyle
from UI_Wood.stableVersion5.back.beam_check import BeamCheck


class checkModel(Update):
    def __init__(self, saveFunc, grid, tabWidgetCount):
        self.saveFunc = saveFunc
        self.grid = grid
        self.tabWidgetCount = tabWidgetCount
        self.warningPage = None
        self.warnings = {}
        self.shearWallLinesExist = {}
        self.studWalls = {}
        self.checkModelPage = None

    def update(self, subject):
        self.tab = subject.data["tab"]
        self.general_properties = subject.data["general_properties"]
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

        self.checkModelPage = CheckModel(self.warningPage, self.warnings, self.tab, self.general_properties)
        self.checkModelPage.show()
        # self.warningPage = warningPage(self.warnings)
        # print(self.warnings)


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


# class CheckModel(QWidget):
#     def __init__(self):
#         super(CheckModel, self).__init__()
#         self.setStyleSheet(TabWidgetStyle)
#         overlapButton = QPushButton("Overlap Check")
#         boundaryButton = QPushButton("ShearWall Boundary Check")
#         beamButton = QPushButton("Beam Check")
#         self.layout = QVBoxLayout()
#         self.layout.addWidget(overlapButton)
#         self.layout.addWidget(boundaryButton)
#         self.layout.addWidget(beamButton)
#         self.setWindowTitle("Check Model")
#         self.setLayout(self.layout)


class SelfClosingMessageBox(QMessageBox):
    def __init__(self, timeout=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Loading . . . ")
        self.setStyleSheet(TabWidgetStyle)
        self.setStandardButtons(QMessageBox.NoButton)  # Remove the default buttons
        self.timeout = timeout
        # self._startTimer()

    def _startTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)
        self.timer.start(self.timeout * 1000)  # Convert seconds to milliseconds

    def closeEvent(self, event):
        # self.timer.stop()
        self.accept()
        super().closeEvent(event)


class CheckModel(QWidget):
    def __init__(self, WarningPage, warnings, tab, general_properties):
        super(CheckModel, self).__init__()
        self.warnings = warnings
        self.warningPage = WarningPage
        self.tab = tab
        self.general_properties = general_properties
        self.beam_check_page = None

        # Set up UI components
        self.initUI()

        # Resize and center the window based on the screen size
        self.resize_and_center()

        # Set window properties
        self.setWindowTitle("Check Model")
        self.setStyleSheet(TabWidgetStyle)  # Assuming TabWidgetStyle was a string with stylesheet properties

        self.infoBox = None
        self.infoBox1 = None

    def initUI(self):
        # Create buttons
        self.overlapButton = QPushButton("Overlap Check")
        self.boundaryButton = QPushButton("ShearWall Boundary Check")
        self.beamButton = QPushButton("Beam Check")

        # Connect buttons to slots
        self.overlapButton.clicked.connect(self.start_overlap_check)
        self.boundaryButton.clicked.connect(self.start_boundary_check)
        self.beamButton.clicked.connect(self.start_beam_check)

        # Set up layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.overlapButton)
        self.layout.addWidget(self.boundaryButton)
        self.layout.addWidget(self.beamButton)
        self.setLayout(self.layout)

    def resize_and_center(self):
        # Get the screen geometry
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Set the window size to a fraction of the screen size (e.g., 0.5)
        width = int(screen_geometry.width() * 0.2)
        height = int(screen_geometry.height() * 0.2)
        self.resize(width, height)

        # Center the window
        self.move(
            (screen_geometry.width() - width) // 2,
            (screen_geometry.height() - height) // 2
        )

    @Slot()
    def start_overlap_check(self):
        self.run_overlap("Overlap Check", "Running overlap check...")

    @Slot()
    def start_boundary_check(self):
        self.run_boundary("ShearWall Boundary Check", "Running shear wall boundary check...")

    @Slot()
    def start_beam_check(self):
        self.run_check_task("Beam Check", "Running beam check...")

    def run_check_task(self, task_name, message):
        # Show the self-closing message box
        self.infoBox = SelfClosingMessageBox(timeout=5)
        self.infoBox.setText(message)
        self.infoBox.setWindowTitle("Check Started")
        self.infoBox.show()
        self.beam_check_page = BeamCheck(self.tab, self.general_properties)
        # Example of starting a long-running task in a separate thread
        self.worker = CheckWorker(task_name)
        self.worker.task_completed.connect(self.on_task_completed)
        self.worker.start()
        # QMessageBox.information(self, "Task Started", message)

    def run_overlap(self, task_name, message):
        # Show the self-closing message box
        self.infoBox = SelfClosingMessageBox(timeout=5)
        self.infoBox.setText(message)
        self.infoBox.setWindowTitle("Check Started")
        self.infoBox.show()
        # Filter warnings.
        filteredWarnings = {}
        for story, value in self.warnings.items():
            filteredWarnings[story] = {}
            filteredWarnings[story]["overlap"] = value["overlap"]
        # Example of starting a long-running task in a separate thread
        self.warningPage = warningPage(filteredWarnings)
        self.worker = CheckWorker(task_name)
        self.worker.task_completed.connect(self.on_task_completed)
        self.worker.start()
        # QMessageBox.information(self, "Task Started", message)

    def run_boundary(self, task_name, message):
        # Show the self-closing message box
        self.infoBox = SelfClosingMessageBox(timeout=5)
        self.infoBox.setText(message)
        self.infoBox.setWindowTitle("Check Started")
        self.infoBox.show()
        # Filter warnings.
        filteredWarnings = {}
        for story, value in self.warnings.items():
            filteredWarnings[story] = {}
            filteredWarnings[story]["shearWallBoundary"] = value["shearWallBoundary"]
        # Example of starting a long-running task in a separate thread
        self.warningPage = warningPage(filteredWarnings)
        self.worker = CheckWorker(task_name)
        self.worker.task_completed.connect(self.on_task_completed)
        self.worker.start()

    @Slot(str)
    def on_task_completed(self, result):
        QMessageBox.information(self, "Check Completed", result)
        if self.infoBox.isVisible():
            self.infoBox.close()  # Ensure the info box is closed if the task completes before timeout


class CheckWorker(QThread):
    task_completed = Signal(str)

    def __init__(self, task_name):
        super().__init__()
        self.task_name = task_name

    def run(self):
        self.task_completed.emit(f"{self.task_name} completed")


class OverLapWorker(QThread):
    task_completed = Signal(str)

    def __init__(self, task_name, WarningPage, warnings):
        super().__init__()
        self.task_name = task_name
        self.warnings = warnings
        self.warningPage = WarningPage

    def run(self):
        # self.warningPage.show()
        # self.warningPage.browser.show()
        print("heloooooooooo")

        self.task_completed.emit(f"{self.task_name} completed")
