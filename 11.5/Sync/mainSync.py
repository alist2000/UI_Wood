import math
import sys

sys.path.append(r"D:\git\Wood\UI_Wood\11.5")
from output.beam_output import beam_output
from analysis.main import Main
from Sync.data import Data
from Sync.reaction import Control_reaction, Reaction_On


class mainSync(Data):
    def __init__(self, saveFunc, grid, tabWidgetCount):
        super().__init__()
        self.saveFunc = saveFunc
        self.grid = grid
        self.tabWidgetCount = tabWidgetCount

    def Run_and_Analysis(self):
        for currentTab in range(self.tabWidgetCount):
            self.grid[currentTab].run_control()
        self.saveFunc()
        ControlTab(self.tab)


class ControlGeneralProp:
    def __init__(self, generalProp):
        self.generalProp = generalProp

        pass


class ControlSeismicParameter:
    def __init__(self, seismicPara):
        self.seismicPara = seismicPara

        pass


class ControlTab:
    def __init__(self, tab):
        self.tab = tab
        self.posts = []
        self.beams = []
        self.joists = []
        self.shearWalls = []

        for i, Tab in self.tab.items():
            post = Tab["post"]
            beam = Tab["beam"]
            joist = Tab["joist"]
            shearWall = Tab["shearWall"]
            self.posts.append(post)
            self.beams.append(beam)
            self.joists.append(joist)
            self.shearWalls.append(shearWall)

        beamAnalysisInstance = beamAnalysis(self.beams, self.posts, self.shearWalls)
        print(beamAnalysisInstance.reactionTab)


class beamAnalysis:
    def __init__(self, beam, Posts, ShearWalls):
        self.beam = beam
        self.reactionTab = []
        self.reaction_list = []

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
                        beam_analysis = Main(beam_)

                        Control_reaction(beam_analysis.output.post_output, beamTab[beamNum], self.reaction_list)
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
                        beam_analysis = Main(beam_)

                        Control_reaction(beam_analysis.output.post_output, beamTab[beamNum], self.reaction_list)
                        pass

            reactionInstance.do_post()
            self.reactionTab.append(self.reaction_list)