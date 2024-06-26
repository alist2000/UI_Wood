import sys

from UI_Wood.stableVersion5.output.post_output import post_output
from UI_Wood.stableVersion5.Sync.beamSync import roundAll
from WOOD_DESIGN.mainpost import MainPost
from UI_Wood.stableVersion5.Sync.beamSync import beamAnalysisSync
from UI_Wood.stableVersion5.run.post import PostStoryBy
from PySide6.QtWidgets import QDialog
from UI_Wood.stableVersion5.output.postSql import PostSQL
from UI_Wood.stableVersion5.output.beamSql import beamSQL


class PostSync2:
    def __init__(self, GridClass, beam, Posts, ShearWalls, height, general_information, db,
                 reportPost=False,
                 reportBeam=False, PostStories=[], BeamStories=[]):
        self.GridClass = GridClass
        self.PostStories = PostStories
        self.BeamStories = BeamStories
        self.inputDB = None
        if reportPost:
            for story, post in enumerate(Posts):
                postStoryDesigned = PostStoryBy(self.PostStories[story], GridClass, story + 1)
                if story == len(beam) - 1:
                    self.reportPost = True
                    self.reportBeam = True
                if postStoryDesigned.result == QDialog.Accepted:
                    continue
                else:
                    break
        else:
            postId = 1
            self.inputDB = PostSQL()
            if not reportBeam:
                BeamInputDB = beamSQL()

            for story, post in enumerate(Posts):
                postItem = list(post.values())[0]
                # for story, postItem in post.items():
                post_forBeamDesign = [{story: postItem}]
                beam_forBeamDesign = [beam[story]]
                shearWall_forBeamDesign = [ShearWalls[story]]
                if not reportBeam:
                    beamAnalysisInstance = beamAnalysisSync(beam_forBeamDesign, post_forBeamDesign,
                                                            shearWall_forBeamDesign,
                                                            general_information,
                                                            db, InputDB=BeamInputDB, Story=story)
                    self.BeamStories.append(beamAnalysisInstance.BeamStories[story])
                self.postOutPut = post_output(post_forBeamDesign, height, True, self.inputDB)
                self.inputDB = self.postOutPut.inputDB
                self.reportPost = reportPost
                self.reportBeam = reportBeam
                postStory = []
                for postEdited in self.postOutPut.postProperties:
                    postAnalysis = MainPost(postEdited)
                    if postAnalysis.query:
                        postAnalysis.query.insert(0, postId)
                        postAnalysis.query.insert(1, str(postEdited["story"]))
                        postAnalysis.query.insert(2, postEdited["label"])
                        newQuery = roundAll(postAnalysis.query)
                        db.cursor1.execute(
                            'INSERT INTO POST (ID, STORY, LABEL, HEIGHT, WIDTH, SPECIES, SIZE, Pa_max, fc_psi, Cp, Pa_allow, Fc_allow, axial_dcr, axial_comb, fcperp_demand, fcperp_comb, fcperp_dcr, b, d, Fb, Ft, Fc, Fv, Fc_perp0, E, Emin, A, Sx, Sy, Ix, Iy, rx, ry, kx, ky, reaction1, reaction2, reaction3, reaction4, reaction5, reaction6, reaction7, max_axial_stress1, max_axial_stress2, max_axial_stress3, max_axial_stress4, '
                            'max_axial_stress5, max_axial_stress6, max_axial_stress7, Cd, Ct, Cfb, Cfc, Cft, Ci, Cm, FCE, Fcstar, Fcperp_capacity, bend_capacity, shear_capacity) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                            newQuery)
                        db.conn1.commit()
                        postId += 1
                        postEdited["axial_dcr"] = newQuery[12]
                        postStory.append(postEdited)
                self.PostStories.append(postStory)
                postStoryDesigned = PostStoryBy(postStory, GridClass, story + 1)
                if story == len(beam) - 1:
                    self.reportPost = True
                    self.reportBeam = True
                if postStoryDesigned.result == QDialog.Accepted:
                    continue
                else:
                    break
