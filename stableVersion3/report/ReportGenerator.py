from PySide6.QtWidgets import QApplication, QHBoxLayout, QCheckBox, QWidget, QTabWidget, QVBoxLayout, QPushButton, \
    QLabel, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt
from functools import partial

import sqlite3
from UI_Wood.stableVersion3.replicate import CheckableComboBox
from UI_Wood.stableVersion3.post_new import magnification_factor

from Report_Lab.version3.main import Main


class ReportGeneratorTab(QWidget):
    def __init__(self, storyCount, general_information):
        super(ReportGeneratorTab, self).__init__()
        self.general_information = general_information
        self.result = {}
        self.setWindowTitle("Report Generation")

        layout = QHBoxLayout()
        v_layout = QVBoxLayout()

        # Create checkboxes
        self.option1 = QCheckBox("Compact Summary")
        self.option2 = QCheckBox("Summary")
        self.option3 = QCheckBox("Detail")
        self.generate = QPushButton("Generate")

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
               background: #A8DF8E;
               image: url(D://git/Wood/UI_Wood/stableVersion3/images/check.png);
           }
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

        # report type
        reportTypes = [i.text() for i in [self.option1, self.option2, self.option3] if i.isChecked()]

        self.result["post"] = postList
        self.result["beam"] = beamList
        self.result["joist"] = joistList
        self.result["shearWall"] = shearWallList
        self.result["studWall"] = studWallList

        Main(reportTypes, self.result, self.general_information)

        print("REPORTS GENERATED")

    def LayoutOutput(self):
        Posts = self.mainTable.PostsLayout
        Beams = self.mainTable.BeamsLayout
        Joists = self.mainTable.JoistsLayout
        ShearWalls = self.mainTable.ShearWallsLayout
        StudWalls = self.mainTable.StudWallsLayout
        return Posts, Beams, Joists, ShearWalls, StudWalls


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
        output1 = "D://git/Wood/Output/beam_report.db"
        postPath = "D://git/Wood/Output/post_Input.db"
        postTable = "postTable"
        postTableOutput = "POST"
        beamPath = "D://git/Wood/Output/beam_Input.db"
        beamTable = "beamTable"
        beamTableOutput = "BEAM"
        joistPath = "D://git/Wood/Output/joist_Input.db"
        joistTable = "joistTable"
        joistTableOutput = "JOIST"
        ShearWallPath = "D://git/Wood/Output/ShearWall_output.db"
        shearWallTable = "shearwalldesign"
        StudWallPath = "D://git/Wood/Output/stud_report.db"
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

            layout1.addLayout(mainLayout, 20)
            layout1.addItem(spacer)

            # self.checkAll.stateChanged.connect(self.checkAllFunc)
            print("hoy hoy hoy")

            # Set layout for tab 1
            tab1.setLayout(layout1)

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
            cursorOutput.execute(f"SELECT Story, Wall_Label, Coordinate_start, Coordinate_end, Shearwall_Type, Shear_DCR, tension_dcr_left, comp_dcr_left, tension_dcr_right, comp_dcr_right, deflection_dcr_ FROM {tableOutput}")
            rows = cursorOutput.fetchall()

        else:

            # Fetch all the rows
            cursorOutput.execute(f"SELECT STORY, LABEL, Coordinate_start, Coordinate_end, SIZE, dc, dcr_b, d_comb FROM {tableOutput}")
            rows = cursorOutput.fetchall()



        # Close the connection
        conn.close()
        stories = set()
        for row in rows:
            stories.add(row[0])
        stories = list(stories)
        stories.sort()
        items = {}
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
