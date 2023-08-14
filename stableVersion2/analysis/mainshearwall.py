import sys

sys.path.append(r"D:\git\Wood")

from WOOD_DESIGN.diaphragms import Diaphragms
from WOOD_DESIGN.wallprop import WallProp
import pandas as pd
from WOOD_DESIGN.elfp import Elfp
from WOOD_DESIGN.master import MasterShearWall
from functools import reduce
import sqlite3
import numpy as np


class MainShearwall:
    def __init__(self, input0, midline):
        self.input0 = input0
        self.midline = midline
        self.w_to_area = []
        for idx, load in enumerate(self.input0['load_area']):
            if not load:
                self.w_to_area.append(0)
            else:
                num = 0
                for idx2, load2 in enumerate(load):
                    c = self.input0['load_area'][idx][idx2] * self.input0['load_magnitude'][idx][idx2]
                    num += c
                self.w_to_area.append(num / self.input0['joist_area'][idx])

        self.elfp_object = None
        self.diaph_object = None
        self.mastersw_object = None

        all_ew = []
        all_ns = []
        ns_line = []
        ew_line = []
        for story in self.midline:  # each story
            ew_mag = [[]]
            ew_area = [[]]
            ns_mag = [[]]
            ns_area = [[]]
            nlines = []
            elines = []
            for dict in self.midline[story]:
                for line in dict:
                    if line.isdigit():
                        nlines.append(line)
                        ns_i_area = []
                        ns_i_mag = []
                        for val in dict[line]:
                            ns_i_area.append(val['area'])
                            ns_i_mag.append(val['magnitude'])
                        ns_mag[0].append(ns_i_mag)
                        ns_area[0].append(ns_i_area)
                    else:
                        elines.append(line)
                        ew_i_area = []
                        ew_i_mag = []
                        for val in dict[line]:
                            ew_i_area.append(val['area'])
                            ew_i_mag.append(val['magnitude'])
                        ew_mag[0].append(ew_i_mag)
                        ew_area[0].append(ew_i_area)

            ns_i = [[nlines], ns_mag, ns_area]
            ew_i = [[elines], ew_mag, ew_area]
            all_ns.append(ns_i)
            all_ew.append(ew_i)
            ns_line.append(nlines)
            ew_line.append(elines)

        self.orients = [all_ew, all_ns]
        self.stories = input0['story_name']
        self.weight_line_ew = []
        self.weight_line_ns = []
        self.lines_ew = [[] for i in self.stories]
        self.lines_ns = [[] for i in self.stories]

        self.to_elfp()
        self.to_diaphragms()
        self.to_master_shearwall()

    def to_elfp(self):
        #      [area, w_to_area, I, s1, ss, hn, fa, fv, tm, r, risk_ctg, story]
        self.elfp_object = Elfp(self.input0['joist_area'], self.w_to_area, self.input0['I'], self.input0['S1'],
                                self.input0['Ss'], 10 * len(self.input0['story_name']), self.input0['Fa'],
                                self.input0['Fv'], self.input0['T model'], self.input0['R Factor'],
                                self.input0['Risk Category'], self.input0['story_name'])

    def to_diaphragms(self):

        '''Here, we need to get weight_line_ew, weight_line_ns, lines_flat_ew and lines_flat_ns for all stories.'''

        ratio = self.elfp_object.story_ratio
        wing = 1
        lines_ew0 = []
        lines_ns0 = []

        for id, item in enumerate(self.orients):
            for idd, st in enumerate(item):
                self.diaph_object = Diaphragms(wing, st[0], st[1], st[2], self.stories[idd], ratio[idd])
                if id == 0:
                    self.weight_line_ew.append(self.diaph_object.weight_line)
                    lines_ew0.append(self.diaph_object.lines_flat)
                elif id == 1:
                    self.weight_line_ns.append(self.diaph_object.weight_line)
                    lines_ns0.append(self.diaph_object.lines_flat)

    def to_master_shearwall(self):
        cnx = sqlite3.connect('D:/git/Wood/Output/ShearWall_Input.db')
        df_ = pd.read_sql_query("SELECT * FROM WallTable", cnx)

        ## lines_ew and lines_ns inputs for wallprop class. Each containing lines for different stories.

        for ix, each in enumerate(df_['Line'].values.tolist()):
            str = df_['Story'].values.tolist()[ix]
            flag = True
            try:
                int(each)
            except ValueError:
                flag = False

            if flag:
                if each not in self.lines_ns[self.stories.index(str)]:
                    self.lines_ns[self.stories.index(str)].append(each)
            else:
                if each not in self.lines_ew[self.stories.index(str)]:
                    self.lines_ew[self.stories.index(str)].append(each)

        unique_id = []
        ln = df_['Line'].values.tolist()
        lb = df_['Wall_Label'].values.tolist()
        for x, ids0 in enumerate(ln):
            ids = ids0 + '-' + lb[x]
            if ids not in unique_id:
                unique_id.append(ids)

        merged_walls = []
        sheathing_ = []
        re_ft_ = []
        portion_force_ = []
        re_open_ = []
        re_hb_ = []
        f_x_ = []
        vabv_ = []
        vdsg_ = []
        typewall_ = []
        allowshear_ = []
        dcrs_ = []

        for numer in unique_id:
            label_i = numer.split('-')[1]
            line_i = numer.split('-')[0]

            self.mastersw_object = MasterShearWall(line_i, label_i, self.stories, df_, 1, self.weight_line_ew,
                                                   self.weight_line_ns, self.lines_ew, self.lines_ns)
            self.mastersw_object.total_line_len()
            self.mastersw_object.total_line_force()
            self.mastersw_object.wall_force()
            self.mastersw_object.shear_wall_design()
            sheathing_.append(self.mastersw_object.sheathing)
            re_ft_.append(self.mastersw_object.re_ft)
            portion_force_.append(self.mastersw_object.portion_force)
            re_open_.append(self.mastersw_object.re_open)
            re_hb_.append(self.mastersw_object.re_hb)
            f_x_.append(self.mastersw_object.f_x)
            vabv_.append(self.mastersw_object.vabv)
            vdsg_.append(self.mastersw_object.vdsg)
            typewall_.append(self.mastersw_object.typewall)
            allowshear_.append(self.mastersw_object.allowshear)
            dcrs_.append(self.mastersw_object.dcrs)
            merged_walls.append(self.mastersw_object.wall)

        master_walls = pd.concat(merged_walls, ignore_index=True)
        master_walls['Sheathing type'] = [item for sublist in sheathing_ for item in sublist]
        master_walls['Reduction FT'] = [item for sublist in re_ft_ for item in sublist]
        master_walls['Portion of Line Forct to Wall'] = [item for sublist in portion_force_ for item in sublist]
        master_walls['Reduction Opening'] = [item for sublist in re_open_ for item in sublist]
        master_walls['Reduction h/b'] = [item for sublist in re_hb_ for item in sublist]
        master_walls['Fx'] = [item for sublist in f_x_ for item in sublist]
        master_walls['Vabv'] = [item for sublist in vabv_ for item in sublist]
        master_walls['Vdesign'] = [item for sublist in vdsg_ for item in sublist]
        master_walls['Shearwall Type'] = [item for sublist in typewall_ for item in sublist]
        master_walls['Allowable shear'] = [item for sublist in allowshear_ for item in sublist]
        master_walls['Shear DCR'] = [item for sublist in dcrs_ for item in sublist]

        dff = master_walls
        # dff.to_excel('types.xlsx')
