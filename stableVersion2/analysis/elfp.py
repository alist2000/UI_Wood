import pandas as pd


class Elfp:
    ''' This class calculates all seismic parameters and shear forces needed for shearwall design and diaphragm design'''

    def __init__(self, area, w_to_area, I, s1, ss, hn, fa, fv, tm, r, risk_ctg, story):
        self.I = I
        self.s1 = s1
        self.ss = ss
        self.hn = hn
        self.fa = fa
        self.fv = fv
        self.tm = tm
        self.r = r
        self.risk_ctg = risk_ctg
        self.ss_c = None
        self.sds = None
        self.sds_c = None
        self.sd1 = None
        self.cs = None
        self.cs_min = None
        self.cs_max = None
        self.ss_c = None
        self.sds_c = None
        self.t = None
        self.wx = []
        self.fx = []
        self.fx_to_area = []
        self.v_base = None
        self.W = None
        self.area = area
        self.w_to_area = w_to_area
        # List of stories
        self.story = story
        self.hx = []
        self.fpx = []
        self.fpx_to_area = []
        self.fpx_min = []
        self.fpx_max = []
        self.story_ratio = []
        self.Ta = None
        self.seismic_params = {}
        self.shearwall_design = pd.DataFrame()
        self.diaphragm_design = pd.DataFrame()

        self.seismic_parameters()
        self.seismic_coefficient()
        self.vertical_shear()
        self.diaphragm_shear()
        self.seismic_output()

    def seismic_parameters(self):

        ## ASCE Eq 11.4-3
        self.sds = 2 * self.fa * self.ss / 3
        ## ASCE Eq 11.4-4
        self.sd1 = 2 * self.fv * self.s1 / 3
        ## ASCE Table 12.8-2: all other structural systems
        ct = 0.02
        x = 0.75
        ## ASCE Eq 12.8-7
        self.Ta = ct * self.hn ** x
        ## ASCE Table 12.8-1 : Cu
        if self.sd1 >= 0.4:
            cu = 1.4
        elif self.sd1 >= 0.3:
            cu = 1.4
        elif self.sd1 >= 0.2:
            cu = 1.5
        elif self.sd1 >= 0.15:
            cu = 1.6
        else:
            cu = 1.7

        ## Cu.Ta
        cu_ta = cu * self.Ta
        if self.tm > 0:
            if self.tm < cu_ta:
                self.t = self.tm
            else:
                self.t = cu_ta
        else:
            self.t = self.Ta

        # ASCE 12.8.3: k
        if self.t < 0.5:
            self.k = 1
        elif self.t > 2.5:
            self.k = 2
        else:
            self.k = 1 + (self.t - 0.5) / 2

        ##  Ss for Cs: CBC 1616.10.11
        if self.hn <= 50 and self.t <= 0.5:
            self.ss_c = max(1.5, 0.8 * self.ss)
        else:
            self.ss_c = self.ss

        ##  Sds for Cs: ASCE 12.8.1.3
        self.sds_c = 2 * self.fa * self.ss_c / 3

        # Seismic design category ASCE 11.6
        if self.s1 >= 0.75:
            if self.risk_ctg == 'IV':
                design_ctg = 'F'
            else:
                design_ctg = 'E'
        else:
            design_ctg = None
        # Seismic design category of Sds: ASCE Table 11.6-1
        if design_ctg is None:
            if self.risk_ctg == 'IV':
                if self.sds < 0.167:
                    sds_ctg = 'A'
                elif self.sds < 0.33:
                    sds_ctg = 'C'
                else:
                    sds_ctg = 'D'
            else:
                if self.sds < 0.167:
                    sds_ctg = 'A'
                elif self.sds < 0.33:
                    sds_ctg = 'B'
                elif self.sds < 0.5:
                    sds_ctg = 'C'
                else:
                    sds_ctg = 'D'

        # Seismic design category of Sd1: ASCE Table 11.6-2
        if design_ctg is None:
            if self.risk_ctg == 'IV':
                if self.sd1 < 0.067:
                    sd1_ctg = 'A'
                elif self.sd1 < 0.133:
                    sd1_ctg = 'C'
                else:
                    sd1_ctg = 'D'
            else:
                if self.sd1 < 0.067:
                    sd1_ctg = 'A'
                elif self.sd1 < 0.133:
                    sd1_ctg = 'B'
                elif self.sd1 < 0.2:
                    sd1_ctg = 'C'
                else:
                    sd1_ctg = 'D'

        if design_ctg is None:
            if ord(sd1_ctg) > ord(sds_ctg):
                design_ctg = sd1_ctg
            else:
                design_ctg = sds_ctg

    def seismic_coefficient(self):
        self.cs = self.sds_c / (self.r / self.I)
        self.cs_max = self.sd1 / ((self.r / self.I) * self.t)
        if self.s1 >= 0.6:
            self.cs_min = 0.5 * self.s1 / (self.r / self.I)
        else:
            self.cs_min = max(0.044 * self.sds * self.I, 0.01)

        if self.cs < self.cs_min:
            self.cs = self.cs_min
        elif self.cs > self.cs_max:
            self.cs = self.cs_max

    def vertical_shear(self):
        self.wx = [self.area[i] * self.w_to_area[i] / 1000 for i in range(len(self.area))]
        self.W = sum(self.wx)
        self.hx = [i * 10 for i in range(1, len(self.story) + 1)]
        self.hx.reverse()
        wx_hx_k = [self.wx[i] * self.hx[i] ** self.k for i in range(len(self.area))]
        wx_hx_k_sum = sum(wx_hx_k)
        wx_hx_k_ratio = [wx_hx_k[i] / wx_hx_k_sum for i in range(len(self.area))]
        self.v_base = self.cs * self.W
        self.fx = [self.v_base * wx_hx_k_ratio[i] for i in range(len(self.area))]
        for i in range(len(self.area)):
            if self.area[i]:
                self.fx_to_area.append(1000 * self.fx[i] / self.area[i])
            else:
                self.fx_to_area.append(0)
        # self.fx_to_area=[1000*self.fx[i]/self.area[i] for i in range(len(self.area))]
        for i in range(len(self.wx)):
            if self.wx[i]:
                self.story_ratio.append(self.fx[i] / self.wx[i])
            else:
                self.story_ratio.append(0)
        # self.story_ratio = [self.fx[i] / self.wx[i] for i in range(len(self.fx))]

    def diaphragm_shear(self):
        sigma_wi = []
        num = 0
        for dp in self.wx:
            sigma_wi.append(dp + num)
            num += dp

        sigma_fi = []
        num2 = 0
        for fi in self.fx:
            sigma_fi.append(fi + num2)
            num2 += fi

        fpx0 = [self.wx[i] * sigma_fi[i] / sigma_wi[i] if sigma_wi[i] else 0 for i in range(len(self.fx))]
        self.fpx_min = [0.2 * self.sds * self.I * self.wx[i] for i in range(len(self.fx))]
        self.fpx_max = [0.4 * self.sds * self.I * self.wx[i] for i in range(len(self.fx))]
        for fp in fpx0:
            if self.fpx_min[fpx0.index(fp)] > fp:
                self.fpx.append(self.fpx_min[fpx0.index(fp)])
            elif self.fpx_max[fpx0.index(fp)] < fp:
                self.fpx.append(self.fpx_max[fpx0.index(fp)])
            else:
                self.fpx.append(fp)

        for i in range(len(self.area)):
            if self.area[i]:
                self.fpx_to_area.append(1000 * self.fpx[i] / self.area[i])
            else:
                self.fpx_to_area.append(0)
        # self.fpx_to_area = [1000 * self.fpx[i] / self.area[i] for i in range(len(self.area))]

    def seismic_output(self):
        self.seismic_params['Ss for Cs'] = self.ss_c
        self.seismic_params['Sds'] = self.sds
        self.seismic_params['Sds for Cs'] = self.sds_c
        self.seismic_params['Sd1'] = self.sd1
        self.seismic_params['Ta'] = self.Ta
        self.seismic_params['T'] = self.t
        self.seismic_params['Cs'] = self.cs
        self.seismic_params['Base shear'] = self.v_base

        self.shearwall_design['Level'] = self.story
        self.shearwall_design['Area'] = self.area
        self.shearwall_design['wx/Area'] = self.w_to_area
        self.shearwall_design['Wx'] = self.wx
        self.shearwall_design['k'] = [self.k] * len(self.story)
        self.shearwall_design['Baes shear'] = [self.v_base] * len(self.story)
        self.shearwall_design['Story Force Fx'] = self.fx
        self.shearwall_design['Fx/Area'] = self.fx_to_area
        self.shearwall_design['Story proportopn'] = self.story_ratio

        self.diaphragm_design['level'] = self.story
        self.diaphragm_design['Area'] = self.area
        self.diaphragm_design['wx/Arae'] = self.w_to_area
        self.diaphragm_design['wpx'] = self.wx
        self.diaphragm_design['Fpx min'] = self.fpx_min
        self.diaphragm_design['Fpx max'] = self.fpx_max
        self.diaphragm_design['Fpx'] = self.fpx
        self.diaphragm_design['Fpx/Area'] = self.fpx_to_area
