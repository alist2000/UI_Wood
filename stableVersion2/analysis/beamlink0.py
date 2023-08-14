class Link0:

    def __init__(self, beam_):
        self.beam_ = beam_
        self.names()

    def names(self):

        ## Distributed
        for i in self.beam_['load']['distributed']:
            for jind, j in enumerate(i['load']):
                if j['type'] == 'Dead':
                    j['type'] = 'D'
                elif j['type'] == 'Live':
                    j['type'] = 'L'
                elif j['type'] == 'Live Roof':
                    j['type'] = 'Lr'
                elif j['type'] == 'Snow':
                    j['type'] = 'S0'
                elif j['type'] == 'Seismic':
                    j['type'] = 'E0'
                else:
                    continue

        for i in self.beam_['load']['distributed']:
            for jind, j in enumerate(i['load']):
                if j['type'] == 'Dead Super':
                    del i['load'][jind]

                    ## Point
        for i in self.beam_['load']['point']:
            for j in i['load']:
                if j['type'] == 'Dead':
                    j['type'] = 'D'
                elif j['type'] == 'Live':
                    j['type'] = 'L'
                elif j['type'] == 'Live Roof':
                    j['type'] = 'Lr'
                elif j['type'] == 'Snow':
                    j['type'] = 'S0'
                elif j['type'] == 'Seismic':
                    j['type'] = 'E0'
