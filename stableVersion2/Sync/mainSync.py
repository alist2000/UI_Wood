import sys

sys.path.append(r"D:\git\Wood\UI_Wood\stableVersion2")
sys.path.append(r"D:\git\Wood")
from UI_Wood.stableVersion2.output.joist_output import Joist_output
from UI_Wood.stableVersion2.output.shearWallSql import MidlineSQL, SeismicParamsSQL
from WOOD_DESIGN.mainbeamnew import MainBeam
from WOOD_DESIGN.mainshearwall import MainShearwall
from WOOD_DESIGN.reports import Sqlreports
from UI_Wood.stableVersion2.Sync.data import Data
from UI_Wood.stableVersion2.Sync.Image import saveImage
from UI_Wood.stableVersion2.Sync.postSync import PostSync
from UI_Wood.stableVersion2.Sync.beamSync import beamAnalysisSync
from UI_Wood.stableVersion2.Sync.shearWallSync import ShearWallSync, ControlSeismicParameter, ControlMidLine, \
    NoShearWallLines, MidlineEdit
from UI_Wood.stableVersion2.Sync.studWallSync import StudWallSync
from UI_Wood.stableVersion2.post_new import magnification_factor
from UI_Wood.stableVersion2.report.ReportGenerator import ReportGeneratorTab
from UI_Wood.stableVersion2.layout.tab_widget2 import secondTabWidgetLayout


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
        self.ReportTab = ReportGeneratorTab(self.tabWidgetCount)
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
            else:
                storyName = str(currentTab + 1)
            midLineDict[storyName] = midLineData
            saveImage(self.grid, currentTab)

        self.saveFunc()

        generalProp = ControlGeneralProp(self.general_properties)
        TabData = ControlTab(self.tab, generalProp, self.general_information)
        shearWallExistLine = TabData.shearWallSync.shearWallOutPut.shearWallExistLine
        # LoadMapaAreaBefore = TabData.loadMapArea
        # LoadMapMagBefore = TabData.loadMapMag
        JoistArea = TabData.joistArea
        storyName = TabData.storyName
        noShearWallLines = NoShearWallLines(shearWallExistLine, set(lineLabels))
        midLineInstance = MidlineEdit(lineLabels, midLineDict, noShearWallLines)
        midLineDictEdited = midLineInstance.newMidline
        # boundaryLineNoShearWall = midLineInstance.boundaryLineNoShearWall
        LoadMapaArea, LoadMapMag = LoadMapAreaNew(midLineDictEdited)
        seismicInstance = ControlSeismicParameter(self.seismic_parameters, storyName, LoadMapaArea, LoadMapMag,
                                                  JoistArea)
        ControlMidLine(midLineDictEdited)

        print(seismicInstance.seismicPara)
        print(midLineDictEdited)
        # MainShearwall(seismicInstance.seismicPara, midLineDictEdited)

        print("FINAL")


class ControlGeneralProp:
    def __init__(self, generalProp):
        self.generalProp = generalProp
        self.y = self.control_inputs(generalProp["h_spacing"])
        self.x = self.control_inputs(generalProp["v_spacing"])
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
    def __init__(self, tab, generalProp, generalInfo):
        self.tab = tab
        self.posts = []
        self.beams = []
        self.joists = []
        self.shearWalls = []
        self.studWalls = []
        self.loadMaps = []

        for i, Tab in self.tab.items():
            post = {i: Tab["post"]}
            beam = Tab["beam"]
            joist = Tab["joist"]
            shearWall = Tab["shearWall"]
            studWall = Tab["studWall"]
            loadMap = Tab["loadMap"]
            self.posts.append(post)
            self.beams.append(beam)
            self.joists.append(joist)
            self.shearWalls.append(shearWall)
            self.studWalls.append(studWall)
            self.loadMaps.append(loadMap)

        # CREATE DB FOR OUTPUT.
        db = Sqlreports()
        db.beam_table()
        db.post_table()

        # BEAM
        beamAnalysisInstance = beamAnalysisSync(self.beams, self.posts, self.shearWalls, generalInfo, db)

        # POST
        PostSync(self.posts, generalProp.height, generalInfo, db)

        # JOIST
        joistOutput = Joist_output(self.joists)

        # SHEAR WALL
        # self.loadMapArea, self.loadMapMag = LoadMapArea(self.loadMaps)
        self.joistArea = JoistSumArea(self.joists)
        self.storyName = StoryName(self.joists)  # item that I sent is not important, every element is ok.
        self.shearWallSync = ShearWallSync(self.shearWalls, generalProp.height, db)
        self.studWallSync = StudWallSync(self.studWalls, generalProp.height)

        # print(beamAnalysisInstance.reactionTab)
        # print("ALL POSTS : ", self.posts)
        # print("ALL BEAMS : ", self.beams)
        print("ALL SHEAR WALLS : ", self.shearWalls)


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
