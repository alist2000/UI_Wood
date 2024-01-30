import sys

sys.path.append(r"D:\git\Wood\UI_Wood\stableVersion5")
sys.path.append(r"D:\git\Wood")
from UI_Wood.stableVersion5.output.joist_output import Joist_output
from UI_Wood.stableVersion5.output.shearWallSql import MidlineSQL, SeismicParamsSQL
from WOOD_DESIGN.mainbeamnew import MainBeam
from WOOD_DESIGN.mainshearwall import MainShearall_verion5
from WOOD_DESIGN.reports import Sqlreports
from UI_Wood.stableVersion5.Sync.data import Data
from UI_Wood.stableVersion5.Sync.Image import saveImage
from UI_Wood.stableVersion5.Sync.postSync import PostSync
from UI_Wood.stableVersion5.Sync.joistSync import joistAnalysisSync
from UI_Wood.stableVersion5.Sync.beamSync import BeamSync
from UI_Wood.stableVersion5.Sync.shearWallSync import ShearWallSync, ControlSeismicParameter, ControlMidLine, \
    NoShearWallLines, MidlineEdit, DataBaseSeismic
from UI_Wood.stableVersion5.Sync.studWallSync import StudWallSync
from UI_Wood.stableVersion5.Sync.Transfer import Transfer
from UI_Wood.stableVersion5.output.shearWallSql import shearWallSQL, DropTables

from UI_Wood.stableVersion5.post_new import magnification_factor
from UI_Wood.stableVersion5.report.ReportGenerator import ReportGeneratorTab
from UI_Wood.stableVersion5.layout.tab_widget2 import secondTabWidgetLayout
from UI_Wood.stableVersion5.Sync.shearWallSync import ShearWallStoryCount
import time


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
        self.reportGenerator.setEnabled(True)
        midLineDict = {}
        lineLabels = None
        boundaryLineLabels = None
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
        # CREATE DB FOR OUTPUT.
        db = Sqlreports()
        db.beam_table()
        db.joist_table()
        db.post_table()

        # drop all shear wall output table
        DropTables("../../../Output/ShearWall_output.db")
        # shear wall database input
        shearWall_input_db = shearWallSQL()
        shearWall_input_db.createTable()
        height_from_top = list(reversed(generalProp.height))
        # seismic parameters database
        seismic_parameters_database = DataBaseSeismic()
        seismic_parameters_database.SeismicParams(seismic_parameters)

        a = time.time()
        beamSync = BeamSync(db, len(tabReversed) - 1)
        postSync = PostSync(db)
        joistSync = joistAnalysisSync(db)
        j = 0
        postTop = None
        shearWallTop = None
        for story, Tab in tabReversed.items():
            # post = {i: Tab["post"]}
            post = Tab["post"]
            beam = Tab["beam"]
            joist = Tab["joist"]
            shearWall = Tab["shearWall"]

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
            joistSync.AnalyseDesign(joist, story)
            d = time.time()
            print(f"Joist analysis story {story} takes ", (d - c) / 60, "Minutes")

            # SHEAR WALL DESIGN
            c = time.time()
            if j == 0:
                storySW = "Roof"
            else:
                storySW = story + 1
            self.shearWallSync = ShearWallSync([shearWallTop, shearWall], height_from_top[j], storySW,
                                               shearWall_input_db)
            # self.studWallSync = StudWallSync(self.studWalls, height_from_top)
            loadMapaArea, loadMapMag = LoadMapAreaNew({storySW: midLineDict[str(storySW)]})

            self.joistArea = JoistSumArea([joist])

            # self.storyName = StoryName(self.joists)  # item that I sent is not important, every element is ok.

            seismicInstance = ControlSeismicParameter(seismic_parameters, [str(storySW)], loadMapaArea,
                                                      loadMapMag,
                                                      self.joistArea, seismic_parameters_database)
            MainShearall_verion5(seismicInstance.seismicPara, {storySW: midLineDict[str(storySW)]}, storySW)
            d = time.time()
            print(f"Shear wall analysis story {story} takes ", (d - c) / 60, "Minutes")

            studWall = Tab["studWall"]
            loadMap = Tab["loadMap"]
            self.posts.append(post)
            self.beams.append(beam)
            self.joists.append(joist)
            self.shearWalls.append(shearWall)
            self.studWalls.append(studWall)
            self.loadMaps.append(loadMap)
            postTop = post
            shearWallTop = shearWall

            j += 1

        b = time.time()
        print("Beam analysis takes ", (b - a) / 60, "Minutes")

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
