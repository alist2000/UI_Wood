import sys

from UI_Wood.stableVersion5.output.post_output import post_output
from UI_Wood.stableVersion5.Sync.beamSync import roundAll
from WOOD_DESIGN.mainpost import MainPost
from UI_Wood.stableVersion5.output.postSql import PostSQL, WritePostInputSQL


class PostSync:
    def __init__(self, output_db):
        self.output_db = output_db
        self.input_db = PostSQL()
        self.postId = 1
        self.postIdInput = 1
        self.PostStories = []

    def AnalyseDesign(self, post, height, story, postTop=None):
        postOutPut = post_output(post, height, postTop, story)
        postStory = []
        for post in postOutPut.postProperties:
            WritePostInputSQL(post, self.postIdInput, self.input_db)
            self.postIdInput += 1
            postAnalysis = MainPost(post)
            if postAnalysis.query:
                postAnalysis.query.insert(0, self.postId)
                postAnalysis.query.insert(1, str(post["story"]))
                postAnalysis.query.insert(2, post["label"])
                newQuery = roundAll(postAnalysis.query)
                self.output_db.cursor1.execute(
                    'INSERT INTO POST (ID, STORY, LABEL, HEIGHT, WIDTH, SPECIES, SIZE, Pa_max, fc_psi, Cp, Pa_allow, Fc_allow, axial_dcr, axial_comb, fcperp_demand, fcperp_comb, fcperp_dcr, b, d, Fb, Ft, Fc, Fv, Fc_perp0, E, Emin, A, Sx, Sy, Ix, Iy, rx, ry, kx, ky, reaction1, reaction2, reaction3, reaction4, reaction5, reaction6, reaction7, max_axial_stress1, max_axial_stress2, max_axial_stress3, max_axial_stress4, '
                    'max_axial_stress5, max_axial_stress6, max_axial_stress7, Cd, Ct, Cfb, Cfc, Cft, Ci, Cm, FCE, Fcstar, Fcperp_capacity, bend_capacity, shear_capacity) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    newQuery)
                self.output_db.conn1.commit()
                self.postId += 1
                post["axial_dcr"] = newQuery[12]
                postStory.append(post)
        self.PostStories.append(postStory)


class PostSyncOld:
    def __init__(self, posts, height, generalInfo, db):
        self.postOutPut = post_output(posts, height)
        print(self.postOutPut.postProperties)
        postId = 1
        for post in self.postOutPut.postProperties:
            postAnalysis = MainPost(post)
            if postAnalysis.query:
                postAnalysis.query.insert(0, postId)
                postAnalysis.query.insert(1, str(post["story"]))
                postAnalysis.query.insert(2, post["label"])
                newQuery = roundAll(postAnalysis.query)
                db.cursor1.execute(
                    'INSERT INTO POST (ID, STORY, LABEL, HEIGHT, WIDTH, SPECIES, SIZE, Pa_max, fc_psi, Cp, Pa_allow, Fc_allow, axial_dcr, axial_comb, fcperp_demand, fcperp_comb, fcperp_dcr, b, d, Fb, Ft, Fc, Fv, Fc_perp0, E, Emin, A, Sx, Sy, Ix, Iy, rx, ry, kx, ky, reaction1, reaction2, reaction3, reaction4, reaction5, reaction6, reaction7, max_axial_stress1, max_axial_stress2, max_axial_stress3, max_axial_stress4, '
                    'max_axial_stress5, max_axial_stress6, max_axial_stress7, Cd, Ct, Cfb, Cfc, Cft, Ci, Cm, FCE, Fcstar, Fcperp_capacity, bend_capacity, shear_capacity) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    newQuery)
                db.conn1.commit()
                postId += 1
                post["axial_dcr"] = newQuery[12]
