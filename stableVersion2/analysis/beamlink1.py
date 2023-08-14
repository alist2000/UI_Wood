class Link1:
    def __init__(self, beam_new):
        self.beam_new = beam_new
        self.length = None
        self.supports = None
        self.dist_loads = None
        self.p_loads = None
        self.dict_dist = None
        self.dict_point = None

        self.ty = None

        self.param()
        self.dist()
        self.point()

    def param(self):

        self.length = self.beam_new['length']
        self.supports = tuple(self.beam_new['support'])

    def dist(self):
        types = []
        range = []
        for i in self.beam_new['load']['distributed']:
            types.append([])
            range.append((i['start'], i['end']))
            for j in i['load']:
                types[self.beam_new['load']['distributed'].index(i)].append([j['type'], j['magnitude']])

        self.ty = types.copy()

        self.dict_dist = {}
        loadtypes = set()
        for ii in types:
            for jj in ii:
                loadtypes.add(jj[0])

        loadtypes_list = list(loadtypes)
        for i3 in loadtypes_list:
            self.dict_dist[i3] = []

        for di4, i4 in enumerate(types):
            for j4 in i4:
                self.dict_dist[j4[0]].append((-j4[1], range[di4]))

    def point(self):
        types = []
        locs = []
        for i in self.beam_new['load']['point']:
            types.append([])
            locs.append(i['start'])
            for j in i['load']:
                types[self.beam_new['load']['point'].index(i)].append([j['type'], j['magnitude']])

        self.dict_point = {}
        loadtypes = set()
        for ii in types:
            for jj in ii:
                loadtypes.add(jj[0])

        loadtypes_list = list(loadtypes)
        for i3 in loadtypes_list:
            self.dict_point[i3] = []

        for di4, i4 in enumerate(types):
            for j4 in i4:
                self.dict_point[j4[0]].append((-j4[1], locs[di4]))
