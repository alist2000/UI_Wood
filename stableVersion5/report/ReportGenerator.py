import copy
import os
from PySide6.QtWidgets import QApplication, QHBoxLayout, QCheckBox, QWidget, QTabWidget, QVBoxLayout, QPushButton, \
    QLabel, QSpacerItem, QSizePolicy, QDoubleSpinBox
from PySide6.QtCore import Qt
from functools import partial

import sqlite3
from UI_Wood.stableVersion5.replicate import CheckableComboBox
from UI_Wood.stableVersion5.post_new import magnification_factor
from UI_Wood.stableVersion5.path import PathHandler, postInputPath, beamInputPath, beamReportPath, \
    shearWallInputPath, shearWallOutputPath, studWallInputPath, studWallOutputPath, joistInputPath

from Report_Lab.version3.main import Main
from UI_Wood.stableVersion5.styles import TabWidgetStyle, ButtonCheck
from UI_Wood.stableVersion5.report.backgroudImage import ImageSelector
from UI_Wood.stableVersion5.path import PathHandler


class ReportGeneratorTab(QWidget):
    def __init__(self, storyCount, general_information, second_tab):
        super(ReportGeneratorTab, self).__init__()
        self.general_information = general_information
        self.second_tab = second_tab
        self.result = {}
        self.setStyleSheet(TabWidgetStyle)
        self.setWindowTitle("Report Generation")

        layout = QHBoxLayout()
        v_layout = QVBoxLayout()

        # Create checkboxes
        self.option1 = QCheckBox("Compact Summary")
        self.option2 = QCheckBox("Summary")
        self.option3 = QCheckBox("Detail")
        self.generate = QPushButton("Generate")
        path = PathHandler("images/check.png")
        # Normalize the path to the current OS's format
        check_image = os.path.normpath(path)

        # Convert to forward slashes
        check_image = check_image.replace("\\", "/")

        # Apply stylesheet to checkboxes
        stylesheet = """
           QCheckBox::indicator {
               width: 13px;
               height: 13px;
               border: 1px solid #B3B3B3;
               border-radius: 7px;
               background: #FFFFFF;
           }
           QCheckBox::indicator:checked {
               background: #A8DF8E;"""
        stylesheet += f"""
               image: url({check_image});
           
        """
        stylesheet += """}
           QCheckBox::indicator:unchecked:hover {
               border: 1px solid #11111;
           }
           """
        self.option1.setStyleSheet(stylesheet)
        self.option2.setStyleSheet(stylesheet)
        self.option3.setStyleSheet(stylesheet)

        tab_widget = QTabWidget()
        self.mainTable = ReportMainTable(tab_widget, storyCount)

        # Add checkboxes and tab widget to layout
        v_layout.addWidget(self.option1)
        v_layout.addWidget(self.option2)
        v_layout.addWidget(self.option3)
        v_layout.addWidget(self.generate)

        layout.addLayout(v_layout)
        layout.addWidget(tab_widget)

        # Set layout
        self.setLayout(layout)
        self.generate.clicked.connect(self.Generate)
        self.show()

    # SLOT
    def Generate(self):
        self.generate.setStyleSheet(ButtonCheck)
        posts = self.mainTable.labelAllPost
        postList = []
        for post in posts:
            postList.append(post.currentData())

        beams = self.mainTable.labelAllBeam
        beamList = []
        for beam in beams:
            beamList.append(beam.currentData())

        shearWalls = self.mainTable.labelAllShearWall
        shearWallList = []
        for shearWall in shearWalls:
            shearWallList.append(shearWall.currentData())

        joists = self.mainTable.labelAllJoist
        joistList = []
        for joist in joists:
            joistList.append(joist.currentData())

        studWalls = self.mainTable.labelAllStudWall
        studWallList = []
        for studWall in studWalls:
            studWallList.append(studWall.currentData())

        opacity = self.mainTable.opacity
        opacityList = []
        for opa in opacity:
            opacityList.append(opa.value())
        imagePath = self.mainTable.imagePath
        imagePathList = []
        for image in imagePath:
            imagePathList.append(image.imagePath)

        # report type
        reportTypes = [i.text() for i in [self.option1, self.option2, self.option3] if i.isChecked()]

        self.result["post"] = postList
        self.result["beam"] = beamList
        self.result["joist"] = joistList
        self.result["shearWall"] = shearWallList
        self.result["studWall"] = studWallList
        print(self.mainTable.JoistsLayout)
        if self.mainTable.PostsLayout:
            selected_posts = self.selected_items(self.mainTable.PostsLayout, postList)
        else:
            selected_posts = {}
        if self.mainTable.BeamsLayout:
            selected_beams = self.selected_items(self.mainTable.BeamsLayout, beamList)
        else:
            selected_beams = self.mainTable.BeamsLayout
        if self.mainTable.JoistsLayout:
            selected_joists = self.selected_items(self.mainTable.JoistsLayout, joistList)
        else:
            selected_joists = self.mainTable.JoistsLayout
        if self.mainTable.ShearWallsLayout:
            selected_shearWalls = self.selected_items(self.mainTable.ShearWallsLayout, shearWallList, "shearWall")
        else:
            selected_shearWalls = self.mainTable.ShearWallsLayout
        if self.mainTable.StudWallsLayout:
            selected_studWalls = self.selected_items(self.mainTable.StudWallsLayout, studWallList, "studWall")
        else:
            selected_studWalls = self.mainTable.StudWallsLayout
        self.second_tab.create_tab(selected_posts, selected_beams, selected_joists, selected_shearWalls,
                                   selected_studWalls, opacityList, imagePathList, reportTypes)
        Main(reportTypes, self.result, self.general_information)

        print("REPORTS GENERATED")

    def LayoutOutput(self):
        Posts = self.mainTable.PostsLayout
        Beams = self.mainTable.BeamsLayout
        Joists = self.mainTable.JoistsLayout
        ShearWalls = self.mainTable.ShearWallsLayout
        StudWalls = self.mainTable.StudWallsLayout
        return Posts, Beams, Joists, ShearWalls, StudWalls

    @staticmethod
    def selected_items(all_items, selected_items, name="beam"):
        selected_indexes = []
        for i in range(len(selected_items)):
            story = i + 1
            try:
                all_items_story = all_items[str(story)]
            except:
                all_items_story = all_items["Roof"]
            all_label = all_items_story["label"]
            selected_index_story = []

            for index_number, item in enumerate(selected_items[i]):
                if name == "shearWall" or name == "studWall":
                    item = str(item[2:])
                if item in all_label:
                    selected_index_story.append(all_label.index(item))
            selected_indexes.append(selected_index_story)

        # make an empty copy from all_items to keep format
        all_items_copy = copy.deepcopy(all_items)
        for storyItem in all_items_copy.values():
            for key, value in storyItem.items():
                storyItem[key] = []

        for story, items in all_items.items():
            if story == "Roof":
                i = -1
            else:
                i = int(story) - 1
            try:
                selected_indexes_story = selected_indexes[i]
                for key, value in items.items():
                    for number, item in enumerate(value):
                        if number in selected_indexes_story:
                            all_items_copy[story][key].append(item)
            except:
                pass
        return all_items_copy


