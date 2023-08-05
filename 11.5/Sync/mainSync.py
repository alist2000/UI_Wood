import sys

sys.path.append(r"D:\git\Wood\UI_Wood\11.5")
sys.path.append(r"D:\git\Wood")
from output.beam_output import beam_output
from output.post_output import post_output
from output.shearWall_output import ShearWall_output, EditLabel
from WOOD_DESIGN.mainpost import MainPost
from WOOD_DESIGN.mainbeam import MainBeam
from WOOD_DESIGN.reports import Sqlreports
from Sync.data import Data
from Sync.Image import saveImage
from Sync.reaction import Control_reaction, Reaction_On
from post_new import magnification_factor


class mainSync(Data):
    def __init__(self, saveFunc, grid, tabWidgetCount):
        super().__init__()
        self.saveFunc = saveFunc
        self.grid = grid
        self.tabWidgetCount = tabWidgetCount

    def Run_and_Analysis(self):
        midLineDict = {}
        for currentTab in range(self.tabWidgetCount):
            midLineData = self.grid[currentTab].run_control()
            midLineDict[str(currentTab)] = midLineData
            saveImage(self.grid, currentTab)

        self.saveFunc()
        generalProp = ControlGeneralProp(self.general_properties)
        TabData = ControlTab(self.tab, generalProp)
        LoadMapaArea = TabData.loadMapArea
        LoadMapMag = TabData.loadMapMag
        JoistArea = TabData.joistArea
        storyName = TabData.storyName
        seismicInstance = ControlSeismicParameter(self.seismic_parameters, storyName, LoadMapaArea, LoadMapMag,
                                                  JoistArea)
        print(seismicInstance.seismicPara)
        print(midLineDict)
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


class ControlSeismicParameter:
    def __init__(self, seismicPara, storyName, areaLoad, magLoad, areaJoist):
        self.seismicPara = seismicPara
        self.seismicPara["story_name"] = storyName
        self.seismicPara["load_area"] = areaLoad
        self.seismicPara["load_magnitude"] = magLoad
        self.seismicPara["joist_area"] = areaJoist


class ControlTab:
    def __init__(self, tab, generalProp):
        self.tab = tab
        self.posts = []
        self.beams = []
        self.joists = []
        self.shearWalls = []
        self.loadMaps = []

        for i, Tab in self.tab.items():
            post = {i: Tab["post"]}
            beam = Tab["beam"]
            joist = Tab["joist"]
            shearWall = Tab["shearWall"]
            loadMap = Tab["loadMap"]
            self.posts.append(post)
            self.beams.append(beam)
            self.joists.append(joist)
            self.shearWalls.append(shearWall)
            self.loadMaps.append(loadMap)

        # CREATE DB FOR OUTPUT.
        db = Sqlreports()
        db.beam_table()
        db.post_table()

        # BEAM
        # beamAnalysisInstance = beamAnalysisSync(self.beams, self.posts, self.shearWalls, db)

        # POST
        # PostSync(self.posts, generalProp.height, db)

        # SHEAR WALL
        self.loadMapArea, self.loadMapMag = LoadMapArea(self.loadMaps)
        self.joistArea = JoistSumArea(self.joists)
        self.storyName = StoryName(self.joists)  # item that I sent is not important, every element is ok.
        ShearWallSync(self.shearWalls, generalProp.height, db)

        # print(beamAnalysisInstance.reactionTab)
        # print("ALL POSTS : ", self.posts)
        # print("ALL BEAMS : ", self.beams)
        # print("ALL SHEAR WALLS : ", self.shearWalls)


