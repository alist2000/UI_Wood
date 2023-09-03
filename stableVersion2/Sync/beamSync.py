import sys

sys.path.append(r"D:\git\Wood\UI_Wood\stableVersion2")

from Report_Lab.version1.main import Main
from UI_Wood.stableVersion2.output.beam_output import beam_output
from WOOD_DESIGN.mainbeamnew import MainBeam
from UI_Wood.stableVersion2.Sync.reaction import Control_reaction, Reaction_On
from UI_Wood.stableVersion2.output.beamSql import beamSQL, WriteBeamInputSQL
from Report_Lab.version1.beam.input import BeamInput


class beamAnalysisSync:
    def __init__(self, beam, Posts, ShearWalls, generalInfo, db):
        self.beam = beam
        self.reactionTab = []
        self.reaction_list = []
        beamId = 1
        beamIdInput = 1
        inputDB = beamSQL()
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

            beamDesignedList = []

            # if beam support was an empty list
            if not beam_support:
                beam_support = "True"
            while beam_support:
                if beam_support == "True":
                    beam_support = []
                beam_support, self.reaction_list, beamDesignedList, reactionInstance, beamId = self.DesignPrimaryBeam(
                    beam_support, beamId,
                    self.reaction_list,
                    tabNumber, db, beamTab,
                    Posts, ShearWalls,
                    beamDesignedList)

            # for beamNum, beam_ in enumerate(beamOutput.beamProperties):
            #     # beam with no support are empty(False)
            #     if beam_:
            #         label = beam_["label"]
            #
            #         if label not in beam_support:
            #             # BEAM SHOULD ANALYZE FIRST
            #             beam_analysis = MainBeam(beam_)
            #             if beam_analysis.query[0] != "No Section Was Adequate":
            #                 # WriteBeamInputSQL(beam_, str(tabNumber + 1), beamId, inputDB)
            #                 beam_analysis.query.insert(0, str(beamId))
            #                 beam_analysis.query.insert(1, str(tabNumber + 1))
            #                 beam_analysis.query.insert(2, beam_["label"])
            #
            #                 db.cursor1.execute(
            #                     'INSERT INTO BEAM (ID, STORY, LABEL, LENGTH, SIZE,Vmax, Mmax, Fb_actual, Fb_allow, Fv_actual, Fv_allow, Deflection_actual, Deflection_allow, Bending_dcr, Shear_dcr,DIST_D, DIST_D_range, DIST_L, DIST_L_range, DIST_LR, DIST_LR_range, DIST_E, DIST_E_range, P_D, P_D_range, P_L, P_L_range, P_LR, P_LR_range, P_E, P_E_range,RD, RL, RLr, RE) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            #                     beam_analysis.query)
            #                 db.conn1.commit()
            #
            #                 Control_reaction(beam_analysis.output.post_output, beamTab[beamNum], self.reaction_list)
            #                 beamId += 1
            #                 pass

            # # assign beam reactions
            # for reaction in self.reaction_list:
            #     assign_beam_reaction(reaction, self.beam)

            # reactionInstance = Reaction_On(beamTab, Posts[tabNumber], ShearWalls[tabNumber], self.reaction_list)
            # reactionInstance.do_beam()

            beamOutput = beam_output(beamTab)
            for beamNum, beam_ in enumerate(beamOutput.beamProperties):
                InputReport = BeamInput(beam_, generalInfo)
                value = InputReport.input
                report = Main(value, value, value,
                              f"D:/git/Wood/UI_Wood/stableVersion1/report/Beam_output_{beam_['label']}_story_{str(i)}.pdf")
                # beam with no support are empty(False)
                if beam_:
                    WriteBeamInputSQL(beam_, str(tabNumber + 1), beamIdInput, inputDB)
                    beamIdInput += 1
                    if beam_["label"] not in beamDesignedList:
                        beam_analysis = MainBeam(beam_)
                        if beam_analysis.query[0] != "No Section Was Adequate":
                            # WriteBeamInputSQL(beam_, str(tabNumber + 1), beamId, inputDB)

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

    @staticmethod
    def DesignPrimaryBeam(beam_support, beamId, reaction_list, tabNumber, db, beamTab, Posts, ShearWalls, beamDesigned):
        beamOutput = beam_output(beamTab)
        for beamNum, beam_ in enumerate(beamOutput.beamProperties):
            # beam with no support are empty(False)
            if beam_:
                label = beam_["label"]

                if label not in beam_support and label not in beamDesigned:
                    # BEAM SHOULD ANALYZE FIRST
                    beam_analysis = MainBeam(beam_)
                    beamDesigned.append(label)
                    if beam_analysis.query[0] != "No Section Was Adequate":
                        # WriteBeamInputSQL(beam_, str(tabNumber + 1), beamId, inputDB)
                        beam_analysis.query.insert(0, str(beamId))
                        beam_analysis.query.insert(1, str(tabNumber + 1))
                        beam_analysis.query.insert(2, beam_["label"])

                        db.cursor1.execute(
                            'INSERT INTO BEAM (ID, STORY, LABEL, LENGTH, SIZE,Vmax, Mmax, Fb_actual, Fb_allow, Fv_actual, Fv_allow, Deflection_actual, Deflection_allow, Bending_dcr, Shear_dcr,DIST_D, DIST_D_range, DIST_L, DIST_L_range, DIST_LR, DIST_LR_range, DIST_E, DIST_E_range, P_D, P_D_range, P_L, P_L_range, P_LR, P_LR_range, P_E, P_E_range,RD, RL, RLr, RE) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                            beam_analysis.query)
                        db.conn1.commit()

                        Control_reaction(beam_analysis.output.post_output, beamTab[beamNum], reaction_list)
                        beamId += 1
                        pass

        # # assign beam reactions
        # for reaction in self.reaction_list:
        #     assign_beam_reaction(reaction, self.beam)

        reactionInstance = Reaction_On(beamTab, Posts[tabNumber], ShearWalls[tabNumber], reaction_list)
        reactionInstance.do_beam()

        reactionPass = []
        for reaction in reaction_list:
            reactionLabel = reaction["label"]
            reactionPass.append(reactionLabel)
        new_beam_support = []
        for beamLabel in beam_support:
            if beamLabel not in reactionPass:
                new_beam_support.append(beamLabel)

        return new_beam_support, reaction_list, beamDesigned, reactionInstance, beamId
