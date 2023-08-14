import sys

sys.path.append(r"D:\git\Wood")

from WOOD_DESIGN.beamlink1 import Link1
from WOOD_DESIGN.beamlink0 import Link0
from WOOD_DESIGN.beamlink2 import ConvertBeamData
import sqlite3
from WOOD_DESIGN.Beamanalysis import BeamDesign
import pandas as pd
from WOOD_DESIGN.reports import Sqlreports


class MainBeam:
    def __init__(self, beam_new):
        self.beam_new = beam_new
        self.query = None

        a = Link0(beam_new)
        b = Link1(a.beam_)
        c = ConvertBeamData(b.dict_dist, b.dict_point)

        conn = sqlite3.connect('..\..\WOOD_DESIGN\section.db')
        sq = conn.cursor()
        sq.execute(" SELECT * FROM section")
        row = sq.fetchall()

        delimiter = " , "

        for r in row:
            q = BeamDesign(length=b.length, supports=b.supports, p_loads=c.p_loads, dist_loads=c.dist_loads,
                           beam_size=r)
            q.beam_properties()
            q.beam_support()
            q.beam_loads()
            q.beam_analysis((r[2] - .15) / 12)
            q.beam_reaction(b.dict_point, b.dict_dist)
            q.beam_design()

            if q.beam_sec != None:

                ## LOAD OUTPUT
                distd_ = delimiter.join(str(elem) for elem in q.distd_sql)
                distdrange_ = delimiter.join(str(elem) for elem in q.distd_range_sql)
                distl_ = delimiter.join(str(elem) for elem in q.distl_sql)
                distlrange_ = delimiter.join(str(elem) for elem in q.distl_range_sql)
                distlr_ = delimiter.join(str(elem) for elem in q.distlr_sql)
                distlrrange_ = delimiter.join(str(elem) for elem in q.distlr_range_sql)
                diste_ = delimiter.join(str(elem) for elem in q.diste_sql)
                disterange_ = delimiter.join(str(elem) for elem in q.diste_range_sql)

                pd_ = delimiter.join(str(elem) for elem in q.pd_sql)
                pdrange_ = delimiter.join(str(elem) for elem in q.pd_range_sql)
                pl_ = delimiter.join(str(elem) for elem in q.pl_sql)
                plrange_ = delimiter.join(str(elem) for elem in q.pl_range_sql)
                plr_ = delimiter.join(str(elem) for elem in q.plr_sql)
                plrrange_ = delimiter.join(str(elem) for elem in q.plr_range_sql)
                pe_ = delimiter.join(str(elem) for elem in q.pe_sql)
                perange_ = delimiter.join(str(elem) for elem in q.pe_range_sql)

                ## REACTION OUTPUT
                rd_sql0 = [sum(q.RD[sq1]) for sq1 in q.RD.keys()]
                rd_sql = delimiter.join(str(elem) for elem in rd_sql0)
                rl_sql0 = [sum(q.RL[sq1]) for sq1 in q.RL.keys()]
                rl_sql = delimiter.join(str(elem) for elem in rl_sql0)
                rlr_sql0 = [sum(q.RLr[sq1]) for sq1 in q.RLr.keys()]
                rlr_sql = delimiter.join(str(elem) for elem in rlr_sql0)
                re_sql0 = [sum(q.E[sq1]) for sq1 in q.E.keys()]
                re_sql = delimiter.join(str(elem) for elem in re_sql0)

                self.query = [q.length, q.beam_sec, q.vsmax, q.mmax, q.fb_actual, q.fb_allow, q.fv_actual,
                              q.fv_allow, q.defmax, q.defl_allow, q.bending_dcr, q.shear_dcr,
                              distd_, distdrange_, distl_, distlrange_, distlr_, distlrrange_, diste_, disterange_, pd_,
                              pdrange_, pl_, plrange_, plr_, plrrange_, pe_, perange_,
                              rd_sql, rl_sql, rlr_sql, re_sql]
                self.output = q

                break
            elif q.beam_sec == None and r != row[-1]:
                continue
            else:
                self.query = ['No Section Was Adequate'] + ['None'] * 31

# f=Sqlreports
# f.beam_table()
# f.cursor1.execute('INSERT INTO BEAM (ID, STORY, LENGTH, SIZE,Vmax, Mmax, Fb_actual, Fb_allow, Fv_actual, Fv_allow, Deflection_actual, Deflection_allow, Bending_dcr, Shear_dcr,
# DIST_D, DIST_D_range, DIST_L, DIST_L_range, DIST_LR, DIST_LR_range, DIST_E, DIST_E_range, P_D, P_D_range, P_L, P_L_range, P_LR, P_LR_range, P_E, P_E_range,
# RD, RL, RLr, RE) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', q.query)
# f.conn1.commit()