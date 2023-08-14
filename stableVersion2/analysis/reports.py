
import sqlite3

class Sqlreports:
    def __init__(self):
        self.conn1 = sqlite3.connect('../../Output/beam_report.db')
        self.cursor1 = self.conn1.cursor()


    def parent_table(self):
        self.cursor1.execute("DROP TABLE IF EXISTS PARENT")
        table0=''' CREATE TABLE PARENT(
        ID INT,
        STORY text,
        );'''
        self.cursor1.execute(table0)
        self.conn1.commit()
    


    def beam_table(self):
        self.cursor1.execute("DROP TABLE IF EXISTS BEAM")
        table1=''' CREATE TABLE BEAM(
                ID INT,
                STORY text,
                LABEL text,
                LENGTH INT,
                SIZE text,
                Vmax float,
                Mmax float,
                Fb_actual float,
                Fb_allow float,
                Fv_actual float,
                Fv_allow float,
                Deflection_actual float,
                Deflection_allow float,
                Bending_dcr float,
                Shear_dcr float,
                DIST_D text,
                DIST_D_range text,
                DIST_L text,
                DIST_L_range text,
                DIST_LR text,
                DIST_LR_range text,
                DIST_E text,
                DIST_E_range text,
                P_D text,
                P_D_range text,
                P_L text,
                P_L_range text,
                P_LR text,
                P_LR_range text,
                P_E text,
                P_E_range text,
                RD text,
                RL text,
                RLr text,
                RE text

        );'''
        self.cursor1.execute(table1)
        self.conn1.commit()

    def post_table(self):

        self.cursor1.execute("DROP TABLE IF EXISTS POST")
        table2=''' CREATE TABLE POST(
                ID INT,
                STORY text,
                LABEL text,
                SIZE text,
                GRADE text,
                Pa_k float,
                fc_psi float,
                Cp float,
                P_allow float,
                Fcc_psi float,
                DCR float,
                Load_comb text,
                Fc_perp float,
                Load_comb_sill text,
                DCR_sill float

        );'''

        self.cursor1.execute(table2)
        self.conn1.commit()



# f.cursor1.execute("INSERT INTO POST (ID, STORY,SIZE, GRADE, Pa_k, fc_psi, Cp, P_allow, Fcc_psi, DCR, Load_comb, Fc_perp, Load_comb_sill, DCR_sill) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",z.query)
# f.conn1.commit()

          
