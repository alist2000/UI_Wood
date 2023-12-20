import sys

sys.path.append(r"D:\git\Wood\UI_Wood\stableVersion4")

from UI_Wood.stableVersion4.output.beam_output import beam_output
from WOOD_DESIGN.mainbeamnewupdated import MainBeam
from UI_Wood.stableVersion4.Sync.reaction import Control_reaction, Reaction_On
from UI_Wood.stableVersion4.output.beamSql import beamSQL, WriteBeamInputSQL
from UI_Wood.stableVersion4.run.beam import BeamStoryBy
from time import sleep
from PySide6.QtWidgets import QDialog


class beamAnalysisSync:
    def __init__(self, beam, Posts, ShearWalls, generalInfo, db, GridClass=None, storyBy=False, report=False,
                 BeamStories=[], InputDB=None, Story=0):
        self.beam = beam
        self.reactionTab = []
        self.reaction_list = []
        beamId = 1
        beamIdInput = 1
        self.BeamStories = BeamStories
        self.report = report
        self.InputDB = InputDB
        self.Story = Story
        if report:
            for i, beamTab in enumerate(beam):
                if storyBy:
                    storyByStoryInstance = BeamStoryBy(self.BeamStories[i], GridClass, i + 1)
                    if i == len(beam) - 1:
                        self.report = True
                    if storyByStoryInstance.result == QDialog.Accepted:
                        continue
                    else:
                        break
        else:
            if InputDB:
                inputDB = self.InputDB
            else:
                inputDB = beamSQL()
            # for i, beamTab in enumerate(beam):
            #     beamOutput = beam_output(beamTab)
            #     for beamNum, beam_ in enumerate(beamOutput.beamProperties):
            #         # beam with no support are empty(False)
            #         if beam_:
            #             WriteBeamInputSQL(beam_, str(i + 1), beamIdInput, inputDB)
            #             beamIdInput += 1

            for i, beamTab in enumerate(beam):
                BeamStory = []
                self.reaction_list.clear()
                if InputDB:
                    tabNumber = Story
                else:
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
                        beamDesignedList, BeamStory)

                beamOutput = beam_output(beamTab)
                for beamNum, beam_ in enumerate(beamOutput.beamProperties):
                    # beam with no support are empty(False)
                    if beam_:
                        # WriteBeamInputSQL(beam_, str(tabNumber + 1), beamIdInput, inputDB)
                        # beamIdInput += 1
                        if beam_["label"] not in beamDesignedList:
                            beam_analysis = MainBeam(beam_)
                            if beam_analysis.query[0] != "No Section Was Adequate":
                                figs = beam_analysis.plots
                                figs[0].write_image(
                                    f"images/beam/Beam_external_story{tabNumber + 1}_label_{beam_['label']}.png")
                                figs[1].write_image(
                                    f"images/beam/Beam_internal_story{tabNumber + 1}_label_{beam_['label']}.png")
                                # WriteBeamInputSQL(beam_, str(tabNumber + 1), beamId, inputDB)

                                beam_analysis.query.insert(0, str(beamId))
                                beam_analysis.query.insert(1, str(tabNumber + 1))
                                beam_analysis.query.insert(2, beam_["label"])
                                newQuery = roundAll(beam_analysis.query)

                                db.cursor1.execute(
                                    'INSERT INTO BEAM (ID, STORY, LABEL, SPECIES, SPANS, LENGTH, LOAD_COMB, SIZE, Vmax, Mmax, Fb_actual, Fb_allow, Fv_actual, Fv_allow, Deflection_actual, Deflection_allow, Bending_dcr, Shear_dcr, defl_dcr, DIST_D, DIST_D_range, DIST_L, DIST_L_range, DIST_LR, DIST_LR_range, DIST_E, DIST_E_range, DIST_S, DIST_S_range, P_D, P_D_range, P_L, P_L_range, P_LR, P_LR_range, P_E, P_E_range, P_S, P_S_range, RD, RL, RLr, RE, RS, Mmax_loc, Vmax_loc, d, b, Fb, Ft, Fc, Fv, Fcperp, E, Emin, A, Sx, Sy, Ix, Iy, Cd, Ct, Cfb, Cfc, Cft, Cfu, Ci, Ciperp, Cr, Cb, Cl, Fcperp_cap, Fcperp_dem) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                                    newQuery)
                                db.conn1.commit()
                                beam_["bending_dcr"] = newQuery[16]
                                beam_["shear_dcr"] = newQuery[17]
                                beam_["deflection_dcr"] = newQuery[18]
                                beam_["size"] = newQuery[7]
                                BeamStory.append(beam_)
                            Control_reaction(beam_analysis.output.post_output, beamTab[beamNum], self.reaction_list)
                            beamId += 1
                self.BeamStories.append(BeamStory)
                reactionInstance.do_post()
                self.reactionTab.append(self.reaction_list)
                if storyBy:
                    storyByStoryInstance = BeamStoryBy(BeamStory, GridClass, i + 1)
                    if i == len(beam) - 1:
                        self.report = True
                    if storyByStoryInstance.result == QDialog.Accepted:
                        continue
                    else:
                        break
            for i, beamTab in enumerate(beam):
                beamOutput = beam_output(beamTab)
                for beamNum, beam_ in enumerate(beamOutput.beamProperties):
                    # beam with no support are empty(False)
                    if beam_:
                        WriteBeamInputSQL(beam_, str(i + 1), beamIdInput, inputDB)
                        beamIdInput += 1

    @staticmethod
    def DesignPrimaryBeam(beam_support, beamId, reaction_list, tabNumber, db, beamTab, Posts, ShearWalls, beamDesigned,
                          BeamStory):
        if len(Posts) == 1 and len(ShearWalls) == 1:
            # we will be here in two situation:
            # 1) if we are use beamSync class in designing posts, story by story.
            # 2) if we have just one story.
            i = 0
        else:
            i = tabNumber
        beamOutput = beam_output(beamTab)
        for beamNum, beam_ in enumerate(beamOutput.beamProperties):
            # beam with no support are empty(False)
            if beam_:
                # WriteBeamInputSQL(beam_, str(tabNumber + 1), beamId, inputDB)
                label = beam_["label"]

                if label not in beam_support and label not in beamDesigned:
                    # BEAM SHOULD ANALYZE FIRST
                    beam_analysis = MainBeam(beam_)

                    beamDesigned.append(label)
                    if beam_analysis.query[0] != "No Section Was Adequate" and beam_analysis.query[0] != 'NOT FOUND':
                        figs = beam_analysis.plots
                        figs[0].write_image(
                            f"images/beam/Beam_external_story{tabNumber + 1}_label_{beam_['label']}.png")
                        figs[1].write_image(
                            f"images/beam/Beam_internal_story{tabNumber + 1}_label_{beam_['label']}.png")
                        beam_analysis.query.insert(0, str(beamId))
                        beam_analysis.query.insert(1, str(tabNumber + 1))
                        beam_analysis.query.insert(2, beam_["label"])
                        newQuery = roundAll(beam_analysis.query)

                        db.cursor1.execute(
                            'INSERT INTO BEAM (ID, STORY, LABEL, SPECIES, SPANS, LENGTH, LOAD_COMB, SIZE, Vmax, Mmax, Fb_actual, Fb_allow, Fv_actual, Fv_allow, Deflection_actual, Deflection_allow, Bending_dcr, Shear_dcr, defl_dcr, DIST_D, DIST_D_range, DIST_L, DIST_L_range, DIST_LR, DIST_LR_range, DIST_E, DIST_E_range, DIST_S, DIST_S_range, P_D, P_D_range, P_L, P_L_range, P_LR, P_LR_range, P_E, P_E_range, P_S, P_S_range, RD, RL, RLr, RE, RS, Mmax_loc, Vmax_loc, d, b, Fb, Ft, Fc, Fv, Fcperp, E, Emin, A, Sx, Sy, Ix, Iy, Cd, Ct, Cfb, Cfc, Cft, Cfu, Ci, Ciperp, Cr, Cb, Cl, Fcperp_cap, Fcperp_dem) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                            newQuery)
                        db.conn1.commit()
                        beam_["bending_dcr"] = newQuery[16]
                        beam_["shear_dcr"] = newQuery[17]
                        beam_["deflection_dcr"] = newQuery[18]
                        beam_["size"] = newQuery[7]
                        BeamStory.append(beam_)

                    Control_reaction(beam_analysis.output.post_output, beamTab[beamNum], reaction_list)
                    # WriteBeamInputSQL(beam_, str(tabNumber + 1), beamId, inputDB)
                    beamId += 1

        # # assign beam reactions
        # for reaction in self.reaction_list:
        #     assign_beam_reaction(reaction, self.beam)

        reactionInstance = Reaction_On(beamTab, Posts[i], ShearWalls[i], reaction_list)
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


def roundAll(myList):
    newList = []
    for i in myList:
        try:
            newList.append(
                round(float(i), 2)
            )
        except:
            newList.append(i)
    return newList


def handle_finished(result):
    if result == QDialog.Accepted:
        print("User clicked Yes")
    else:
        print("User clicked No or closed the dialog")
