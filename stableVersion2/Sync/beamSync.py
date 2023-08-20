import sys

sys.path.append(r"D:\git\Wood\UI_Wood\stableVersion2")

from Report_Lab.version1.main import Main
from UI_Wood.stableVersion2.output.beam_output import beam_output
from WOOD_DESIGN.mainbeamnew import MainBeam
from UI_Wood.stableVersion2.Sync.reaction import Control_reaction, Reaction_On
from Report_Lab.version1.beam.input import BeamInput


class beamAnalysisSync:
    def __init__(self, beam, Posts, ShearWalls, generalInfo, db):
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
                InputReport = BeamInput(beam_, generalInfo)
                value = InputReport.input
                report = Main(value, value, value,
                              f"D:/git/Wood/UI_Wood/stableVersion1/report/Beam_output_{beam_['label']}_story_{str(i)}.pdf")
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
