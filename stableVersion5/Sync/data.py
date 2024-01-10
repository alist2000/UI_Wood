# Observer
class Update:
    def __init__(self):
        self.general_information = None
        self.general_properties = None
        self.seismic_parameters = None
        self.load_set = None
        self.tab = None

    def update(self, subject):
        pass


# Concrete observer / Subscriber
class Data(Update):

    def update(self, subject):
        self.general_information = subject.data["general_information"]
        self.general_properties = subject.data["general_properties"]
        self.seismic_parameters = subject.data["seismic_parameters"]
        self.load_set = subject.data["load_set"]
        self.tab = subject.data["tab"]

        print(self.general_information)
        print(self.general_properties)
        print(self.seismic_parameters)
        print(self.load_set)
        print(self.tab)
