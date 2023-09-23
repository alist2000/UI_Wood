import sys

from Report_Lab.version1.main import Main
from UI_Wood.stableVersion2.output.joist_output import Joist_output
from WOOD_DESIGN.mainbeamnewupdated import MainBeam
from UI_Wood.stableVersion2.Sync.beamSync import roundAll


class joistAnalysisSync:
    def __init__(self, joist, db):
        self.joist = joist
        joistId = 1
        joistOutput = Joist_output(joist)

        for i, joistTab in enumerate(joistOutput.Joists):

            tabNumber = i

            for joistNum, joist_ in enumerate(joistTab):
                if joist_:
                    joistItems = joist_["joist_item"]
                    joistDesigned = []
                    joistIDList = []
                    joistBendDCR = []
                    joistShearDCR = []
                    for joistItem in joistItems:
                        joist_analysis = MainBeam(joistItem, "joist")
                        if joist_analysis.query[0] != "No Section Was Adequate":
                            joist_analysis.query.insert(0, str(joistId))
                            joist_analysis.query.insert(1, str(tabNumber + 1))
                            joist_analysis.query.insert(2, joist_["label"])
                            joistDesigned.append(joist_analysis)
                            joistIDList.append(joist_analysis.query[-1])
                            joistBendDCR.append(joist_analysis.query[16])
                            joistShearDCR.append(joist_analysis.query[17])

                    if joistDesigned:
                        checkJoist = ChooseJoist(joistDesigned, joistIDList, joistBendDCR, joistShearDCR)
                        joist_analysis_selected = checkJoist.checkAll()
                        figs = joist_analysis_selected.plots
                        figs[0].write_image(
                            f"images/joist/Joist_external_story{tabNumber + 1}_label_{joist_analysis_selected.query[2]}.png")
                        figs[1].write_image(
                            f"images/joist/Joist_internal_story{tabNumber + 1}_label_{joist_['label']}.png")
                        newQuery = roundAll(joist_analysis_selected.query)
                        db.cursor1.execute(
                            'INSERT INTO JOIST (ID, STORY, LABEL, SPECIES, SPANS, LENGTH, LOAD_COMB, SIZE, Vmax, Mmax, Fb_actual, Fb_allow, Fv_actual, Fv_allow, Deflection_actual, Deflection_allow, Bending_dcr, Shear_dcr, defl_dcr, DIST_D, DIST_D_range, DIST_L, DIST_L_range, DIST_LR, DIST_LR_range, DIST_E, DIST_E_range, DIST_S, DIST_S_range, P_D, P_D_range, P_L, P_L_range, P_LR, P_LR_range, P_E, P_E_range, P_S, P_S_range, RD, RL, RLr, RE, RS, Mmax_loc, Vmax_loc, d, b, Fb, Ft, Fc, Fv, Fcperp, E, Emin, A, Sx, Sy, Ix, Iy, Cd, Ct, Cfb, Cfc, Cft, Cfu, Ci, Ciperp, Cr, Cb, Cl, Fcperp_cap, Fcperp_dem) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                            newQuery[:-1])
                        db.conn1.commit()
                        joistId += 1


class ChooseJoist:
    def __init__(self, joists, Id, bending_dcr, shear_dcr):
        maxId = max(Id)
        self.joists = joists
        self.indexes_section = self.find_indices(Id, maxId)
        self.bending_dcr = self.find_index_base(bending_dcr)
        self.shear_dcr = self.find_index_base(shear_dcr)

    @staticmethod
    def find_indices(input_list, search_item):
        return [index for index, item in enumerate(input_list) if item == search_item]

    def find_index_base(self, input_list):
        return [item for index, item in enumerate(input_list) if (index in self.indexes_section)]

    def find_section_based(self, indexes):
        if len(indexes) == 1:
            return self.joists[indexes[0]]
        return None

    def checkAll(self):
        item = self.find_section_based(self.indexes_section)
        if item:
            return item
        maxBend = max(self.bending_dcr)
        indexes = self.find_indices(self.bending_dcr, maxBend)
        item = self.find_section_based(indexes)
        if item:
            return item
        maxShear = max(self.shear_dcr)
        indexes = self.find_indices(self.shear_dcr, maxShear)
        item = self.find_section_based(indexes)
        if item:
            return item
        else:
            return self.joists[indexes[0]]