class beamAnalysisSync:
    def __init__(self, beam, Posts, ShearWalls, db):
        self.beam = beam
        self.reactionTab = []
        self.reaction_list = []
        beamId = 1

        for i, beamTab in enumerate(beam):
            self.reaction_list.clear()
            beamOutput = beam_output(beamTab)

            tabNumber = i
            beam_support = []

            for Beam in beamTab:
                beamSupport = Beam["support"]
                for support in beamSupport:
                    supportLabel = support["label"]
                    if "B" in supportLabel:
                        beam_support.append(supportLabel)

            for beamNum, beam_ in enumerate(beamOutput.beamProperties):
                # beam with no support are empty(False)
                if beam_:
                    label = beam_["label"]
                    if label not in beam_support:
                        # BEAM SHOULD ANALYZE FIRST
                        beam_analysis = MainBeam(beam_)
                        if beam_analysis.query[0] != "No Section Was Adequate":
                            beam_analysis.query.insert(0, str(beamId))
                            beam_analysis.query.insert(1, str(tabNumber + 1))
                            beam_analysis.query.insert(2, beam_["label"])

                            db.cursor1.execute(
                                'INSERT INTO BEAM (ID, STORY, LABEL, LENGTH, SIZE,Vmax, Mmax, Fb_actual, Fb_allow, Fv_actual, Fv_allow, Deflection_actual, Deflection_allow, Bending_dcr, Shear_dcr,DIST_D, DIST_D_range, DIST_L, DIST_L_range, DIST_LR, DIST_LR_range, DIST_E, DIST_E_range, P_D, P_D_range, P_L, P_L_range, P_LR, P_LR_range, P_E, P_E_range,RD, RL, RLr, RE) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                beam_analysis.query)
                            db.conn1.commit()

                            Control_reaction(beam_analysis.output.post_output, beamTab[beamNum], self.reaction_list)
                            beamId += 1
                            pass

            # # assign beam reactions
            # for reaction in self.reaction_list:
            #     assign_beam_reaction(reaction, self.beam)

            reactionInstance = Reaction_On(beamTab, Posts[tabNumber], ShearWalls[tabNumber], self.reaction_list)
            reactionInstance.do_beam()

            beamOutput = beam_output(beamTab)
            for beamNum, beam_ in enumerate(beamOutput.beamProperties):
                # beam with no support are empty(False)
                if beam_:
                    if beam_["label"] in beam_support:
                        beam_analysis = MainBeam(beam_)
                        if beam_analysis.query[0] != "No Section Was Adequate":
                            beam_analysis.query.insert(0, str(beamId))
                            beam_analysis.query.insert(1, str(tabNumber + 1))
                            beam_analysis.query.insert(2, beam_["label"])

                            db.cursor1.execute(
                                'INSERT INTO BEAM (ID, STORY, LABEL, LENGTH, SIZE,Vmax, Mmax, Fb_actual, Fb_allow, Fv_actual, Fv_allow, Deflection_actual, Deflection_allow, Bending_dcr, Shear_dcr,DIST_D, DIST_D_range, DIST_L, DIST_L_range, DIST_LR, DIST_LR_range, DIST_E, DIST_E_range, P_D, P_D_range, P_L, P_L_range, P_LR, P_LR_range, P_E, P_E_range,RD, RL, RLr, RE) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                beam_analysis.query)
                            db.conn1.commit()
                            Control_reaction(beam_analysis.output.post_output, beamTab[beamNum], self.reaction_list)
                            beamId += 1

                            pass

            reactionInstance.do_post()
            self.reactionTab.append(self.reaction_list)


class PostSync:
    def __init__(self, posts, height, db):
        self.postOutPut = post_output(posts, height)
        print(self.postOutPut.postProperties)
        postId = 1
        for post in self.postOutPut.postProperties:
            postAnalysis = MainPost(post)
            postAnalysis.query.insert(0, postId)
            postAnalysis.query.insert(1, str(post["story"]))
            postAnalysis.query.insert(2, post["label"])
            db.cursor1.execute(
                'INSERT INTO POST (ID, STORY,LABEL, SIZE, GRADE, Pa_k, fc_psi, Cp, P_allow, Fcc_psi, DCR, Load_comb, Fc_perp, Load_comb_sill, DCR_sill) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                postAnalysis.query)
            db.conn1.commit()
            postId += 1


class ShearWallSync:
    def __init__(self, shearWall, height, db):
        shearWallEditedInstance = EditLabel(shearWall)
        shearWallEdited = list(reversed(shearWallEditedInstance.shearWalls_rev))
        self.shearWallOutPut = ShearWall_output(shearWallEdited, height)
        print("*** SHEAR PROP IS HERE", self.shearWallOutPut.shearWallProperties)
        shearWallId = 1


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
            storyList.append(f"Story{i + 1}")
        else:
            storyList.append("Roof")
    storyList.reverse()
    return storyList
