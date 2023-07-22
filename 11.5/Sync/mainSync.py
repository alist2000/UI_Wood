from Sync.data import Data


class mainSync(Data):
    def __init__(self):
        super().__init__()

        print(self.general_information)
        print(self.general_properties)
        print(self.seismic_parameters)
        print(self.load_set)
        print(self.tab)


class ControlGeneralProp:
    def __init__(self, generalProp):
        self.generalProp = generalProp

        pass


class ControlSeismicParameter:
    def __init__(self, seismicPara):
        self.seismicPara = seismicPara

        pass


class ControlTab:
    def __init__(self, tab):
        self.tab = tab

        for Tab in self.tab:
            pass
