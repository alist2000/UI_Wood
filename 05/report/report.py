from abc import ABC, abstractmethod


class Inputs:
    def __init__(self):
        self.information = None
        self.general_properties = None

    def Information(self, inputs):
        project_title = inputs[0]
        company = inputs[1]
        designer = inputs[2]
        client = inputs[3]
        comment = inputs[4]
        unit_system = inputs[5]
        information_dict = {
            "project_title": project_title,
            "company": company,
            "designer": designer,
            "client": client,
            "comment": comment,
            "unit_system": unit_system
        }
        self.information = information_dict

    def General_prop(self, values):
        self.general_properties = values

    def collaboration(self):
        info = self.information
        general_properties = self.general_properties
        return info, general_properties


class report:
    def __init__(self, Input_instance):
        self.final_value = Input_instance

    def collaboration(self):
        pass

    def result(self):
        pass
