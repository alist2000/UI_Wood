from indeterminatebeam import Beam, Support, PointLoadV, PointTorque, UDLV, DistributedLoadV


class BeamDesign:
    ''' A class to design beams'''

    def __init__(self, length, supports, beam_size, p_loads=None, dist_loads=None):
        '''
        parameters: length, Trib, Point Loads, Dist Loads, support conditions.
        '''
        self.length = length
        self.p_loads = p_loads
        self.dist_loads = dist_loads
        self.supports = supports
        self.beam_size = beam_size
        self.load_dict = {}
        self.beam_section = []
        self.load0 = [];
        self.load1 = [];
        self.load2 = [];
        self.load3 = [];
        self.load4 = [];
        self.load5 = [];
        self.fig_1 = None
        self.fig_2 = None
        self.reaction = []
        self.reaction_coord = []
        self.post_output = {}
        self.reactions = []
        self.reaction_keys = []
        self.vs_cd = []
        self.vsmax = None
        self.vact_max = None
        self.mmax = None
        self.defmax = None
        self.defl_allow = None
        self.fb_actual = None
        self.fv_actual = None
        self.fb_allow = None
        self.fv_allow = None
        self.bending_dcr = None
        self.shear_dcr = None
        self.defl_dcr = None
        self.beam = None
        self.beam_sec = None
        self.RD = {}
        self.RL = {}
        self.RLr = {}
        self.E = {}
        self.cd = None
        self.vs_act = None
        self.points = {}
        self.distributed = {}
        self.all_loads = None

        self.distd_sql = [];
        self.pd_sql = []
        self.distd_range_sql = [];
        self.pd_range_sql = []
        self.distl_sql = [];
        self.pl_sql = []
        self.distl_range_sql = [];
        self.pl_range_sql = []
        self.distlr_sql = [];
        self.plr_sql = []
        self.distlr_range_sql = [];
        self.plr_range_sql = []
        self.diste_sql = [];
        self.pe_sql = []
        self.diste_range_sql = [];
        self.pe_range_sql = []

    def beam_properties(self):
        '''
        Pass beam information, set units.
        '''
        # Initialize a Beam object with length, E and I as defined
        self.beam = Beam(self.length, E=self.beam_size[4], I=self.beam_size[5])
        # Set the units to (kip,in,ft)
        self.beam.update_units(key='length', unit='ft')
        self.beam.update_units('force', 'kip')
        self.beam.update_units('distributed', 'kip/ft')
        self.beam.update_units('moment', 'kip.ft')
        self.beam.update_units('E', 'kip/in2')
        self.beam.update_units('I', 'in4')
        self.beam.update_units('deflection', 'in')

    def beam_support(self):
        '''
        Define supports
        '''
        supports_active = []
        for sup in self.supports:
            supports_active.append(Support(sup[0], sup[1]))
        ## Assign the support objects to a beam object created earlier
        self.beam.add_supports(*supports_active)

    def beam_loads(self):
        '''
        Define loads

        p_loads is the dictinary containing point loads in different load combinations.
        dist_load is the dictinary containing distributed loads in different load combinations.
        The load combinations include: [D, D+L, D+Lr, D+0.75L+0.75Lr, D+0.7E, D+0.75L+0.525E]
        Each load case is apploied to the beam through PointLoadV & DistributedLoadV functions.
        The outputs are stored in a dictionary named 'load_dict'.
        '''

        if self.p_loads is None:
            self.points['D'] = PointLoadV(0, (0))
        else:
            for pk, pv in self.p_loads.items():
                self.points[pk] = []
                for p in pv:
                    self.points[pk].append(PointLoadV(p[0], (p[1])))

        if self.dist_loads is None:
            self.distributed['D'] = DistributedLoadV(0, (0, self.length))
        else:
            for dk, dv in self.dist_loads.items():
                self.distributed[dk] = []
                for d in dv:
                    self.distributed[dk].append(DistributedLoadV(d[0], d[1]))

    def beam_analysis(self, depth):
        '''
        Apply the loads to the beam object. Analyze the beam. Get maximum shear, bending and deflection. Get reactions.

        vs: is a list containing maximum shear forces in different load combinations.
        vs_act: is a list containing actual shear forces that means shear forces at d from support.
        mb: is a list containing maximum bending moments in different load combinations.
        dfl: is a list containing maximum deflections in different load combinations.
        reactions: is a list containing the support reactions of the beam under different load cases (load combinations)
        reaction: is a list containing the support reactions of the beam UNDER MAXIMUM LOAD CASE (load combination).
        RD: is the list of dead reaction loads of all supports
        RL: is the list of live reaction loads of all supports
        RLr: is the list of roof live reaction loads of all supports
        RE: is the list of seismic reaction loads of all supports
        '''

        self.vs_act = []
        self.all_loads = []
        all_combs = []

        for ky, vl in self.points.items():
            for vl0 in vl:
                all_combs.append(ky)

        for kyy, vll in self.distributed.items():
            for vll0 in vll:
                all_combs.append(kyy)

        for cod1 in self.points.values():
            for cod2 in cod1:
                self.all_loads.append(cod2)

        for cod3 in self.distributed.values():
            for cod4 in cod3:
                self.all_loads.append(cod4)

        ## Find cd factor from dominated load combo
        for each in self.all_loads:
            self.beam.add_loads(each)
            self.beam.analyse()
            self.vs_cd.append(self.beam.get_shear_force(return_absmax=True))
            self.beam.remove_loads(each, remove_all=True)

        index_for_cd = self.vs_cd.index(max(self.vs_cd))
        print(index_for_cd)
        print(len(all_combs))
        print(len(self.all_loads))

        comb_for_cd = all_combs[index_for_cd]
        if comb_for_cd == 'D':
            self.cd = 0.9
        elif comb_for_cd == 'D + L':
            self.cd = 1
        elif comb_for_cd == 'D + Lr' or comb_for_cd == 'D + 0.75*L + 0.75*Lr':
            self.cd = 1.25
        elif comb_for_cd == 'D + S' or comb_for_cd == 'D + 0.75*L + 0.75*S':
            self.cd = 1.15
        else:
            self.cd = 1.6

        ## Find maximum deflection, shear and moment for design
        self.beam.add_loads(*self.all_loads)
        self.beam.analyse()
        self.vsmax = self.beam.get_shear_force(return_absmax=True)
        self.mmax = self.beam.get_bending_moment(return_absmax=True)
        self.defmax = self.beam.get_deflection(return_absmax=True)
        self.fig_1 = self.beam.plot_beam_external()
        self.fig_2 = self.beam.plot_beam_internal()

        ## Find shear at d from column
        for j in self.supports:
            # is v_act ok??
            self.vs_act.append(self.beam.get_shear_force(j[0] + depth))
        self.vact_max = max(self.vs_act)

    def beam_reaction(self, dict_point, dict_dist):

        self.reaction_coord = [j[0] for j in self.supports]
        for j0 in self.supports:
            self.RD[str(j0[0])] = []
            self.RL[str(j0[0])] = []
            self.RLr[str(j0[0])] = []
            self.E[str(j0[0])] = []

        self.beam.remove_loads(*self.all_loads, remove_all=True)
        for key, i in dict_point.items():
            for j in i:
                self.beam.add_loads(PointLoadV(j[0], j[1]))
                self.beam.analyse()
                if key == 'D':
                    self.pd_sql.append(j[0])
                    self.pd_range_sql.append(j[1])
                    for j1 in self.reaction_coord:
                        self.RD[str(j1)].append(self.beam.get_reaction(j1, direction='y'))
                elif key == 'L':
                    self.pl_sql.append(j[0])
                    self.pl_range_sql.append(j[1])
                    for j1 in self.reaction_coord:
                        self.RL[str(j1)].append(self.beam.get_reaction(j1, direction='y'))
                elif key == 'Lr':
                    self.plr_sql.append(j[0])
                    self.plr_range_sql.append(j[1])
                    for j1 in self.reaction_coord:
                        self.RLr[str(j1)].append(self.beam.get_reaction(j1, direction='y'))
                elif key == 'E':
                    self.pe_sql.append(j[0])
                    self.pe_range_sql.append(j[1])
                    for j1 in self.reaction_coord:
                        self.E[str(j1)].append(self.beam.get_reaction(j1, direction='y'))
                self.beam.remove_loads(PointLoadV(j[0], j[1]), remove_all=True)

        for key1, i1 in dict_dist.items():
            for k in i1:
                self.beam.add_loads(DistributedLoadV(k[0], k[1]))
                self.beam.analyse()
                if key1 == 'D':
                    self.distd_sql.append(k[0])
                    self.distd_range_sql.append(k[1])
                    for k1 in self.reaction_coord:
                        self.RD[str(k1)].append(self.beam.get_reaction(k1, direction='y'))
                elif key1 == 'L':
                    self.distl_sql.append(k[0])
                    self.distl_range_sql.append(k[1])
                    for k1 in self.reaction_coord:
                        self.RL[str(k1)].append(self.beam.get_reaction(k1, direction='y'))
                elif key1 == 'Lr':
                    self.distlr_sql.append(k[0])
                    self.distlr_range_sql.append(k[1])
                    for k1 in self.reaction_coord:
                        self.RLr[str(k1)].append(self.beam.get_reaction(k1, direction='y'))
                elif key1 == 'E':
                    self.diste_sql.append(k[0])
                    self.diste_range_sql.append(k[1])
                    for k1 in self.reaction_coord:
                        self.E[str(k1)].append(self.beam.get_reaction(k1, direction='y'))
                self.beam.remove_loads(DistributedLoadV(k[0], k[1]), remove_all=True)

        for cord in self.reaction_coord:
            self.post_output[str(cord)] = [sum(self.RD[str(cord)]), sum(self.RL[str(cord)]), sum(self.RLr[str(cord)]),
                                           sum(self.E[str(cord)])]

    # # # def beam_plot(self):
    # # #     '''
    # # #     Plot shear, moment and deflection diagrams
    # # #     '''
    # # #     self.fig_1[self.vs.index(max(self.vs))].show()
    # # #     self.fig_2[self.vs.index(max(self.vs))].show()

    def beam_design(self):
        '''
        Design the beam by selecting sections that have bending, shear and deflection DCR less than 1.
        '''

        self.fb_actual = self.mmax * 12 * 1000 / self.beam_size[6]
        self.fb_allow = self.cd * self.beam_size[9] * self.beam_size[8]
        self.fv_actual = 1.5 * self.vact_max * 1000 / self.beam_size[3]
        self.fv_allow = self.cd * self.beam_size[7]
        self.defl_allow = self.length * 12 / 240

        self.bending_dcr = self.fb_actual / self.fb_allow
        self.shear_dcr = self.fv_actual / self.fv_allow
        # self.defl_dcr=self.defmax*12/self.defl_allow

        if self.bending_dcr < 1 and self.shear_dcr < 1 and self.defmax < (self.length * 12 / 240):
            self.beam_sec = self.beam_size[0]
            # self.beam_section.append(self.beam_size[0])
        else:
            self.beam_sec == 'None'