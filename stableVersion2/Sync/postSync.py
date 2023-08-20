import sys

sys.path.append(r"D:\git\Wood\UI_Wood\stableVersion2")
from UI_Wood.stableVersion2.output.post_output import post_output
from WOOD_DESIGN.mainpost import MainPost
from Report_Lab.version1.main import Main
from Report_Lab.version1.post.input import PostInput


class PostSync:
    def __init__(self, posts, height, generalInfo, db):
        self.postOutPut = post_output(posts, height)
        print(self.postOutPut.postProperties)
        postId = 1
        for post in self.postOutPut.postProperties:
            InputReport = PostInput(post, generalInfo)
            value = InputReport.input
            report = Main(value, value, value,
                          f"D:/git/Wood/UI_Wood/stableVersion1/report/Post_output_{post['label']}_ID_{str(postId)}.pdf")
            postAnalysis = MainPost(post)
            postAnalysis.query.insert(0, postId)
            postAnalysis.query.insert(1, str(post["story"]))
            postAnalysis.query.insert(2, post["label"])
            db.cursor1.execute(
                'INSERT INTO POST (ID, STORY,LABEL, SIZE, GRADE, Pa_k, fc_psi, Cp, P_allow, Fcc_psi, DCR, Load_comb, Fc_perp, Load_comb_sill, DCR_sill) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                postAnalysis.query)
            db.conn1.commit()
            postId += 1
