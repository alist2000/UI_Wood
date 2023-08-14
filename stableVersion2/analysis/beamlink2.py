from sympy import *
import numpy as np


class ConvertBeamData:

    def __init__(self, dict_dist, dict_point):
        self.dict_dist = dict_dist
        self.dict_point = dict_point
        self.dist_loads = {}
        self.p_loads = {}

        self.params = None
        self.expr1 = None;
        self.expr2 = None;
        self.expr3 = None
        self.expr4 = None;
        self.expr5 = None;
        self.expr6 = None
        self.expr7 = None;
        self.expr8 = None;
        self.expr9 = None
        self.eqs = None

        self.symbols()
        self.dist_convert()
        self.point_convert()

    def symbols(self):
        D, L, Lr, E0, S0 = symbols('D L Lr E0 S0')
        self.expr1 = D
        self.expr2 = D + L
        self.expr3 = D + Lr
        self.expr4 = D + 0.7 * E0
        self.expr5 = D + S0
        self.expr6 = D + 0.75 * L + 0.75 * Lr
        self.expr7 = D + 0.75 * L + 0.75 * S0
        self.expr8 = D + 0.75 * L + 0.525 * E0
        self.expr9 = D + 0.75 * L + 0.75 * S0 + 0.525 * E0

        self.params = [D, L, Lr, E0, S0]
        self.eqs = [self.expr1, self.expr2, self.expr3, self.expr4, self.expr5, self.expr6, self.expr7, self.expr8,
                    self.expr9]
        for ex in self.eqs:
            self.p_loads[ex] = []
            self.dist_loads[ex] = []

    def dist_convert(self):
        ## Distributed loads
        unique_ranges = []
        for it in list(self.dict_dist.values()):
            for it2 in it:
                if it2[1] not in unique_ranges:
                    unique_ranges.append(it2[1])

        load_sets = [[] for i in range(len(unique_ranges))]
        load_set_vals = [[] for i in range(len(unique_ranges))]

        for ii in unique_ranges:
            for jj in self.dict_dist.values():
                for jj2 in jj:
                    if jj2[1] == ii:
                        load_sets[unique_ranges.index(ii)].append(
                            list(self.dict_dist.keys())[list(self.dict_dist.values()).index(jj)])
                        load_set_vals[unique_ranges.index(ii)].append(jj2[0])

        for index0, load in enumerate(load_sets):
            symbs = [sympify(i, evaluate=True) for i in load]
            vals = load_set_vals[index0]
            params_vals = [0] * 5

            for index1, sy in enumerate(symbs):
                for index2, item in enumerate(self.params):
                    if sy == item:
                        params_vals[index2] = vals[index1]

            f = lambdify([*self.params],
                         [self.expr1, self.expr2, self.expr3, self.expr4, self.expr5, self.expr6, self.expr7,
                          self.expr8, self.expr9])
            f_result = f(*params_vals)

            f_resultplus = [-i for i in f_result]
            idx3 = f_resultplus.index(max(f_resultplus))
            critical_load = self.eqs[idx3]

            self.dist_loads[critical_load].append((f_result[idx3], unique_ranges[index0]))

        for cont in list(self.dist_loads.keys()):
            self.dist_loads[str(cont)] = self.dist_loads.pop(cont)

    def point_convert(self):
        ## Distributed loads
        unique_locs = []
        for it in list(self.dict_point.values()):
            for it2 in it:
                if it2[1] not in unique_locs:
                    unique_locs.append(it2[1])

        load_sets = [[] for i in range(len(unique_locs))]
        load_set_vals = [[] for i in range(len(unique_locs))]

        for ii in unique_locs:
            for jj in self.dict_point.values():
                for jj2 in jj:
                    if jj2[1] == ii:
                        load_sets[unique_locs.index(ii)].append(
                            list(self.dict_point.keys())[list(self.dict_point.values()).index(jj)])
                        load_set_vals[unique_locs.index(ii)].append(jj2[0])

        for index0, load in enumerate(load_sets):
            symbs = [sympify(i, evaluate=True) for i in load]
            vals = load_set_vals[index0]
            params_vals = [0] * 5

            for index1, sy in enumerate(symbs):
                for index2, item in enumerate(self.params):
                    if sy == item:
                        params_vals[index2] = vals[index1]

            f = lambdify([*self.params],
                         [self.expr1, self.expr2, self.expr3, self.expr4, self.expr5, self.expr6, self.expr7,
                          self.expr8, self.expr9])
            f_result = f(*params_vals)

            f_resultplus = [-i for i in f_result]
            idx3 = f_resultplus.index(max(f_resultplus))
            critical_load = self.eqs[idx3]

            self.p_loads[critical_load].append((f_result[idx3], unique_locs[index0]))

        for cont in list(self.p_loads.keys()):
            self.p_loads[str(cont)] = self.p_loads.pop(cont)