def dataExtract(Dict):
    keys = list(Dict.values())[0].keys()
    finalList = []
    for item in keys:
        myList = []
        for value in Dict.values():
            myList.append(value[item])

        finalList.append(myList)
    return finalList


class ReportMainTable:
    def __init__(self, tab_widget, storyCount):
        # output1 = "D://git/Wood/Output/beam_report.db"
        output1 = beamReportPath
        # postPath = "D://git/Wood/Output/post_Input.db"
        postPath = postInputPath
        postTable = "postTable"
        postTableOutput = "POST"
        # beamPath = "D://git/Wood/Output/beam_Input.db"
        beamPath = beamInputPath
        beamTable = "beamTable"
        beamTableOutput = "BEAM"
        # joistPath = "D://git/Wood/Output/joist_Input.db"
        joistPath = joistInputPath
        joistTable = "joistTable"
        joistTableOutput = "JOIST"
        # ShearWallPath = "D://git/Wood/Output/ShearWall_output.db"
        ShearWallPath = shearWallOutputPath
        shearWallTable = "shearwalldesign"
        # StudWallPath = "D://git/Wood/Output/stud_report.db"
        StudWallPath = studWallOutputPath
        studWallTable = "STUD_REPORT_FILE"
        paths = [postPath, beamPath, joistPath, ShearWallPath, StudWallPath]
        path2 = [output1, output1, output1, ShearWallPath, StudWallPath]
        tableNames = [postTable, beamTable, joistTable, shearWallTable, studWallTable]
        tableNames2 = [postTableOutput, beamTableOutput, joistTableOutput, shearWallTable, studWallTable]
        itemNames = ["post", "beam", "joist", "shearWall", "studWall"]
        [self.Posts, self.Beams, self.Joists, self.ShearWalls, self.StudWalls] = list(
            map(self.itemList, paths, tableNames))
        [self.PostsLayout, self.BeamsLayout, self.JoistsLayout, self.ShearWallsLayout, self.StudWallsLayout] = list(
            map(self.itemListLayout, paths, path2, tableNames, tableNames2, itemNames))

        self.StudWalls = self.changeLabel(self.StudWalls, "ST")
        self.ShearWalls = self.changeLabel(self.ShearWalls, "SW")

        self.tab_widget = tab_widget
        self.storyCount = storyCount
        self.checkAll = []
        self.selectAllPost = []
        self.selectAllBeam = []
        self.selectAllJoist = []
        self.selectAllShearWall = []
        self.selectAllStudWall = []
        self.labelAllPost = []
        self.labelAllBeam = []
        self.labelAllJoist = []
        self.labelAllShearWall = []
        self.labelAllStudWall = []
        self.comboBoxes = []
        self.opacity = []
        self.imagePath = []

        for story in range(storyCount):
            # Create tab pages
            tab1 = QWidget()

            # Create layouts for each tab
            mainLayout = QHBoxLayout()
            layout1 = QVBoxLayout()

            # Create checkboxes for tab 1
            checkAll = QCheckBox("Select/Deselect All")
            self.checkAll.append(checkAll)

            # Create spacer item
            spacer = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

            # Set the size policy for the checkAll checkbox
            self.checkAll[story].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.checkAll[story].setFixedHeight(30)  # Set the desired height for the checkAll checkbox

            # Add the checkAll checkbox, spacer, and other elements to the layout

            # Add checkboxes to layout for tab 1
            layout1.addWidget(checkAll, 1)
            postButton, postLabels = self.Element(mainLayout, "Post", self.Posts, story + 1)
            beamButton, beamLabels = self.Element(mainLayout, "Beam", self.Beams, story + 1)
            joistButton, joistLabels = self.Element(mainLayout, "Joist", self.Joists, story + 1)
            shearWallButton, shearWallLabels = self.Element(mainLayout, "Shear Wall", self.ShearWalls, story + 1)
            studWallButton, studWallLabels = self.Element(mainLayout, "Stud Wall", self.StudWalls, story + 1)
            # Create checkboxes for each element in the list
            self.selectAllPost.append(postButton)
            self.selectAllBeam.append(beamButton)
            self.selectAllJoist.append(joistButton)
            self.selectAllShearWall.append(shearWallButton)
            self.selectAllStudWall.append(studWallButton)

            self.labelAllPost.append(postLabels)
            self.labelAllBeam.append(beamLabels)
            self.labelAllJoist.append(joistLabels)
            self.labelAllShearWall.append(shearWallLabels)
            self.labelAllStudWall.append(studWallLabels)

            # background image
            backLayout = QHBoxLayout()
            backLabel = QLabel("Background Image")
            backLayout.addWidget(backLabel)
            imageSelector = ImageSelector()
            backLayout.addWidget(imageSelector)
            opacityLabel = QLabel("Opacity")
            opacity = QDoubleSpinBox()
            opacity.setRange(1, 100)
            opacity.setValue(40)
            backLayout.addWidget(opacityLabel)
            backLayout.addWidget(opacity)

            layout1.addLayout(mainLayout, 20)
            layout1.addItem(spacer)
            layout1.addLayout(backLayout)

            # Set layout for tab 1
            tab1.setLayout(layout1)
            self.opacity.append(opacity)
            self.imagePath.append(imageSelector)

            # Add tabs to the tab widget
            tab_widget.addTab(tab1, f"Story {story + 1}")
            self.checkAll[story].stateChanged.connect(partial(self.checkAllFunc, story))

        # Connect the stateChanged signal after creating all the checkboxes
        # self.checkAll.stateChanged.connect(self.checkAllFunc)

    def checkAllFunc(self, index, checked):
        if checked:
            self.selectAllPost[index].setCheckState(Qt.Checked)
            self.selectAllBeam[index].setCheckState(Qt.Checked)
            self.selectAllJoist[index].setCheckState(Qt.Checked)
            self.selectAllShearWall[index].setCheckState(Qt.Checked)
            self.selectAllStudWall[index].setCheckState(Qt.Checked)
        else:
            self.selectAllPost[index].setCheckState(Qt.Unchecked)
            self.selectAllBeam[index].setCheckState(Qt.Unchecked)
            self.selectAllJoist[index].setCheckState(Qt.Unchecked)
            self.selectAllShearWall[index].setCheckState(Qt.Unchecked)
            self.selectAllStudWall[index].setCheckState(Qt.Unchecked)

    def Element(self, layout, itemName, itemList, story):
        if itemName == "Shear Wall" or itemName == "Stud Wall":
            if story == self.storyCount:
                story = "Roof"
        # Set up combo box 2
        label2 = QLabel(itemName)
        labels = CheckableComboBox()
        items = []
        try:
            for i in itemList.get(str(story)):
                items.append(i)
        except TypeError:
            pass
        # labels.addItems([i for i in itemList.get(str(story))])
        labels.addItems(items)
        selectAllButton = QCheckBox("Select/Deselect")
        selectAllButton.stateChanged.connect(labels.selectDeselectAll)
        h_layout = QHBoxLayout()
        h_layout.addWidget(label2)
        h_layout.addWidget(selectAllButton)
        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addWidget(labels)
        layout.addLayout(v_layout)
        return selectAllButton, labels

    @staticmethod
    def itemList(path, tableName):
        if check_table_exists(path, tableName):

            # Connect to the SQLite database
            conn = sqlite3.connect(path)

            # Create a cursor object
            cursor = conn.cursor()

            # Execute the query
            try:
                cursor.execute(f"SELECT Story, Label FROM {tableName}")
            except sqlite3.OperationalError:
                cursor.execute(f"SELECT Story, Wall_Label FROM {tableName}")

            # Fetch all the rows
            rows = cursor.fetchall()

            # Close the connection
            conn.close()
            stories = set()
            for row in rows:
                stories.add(row[0])
            stories = list(stories)
            stories.sort()
            items = {}
            for story in stories:
                items[story] = set()
                for row in rows:
                    if row[0] == story:
                        items[story].add(row[1])

                items[story] = list(items[story])
                items[story].sort()
                items[story].sort(key=len)
            return items
        else:

            return {}

    @staticmethod
    def changeLabel(items, name):
        newDict = {}
        for story, itemList in items.items():
            newDict[story] = []
            for item in itemList:
                newItem = name + item
                newDict[story].append(newItem)
        return newDict

    @staticmethod
    def itemListLayout(path, pathOutput, tableName, tableOutput, itemName):
        items = {}
        if check_table_exists(path, tableName) and check_table_exists(pathOutput, tableOutput):
            # Connect to the SQLite database
            conn = sqlite3.connect(path)
            connOutput = sqlite3.connect(pathOutput)

            # Create a cursor object
            cursor = conn.cursor()
            cursorOutput = connOutput.cursor()
            if itemName == "post":
                cursor.execute(f"SELECT Story, Label, Coordinate FROM {tableName}")
                rows = cursor.fetchall()
            elif itemName == "joist":
                cursor.execute(f"SELECT Story, Label, Orientation, Coordinate_start, Coordinate_end FROM {tableName}")
                rows = cursor.fetchall()
            elif itemName == "beam":
                cursor.execute(f"SELECT Story, Label, Coordinate_start, Coordinate_end FROM {tableName}")
                rows = cursor.fetchall()
            elif itemName == "shearWall":

                # Fetch all the rows
                cursorOutput.execute(
                    f"SELECT Story, Wall_Label, Coordinate_start, Coordinate_end, Shearwall_Type, Shear_DCR, tension_dcr_left, comp_dcr_left, tension_dcr_right, comp_dcr_right, deflection_dcr_ FROM {tableOutput}")
                rows = cursorOutput.fetchall()

            else:

                # Fetch all the rows
                cursorOutput.execute(
                    f"SELECT STORY, LABEL, Coordinate_start, Coordinate_end, SIZE, dc, dcr_b, d_comb FROM {tableOutput}")
                rows = cursorOutput.fetchall()

            # Close the connection
            conn.close()
            stories = set()
            for row in rows:
                stories.add(row[0])
            stories = list(stories)
            stories.sort()
            for story in stories:
                if itemName == "joist":
                    items[story] = {"label": [], "coordinate": [], "direction": [], "bending_dcr": [], "shear_dcr": [],
                                    "deflection_dcr": [], "size": []}
                elif itemName == "beam":
                    items[story] = {"label": [], "coordinate": [], "bending_dcr": [], "shear_dcr": [],
                                    "deflection_dcr": [], "size": []}
                elif itemName == "post":
                    items[story] = {"label": [], "coordinate": [],
                                    "axial_dcr": [], "size": []}
                elif itemName == "shearWall":
                    items[story] = {"label": [], "coordinate": [], "size": [], "dcr_shear": [],
                                    "dcr_tension": [], "dcr_compression": [], "deflection_dcr": []}
                else:
                    items[story] = {"label": [], "coordinate": [], "size": [], "dcr_comp": [],
                                    "dcr_bend": [], "dcr_comb": []}

                for row in rows:
                    if row[0] == story:
                        try:
                            items[story]["label"].append(row[1])
                        except:
                            print("fuck off")
                        if itemName == "post":
                            cursorOutput.execute(
                                f"SELECT SIZE, axial_dcr FROM {tableOutput} WHERE STORY = ? AND LABEL = ?",
                                [float(story), row[1]])
                            value = cursorOutput.fetchall()
                            if value:
                                [valueMain] = value
                                size = valueMain[0]
                                axial_dcr = valueMain[1]
                            else:
                                axial_dcr = 999
                                size = "-"
                            items[story]["axial_dcr"].append(axial_dcr)
                            items[story]["size"].append(size)
                            items[story]["coordinate"].append(StrToTuple(row[2]))
                        elif itemName == "joist":
                            cursorOutput.execute(
                                f"SELECT SIZE, Bending_dcr, Shear_dcr, defl_dcr FROM {tableOutput} WHERE STORY = ? AND LABEL = ?",
                                [float(story), row[1]])
                            value = cursorOutput.fetchall()
                            if value:
                                [valueMain] = value
                                size = valueMain[0]
                                bending_dcr = valueMain[1]
                                shear_dcr = valueMain[2]
                                deflection_dcr = valueMain[3]
                            else:
                                bending_dcr = 999
                                shear_dcr = 999
                                deflection_dcr = 999
                                size = "-"
                            items[story]["direction"].append(row[2])
                            items[story]["coordinate"].append([StrToTuple(row[3]),
                                                               StrToTuple(row[4])])
                            items[story]["bending_dcr"].append(bending_dcr)
                            items[story]["shear_dcr"].append(shear_dcr)
                            items[story]["deflection_dcr"].append(deflection_dcr)
                            items[story]["size"].append(size)
                        elif itemName == "beam":
                            cursorOutput.execute(
                                f"SELECT SIZE, Bending_dcr, Shear_dcr, defl_dcr FROM {tableOutput} WHERE STORY = ? AND LABEL = ?",
                                [float(story), row[1]])
                            value = cursorOutput.fetchall()
                            if value:
                                [valueMain] = value
                                size = valueMain[0]
                                bending_dcr = valueMain[1]
                                shear_dcr = valueMain[2]
                                deflection_dcr = valueMain[3]
                            else:
                                bending_dcr = 999
                                shear_dcr = 999
                                deflection_dcr = 999
                                size = "-"
                            items[story]["coordinate"].append([StrToTuple(row[2]),
                                                               StrToTuple(row[3])])
                            items[story]["bending_dcr"].append(bending_dcr)
                            items[story]["shear_dcr"].append(shear_dcr)
                            items[story]["deflection_dcr"].append(deflection_dcr)
                            items[story]["size"].append(size)
                        elif itemName == "shearWall":
                            size = row[4]
                            try:
                                maxComp = max(round(float(row[7]), 2), round(float(row[9]), 2))
                            except:
                                maxComp = "-"
                            try:
                                maxTension = max(round(float(row[6]), 2), round(float(row[8]), 2))
                            except:
                                maxTension = "-"
                            shear_dcr = row[5]
                            deflection_dcr = row[10]
                            items[story]["coordinate"].append([StrToTuple(row[2]),
                                                               StrToTuple(row[3])])
                            items[story]["size"].append(size)
                            items[story]["dcr_shear"].append(shear_dcr)
                            items[story]["dcr_tension"].append(maxTension)
                            items[story]["dcr_compression"].append(maxComp)
                            items[story]["dcr_compression"].append(maxComp)
                            items[story]["deflection_dcr"].append(deflection_dcr)
                        else:
                            size = row[4]
                            dcr_comp = row[5]
                            dcr_bend = row[6]
                            dcr_comb = row[7]

                            items[story]["coordinate"].append([StrToTuple(row[2]),
                                                               StrToTuple(row[3])])
                            items[story]["dcr_comp"].append(dcr_comp)
                            items[story]["dcr_bend"].append(dcr_bend)
                            items[story]["dcr_comb"].append(dcr_comb)
                            items[story]["size"].append(size)

                # items[story] = list(items[story])
                # items[story].sort()
                # items[story].sort(key=len)
        return items


def StrToTuple(string):
    b = string.split(",")
    Tuple = (float(b[0].strip()[1:]) * magnification_factor, float(b[1].strip()[:-2]) * magnification_factor)
    return Tuple


def check_table_exists(db_name, table_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Query the sqlite_master table to check for the table's existence
    cursor.execute("""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND name=?;
    """, (table_name,))

    # Fetch one result
    result = cursor.fetchone()

    # Close the connection
    conn.close()

    # Return True if the table exists, else False
    return result is not None
