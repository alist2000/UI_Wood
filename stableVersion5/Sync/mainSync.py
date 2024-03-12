import copy
import sys
from WOOD_DESIGN.mainshearwall import MainShearWall_version5
from WOOD_DESIGN.reports import Sqlreports
from UI_Wood.stableVersion5.Sync.data import Data
from UI_Wood.stableVersion5.Sync.Image import saveImage
from UI_Wood.stableVersion5.Sync.postSync import PostSync
from UI_Wood.stableVersion5.Sync.joistSync import joistAnalysisSync
from UI_Wood.stableVersion5.Sync.beamSync import BeamSync
from UI_Wood.stableVersion5.Sync.shearWallSync import ShearWallSync, ControlSeismicParameter, ControlMidLine, \
    DataBaseSeismic, EditLabels
from UI_Wood.stableVersion5.Sync.studWallSync import StudWallSync
from UI_Wood.stableVersion5.Sync.Transfer import Transfer, DeleteTransferred
from UI_Wood.stableVersion5.output.shearWallSql import shearWallSQL, DropTables
from UI_Wood.stableVersion5.output.studWallSql import studWallSQL

from UI_Wood.stableVersion5.post_new import magnification_factor
from UI_Wood.stableVersion5.report.ReportGenerator import ReportGeneratorTab
from UI_Wood.stableVersion5.layout.tab_widget2 import secondTabWidgetLayout
from UI_Wood.stableVersion5.Sync.shearWallSync import ShearWallStoryCount
import time
import os


class mainSync(Data):
    def __init__(self, saveFunc, grid, tabWidgetCount):
        super().__init__()
        self.saveFunc = saveFunc
        self.grid = grid
        self.tabWidgetCount = tabWidgetCount
        self.reportGenerator = None
        self.ReportTab = None

    def send_report_generator(self, reportGenerator):
        self.reportGenerator = reportGenerator
        self.reportGenerator.triggered.connect(self.runn)

    def runn(self):
        self.ReportTab = ReportGeneratorTab(self.tabWidgetCount, self.general_information)
        secondTabWidgetLayout(self.general_properties, self.ReportTab)
        print("REPORT GENERATOR BUTTON CLICKED")

    def Run_and_Analysis(self):
        # create report directory
        try:
            os.makedirs('../../Output')  # Windows
        except:
            pass
        try:
            os.makedirs('../../Output/Seismic')  # Windows
        except:
            pass
        try:
            os.makedirs('images')  # Windows
        except:
            pass
        try:
            os.makedirs('images/beam')  # Windows
        except:
            pass
        try:
            os.makedirs('images/post')  # Windows
        except:
            pass
        self.reportGenerator.setEnabled(True)
        midLineDict = {}
        lineLabels = None
        boundaryLineLabels = None
        shearWallsValues = []
        shearWallsKeys = []
        studWallsValues = []
        studWallsKeys = []
        for currentTab in range(self.tabWidgetCount - 1, -1, -1):
            shearWall = self.grid[currentTab].shearWall_instance.shearWall_rect_prop
            studWall = self.grid[currentTab].studWall_instance.studWall_rect_prop
            shearWallsValues.append(list(shearWall.values()))
            shearWallsKeys.append(list(shearWall.keys()))
            studWallsValues.append(list(studWall.values()))
            studWallsKeys.append(list(studWall.keys()))

        shearWallsEdited = EditLabels(shearWallsValues)
        studWallsEdited = EditLabels(studWallsValues, "studWall")
        shearWallsEdited.reverse()
        studWallsEdited.reverse()
        shearWallsKeys.reverse()
        studWallsKeys.reverse()
        for currentTab in range(self.tabWidgetCount - 1, -1, -1):
            shearWallDict = {}
            studWallDict = {}
            for i in range(len(shearWallsEdited[currentTab])):
                try:
                    shearWallDict[shearWallsKeys[currentTab][i]] = shearWallsEdited[currentTab][i]
                except:
                    pass
                try:
                    studWallDict[studWallsKeys[currentTab][i]] = studWallsEdited[currentTab][i]
                except:
                    pass
            self.grid[currentTab].shearWall_instance.shearWall_rect_prop = shearWallDict
            self.grid[currentTab].studWall_instance.studWall_rect_prop = studWallDict
        for currentTab in range(self.tabWidgetCount - 1, -1, -1):
            midLineData, lineLabels, boundaryLineLabels = self.grid[currentTab].run_control()
            if currentTab == self.tabWidgetCount - 1:
                storyName = "Roof"
                ShearWallStoryCount.storyFinal = str(currentTab + 1)

            else:
                storyName = str(currentTab + 1)
            midLineDict[storyName] = midLineData
            saveImage(self.grid, currentTab)

        self.saveFunc()

        generalProp = ControlGeneralProp(self.general_properties)
        TabData = ControlTab(self.tab, generalProp, midLineDict, self.seismic_parameters)

        ControlMidLine(midLineDict)
        print(midLineDict)
        print("FINAL")


