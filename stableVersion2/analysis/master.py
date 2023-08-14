import sys

sys.path.append(r"D:\git\Wood")


import math
import numpy as np
from WOOD_DESIGN.wallprop import WallProp
import pandas as pd


class MasterShearWall(WallProp):
    ''' design shear walls, wall to wall'''

    def __init__(self, line, label, story, wallproperties, wall_method, weight_line_ew, weight_line_ns, lines_ew,
                 lines_ns):
        self.wallproperties = wallproperties
        self.story = story
        self.line = line
        self.label = label
        self.wall = None  # data of specified wall (line and label)
        self.sheathing_type = None
        self.portion_line_force = None
        self.reduction_ft = None
        self.reduction_open = None
        self.reduction_hb = None
        self.wall_fx = []
        self.indexes = []
        self.v_abv = []
        self.v_design = []
        self.rho = 1
        self.cd = 4
        self.delta_a = 0.02
        self.unit_shear = []
        self.shear_allowable = []
        self.shearwall_type = []
        self.line_and_label = []

        self.sheathing = None
        self.re_ft = None
        self.portion_force = None
        self.re_open = None
        self.re_hb = None
        self.f_x = None
        self.vabv = None
        self.vdsg = None
        self.typewall = None
        self.allowshear = None
        self.dcrs = None

        WallProp.__init__(self, story, wallproperties, wall_method, weight_line_ew, weight_line_ns, lines_ew, lines_ns)

    def shear_wall_design(self):

        # Selected wall dataframe
        wall0 = self.wallproperties[
            (self.wallproperties['Line'] == self.line) & (self.wallproperties['Wall_Label'] == self.label)]
        self.wall = wall0.drop(
            ['Opening_Width', 'start', 'end', 'Rd', 'Rl', 'Rlr', 'Rs', 'Left_Bottom_End', 'Right_Top_End', 'Po_Left',
             'Pl_Left',
             'Pe_Left', 'Po_Right', 'Pl_Right', 'Pe_Right'], axis=1)

        self.line_and_label.append((self.line, self.label))

        ## Wall indexes in wallproperties
        idx = \
        list(np.where((self.wallproperties['Line'] == self.line) & (self.wallproperties['Wall_Label'] == self.label)))[
            0]
        self.indexes = idx.tolist()

        ## Sheathing type & Reduction factor for fire treated walls
        if self.wall['Int_Ext'][self.indexes[0]] == 'E':
            self.sheathing_type = 'Plywood'
            self.reduction_ft = 0.84
        else:
            self.sheathing_type = 'OSB'
            self.reduction_ft = 1
        self.sheathing = [self.sheathing_type] * len(self.indexes)
        self.re_ft = [self.reduction_ft] * len(self.indexes)
        # self.wall['Sheathing type']=[self.sheathing_type]*len(self.indexes)
        # self.wall['Reduction FT']=[self.reduction_ft]*len(self.indexes)

        # Portion of line force to wall
        self.portion_line_force = self.wall['Wall_Length'][self.indexes[0]] / self.wall['Line_Total_Length'][
            self.indexes[0]]
        self.portion_force = [self.portion_line_force] * len(self.indexes)
        # self.wall['Portion of Line Forct to Wall']=[self.portion_line_force]*len(self.indexes)

        ## Reduction factor for opening in walls
        # self.wallproperties['Opening_Width']=self.wallproperties['Opening_Width'].replace(np.nan,0)                
        self.reduction_open = (self.wallproperties['Wall_Length'][self.indexes[0]] - int(
            self.wallproperties['Opening_Width'][self.indexes[0]])) / self.wallproperties['Wall_Length'][
                                  self.indexes[0]]
        self.re_open = [self.reduction_open] * len(self.indexes)
        # self.wall['Reduction Opening']=[self.reduction_open]*len(self.indexes)        

        ## Reduction factor for h/b
        # self.reduction_hb=min(1, 1.25-0.125*(self.wall.iloc[0,5]-1)/self.wall.iloc[0,4])
        self.reduction_hb = min(1, 1.25 - 0.125 * (self.wall['Story_Height'][self.indexes[0]] - 1) /
                                self.wall['Wall_Length'][self.indexes[0]])

        self.re_hb = [self.reduction_hb] * len(self.indexes)
        # self.wall['Reduction h/b']=[self.reduction_hb]*len(self.indexes)

        ## Fx (kips)
        self.wall_fx = [self.wallproperties['Wall_Force'][i] for i in self.indexes]
        self.f_x = self.wall_fx
        # self.wall['Fx']=self.wall_fx

        ## V_above (kips)

        self.v_abv = [sum(self.wall_fx[0:i + 1]) for i in range(len(self.wall_fx) - 1)]
        self.v_abv.insert(0, 0)
        self.vabv = self.v_abv
        # self.wall['Vabv']=self.v_abv

        ## V_design (kips)
        self.v_design = [self.wall_fx[i] + self.v_abv[i] for i in range(len(self.wall_fx))]
        self.vdsg = self.v_design
        # self.wall['Vdesign']=self.v_design

        ## ASD unit shear (plf)
        length = [self.wall['Wall_Length'][i] for i in self.indexes]
        self.unit_shear = [0.7 * self.v_design[i] * 1000 * self.rho / length[i] for i in range(len(self.v_design))]

        ## Shearwall type
        factors = self.reduction_ft * self.reduction_open * self.reduction_hb
        shear_demand = [self.unit_shear[i] / factors for i in range(len(self.unit_shear))]
        print(shear_demand)
        for tp in shear_demand:
            if tp <= 510:
                sw_type = 3
                capacity = 510  ## plf
            elif tp <= 665:
                sw_type = 4
                capacity = 665
            elif tp <= 870:
                sw_type = 5
                capacity = 870
            elif tp <= 1330:
                sw_type = 6
                capacity = 1330
            elif tp <= 1740:
                sw_type = 7
                capacity = 1740
            else:
                sw_type = 'NG'
                capacity = 1740

            self.shearwall_type.append(sw_type)
            self.shear_allowable.append(capacity * factors)
        self.typewall = self.shearwall_type
        # self.wall['Shearwall Type']=self.shearwall_type

        ## Allowable shear
        self.allowshear = self.shear_allowable
        # self.wall['Allowable shear']=self.shear_allowable

        ## Shear DCR
        self.shear_DCR = [self.unit_shear[i] / self.shear_allowable[i] for i in range(len(self.unit_shear))]
        self.dcrs = self.shear_DCR
        # self.wall['Shear DCR']=self.shear_DCR