class ControlGeneralProp:
    def __init__(self, generalProp):
        self.generalProp = generalProp
        self.height = [i / magnification_factor for i in self.control_inputs(generalProp["height_story"])]
        self.Hn = sum(self.height) / magnification_factor

    @staticmethod
    def control_inputs(item):
        if item:
            # better appearance
            item = [i * magnification_factor for i in item]
        else:
            item = [10 * magnification_factor]  # 10 ft or 10 m

        return item


class ControlTab:
    def __init__(self, tab, generalProp, midLineDict, seismic_parameters):
        self.tab = tab
        self.posts = []
        self.beams = []
        self.joists = []
        self.shearWalls = []
        self.studWalls = []
        self.loadMaps = []
        tabReversed = self.reverse_dict(self.tab)  # top to bottom

        # TRANSFER
        TransferInstance = Transfer()

        # CREATE DB FOR OUTPUT.
        db = Sqlreports()
        db.beam_table()
        db.joist_table()
        db.post_table()

        # drop all shear wall output table
        DropTables("../../../Output/ShearWall_output.db")
        # drop all stud wall output table
        DropTables("../../../Output/stud_report.db")
        # shear wall database input
        shearWall_input_db = shearWallSQL()
        shearWall_input_db.createTable()
        # stud wall database input
        studWall_input_db = studWallSQL()
        studWall_input_db.createTable()
        studWall_input_db.createTable("Exterior")
        studWall_input_db.createTable("Interior4")
        studWall_input_db.createTable("Interior6")

        height_from_top = list(reversed(generalProp.height))
        # seismic parameters database
        seismic_parameters_database = DataBaseSeismic()
        seismic_parameters_database.SeismicParams(seismic_parameters)

        a = time.time()
        beamSync = BeamSync(db, len(tabReversed) - 1)
        postSync = PostSync(db)
        joistSync = joistAnalysisSync(db)
        postTop = None
        shearWallTop = None
        j = 0
        storyNames = []
        for story, Tab in tabReversed.items():
            if j == 0:
                storySW = "Roof"
            else:
                storySW = str(story + 1)
            storyNames.append(storySW)
            shearWall = Tab["shearWall"]
            joist = Tab["joist"]
            self.joists.append(joist)
            self.shearWalls.append(shearWall)
            self.shearWallSync = ShearWallSync([shearWallTop, shearWall], [0, height_from_top[j]], storySW,
                                               shearWall_input_db, True, False)
            shearWallTop = shearWall
            j += 1

        # SHEAR WALL DESIGN
        c = time.time()

        loadMapaArea, loadMapMag = LoadMapAreaNew(midLineDict)

        self.joistArea = JoistSumArea(self.joists)

        # self.storyName = StoryName(self.joists)  # item that I sent is not important, every element is ok.

        seismicInstance = ControlSeismicParameter(seismic_parameters, storyNames, loadMapaArea,
                                                  loadMapMag,
                                                  self.joistArea, seismic_parameters_database)
        shearWallDesign = MainShearWall_version5(seismicInstance.seismicPara, midLineDict
                                                 )
        shearWallExist = shearWallDesign.to_elfp()
        if shearWallExist:
            shearWallDesign.to_diaphragms()
            shearWallDesign.diaphragm_design()
            # shearWallDesign.to_master_shearwall()

        j = 0
        self.shearWalls = []
        self.joists = []

        DropTables("../../../Output/ShearWall_Input.db")
        shearWall_input_db = shearWallSQL()
        shearWall_input_db.createTable()
        shearWallTop = None
        studWallTop = None
        heightTop = None
        storySWTop = None
        for story, Tab in tabReversed.items():
            # post = {i: Tab["post"]}
            post = Tab["post"]
            beam = Tab["beam"]
            joist = Tab["joist"]
            shearWall = Tab["shearWall"]
            studWall = Tab["studWall"]

            if j == 0:
                storySW = "Roof"
            else:
                storySW = story + 1

            # CONTROL STACK
            TransferInstance.StackControl(shearWallTop, shearWall, storySW, "shearWall")
            TransferInstance.StackControl(studWallTop, studWall, storySW, "studWall")
            print("This list should be transferred: ", TransferInstance.transferListShearWall)

            # Transfer Gravity and Earthquake loads from Transferred shearWalls to beams.
            TransferInstance.TransferOtherLoads(shearWallTop, beam, heightTop, "shearWall", storySWTop)

            # Transfer Gravity loads from Transferred studWalls to beams.
            TransferInstance.TransferOtherLoads(studWallTop, beam, heightTop, "studWall")

            # BEAM DESIGN
            c = time.time()
            beamSync.AnalyseDesign(beam, post, shearWall, story)
            d = time.time()
            print(f"Beam analysis story {story} takes ", (d - c) / 60, "Minutes")

            # POST DESIGN
            c = time.time()
            postSync.AnalyseDesign(post, height_from_top[j], story, postTop)
            d = time.time()
            print(f"Post analysis story {story} takes ", (d - c) / 60, "Minutes")

            # JOIST DESIGN
            c = time.time()
            # joistSync.AnalyseDesign(joist, story)
            d = time.time()
            print(f"Joist analysis story {story} takes ", (d - c) / 60, "Minutes")

            # SHEAR WALL DESIGN
            c = time.time()
            # Control load root on shear walls and edit labels.
            self.shearWallSync = ShearWallSync([shearWallTop, shearWall], [heightTop, height_from_top[j]], storySW,
                                               shearWall_input_db)
            TransferInstance.TransferShear(shearWallTop, shearWall, storySW)
            shearWallDesign.to_master_shearwall(storySW, len(tabReversed))
            TransferInstance.get_data_after_run(shearWall, storySW)

            # self.studWallSync = StudWallSync(self.studWalls, height_from_top)
            # loadMapaArea, loadMapMag = LoadMapAreaNew({storySW: midLineDict[str(storySW)]})

            # self.joistArea = JoistSumArea([joist])

            # self.storyName = StoryName(self.joists)  # item that I sent is not important, every element is ok.

            # seismicInstance = ControlSeismicParameter(seismic_parameters, [str(storySW)], loadMapaArea,
            #                                           loadMapMag,
            #                                           self.joistArea, seismic_parameters_database)
            # MainShearall_verion5(seismicInstance.seismicPara, {storySW: midLineDict[str(storySW)]}, height_from_top[j:],
            #                      storySW)
            # add to shearWall pe_main, it is PE_initial or v_design or ect.

            d = time.time()
            print(f"Shear wall analysis story {story} takes ", (d - c) / 60, "Minutes")

            # STUD WALL DESIGN
            self.studWallSync = StudWallSync([studWallTop, studWall], [heightTop, height_from_top[j]], storySW,
                                             studWall_input_db)

            loadMap = Tab["loadMap"]
            self.posts.append(post)
            self.beams.append(beam)
            self.joists.append(joist)
            self.shearWalls.append(shearWall)
            self.studWalls.append(studWall)
            self.loadMaps.append(loadMap)
            postTop = post
            shearWallTop = shearWall
            studWallTop = studWall
            heightTop = height_from_top[j]
            storySWTop = storySW

            j += 1

        # Stud wall design has not been changed yet
        # self.studWallSync = StudWallSync(list(reversed(self.studWalls)), generalProp.height, storySW, studWall_input_db)

        b = time.time()
        print("Total analysis takes ", (b - a) / 60, "Minutes")
        DeleteTransferred(self.beams)
        DeleteTransferred(self.shearWalls)
        DeleteTransferred(self.studWalls)

    @staticmethod
    def reverse_dict(Dict):
        key = list(Dict.keys())
        value = list(Dict.values())
        key.reverse()
        value.reverse()
        newDict = {}
        for k, v in zip(key, value):
            newDict[k] = v

        return newDict


def LoadMapArea(loadMaps):
    areaListFull = []
    magListFull = []
    for i, loadMapTab in enumerate(loadMaps):
        areaList = []
        magList = []
        for loadMap in loadMapTab:
            for load in loadMap["load"]:
                if load["type"] == "Dead Super":
                    areaList.append(loadMap["area"] / (magnification_factor ** 2))
                    magList.append(load["magnitude"])
        areaListFull.append(areaList)
        magListFull.append(magList)

    return areaListFull, magListFull


def LoadMapAreaNew(midLine):
    areaListFull = []
    magListFull = []
    controlLines = [str(i) for i in range(1000)]  # 1000 is just a big number
    for i, loadMapTab in midLine.items():
        magList = []
        areaList = []
        for LoadProp in loadMapTab:
            line = list(LoadProp.keys())[0]
            if line in controlLines:
                for loadMap in LoadProp.values():
                    for load in loadMap:
                        areaList.append(load["area"])
                        magList.append(load["magnitude"])
        areaListFull.append(areaList)
        magListFull.append(magList)

    return areaListFull, magListFull


def JoistSumArea(joists):
    JoistArea = []
    for joistTab in joists:
        area = 0
        for joist in joistTab:
            area += joist["area"] / (magnification_factor ** 2)
        JoistArea.append(area)

    return JoistArea


def StoryName(item):
    storyList = []
    storyNumber = len(item)
    for i in range(storyNumber):
        if i < storyNumber - 1:
            storyList.append(f"{i + 1}")
        else:
            storyList.append("Roof")
    storyList.reverse()
    return storyList
