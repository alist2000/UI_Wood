from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
import json
import sys


# Subject
class Subject:
    def __init__(self):
        self.subscribers = []

    def add_subscriber(self, item):
        self.subscribers.append(item)

    def remove_subscriber(self, item):
        self.subscribers.remove(item)

    def manage(self):
        for subscriber in self.subscribers:
            subscriber.update(self)


# Concrete Subject
class Save(Subject):
    def __init__(self, mainPage):
        Subject.__init__(self)
        self.mainPage = mainPage
        self.data = None

    def save_data(self):
        # Define the data to save
        self.data = {
            'general_information': 'value1',
            'general_properties': self.mainPage.mainPage.inputs,
            "seismic_parameters": {},
            "load_set": "",
            'tab': {}
        }

        # Save every thing user draw
        for i in range(len(self.mainPage.mainPage.grid)):
            self.data["tab"][i] = {}
            self.data["tab"][i]["post"] = list(self.mainPage.mainPage.grid[i].post_instance.post_prop.values())
            self.data["tab"][i]["beam"] = list(self.mainPage.mainPage.grid[i].beam_instance.beam_rect_prop.values())
            self.data["tab"][i]["joist"] = list(self.mainPage.mainPage.grid[i].joist_instance.rect_prop.values())
            self.data["tab"][i]["studWall"] = list(
                self.mainPage.mainPage.grid[i].studWall_instance.studWall_rect_prop.values())
            self.data["tab"][i]["loadMap"] = list(self.mainPage.mainPage.grid[i].load_instance.rect_prop.values())
            shearWall_values = list(self.mainPage.mainPage.grid[i].shearWall_instance.shearWall_rect_prop.values())
            # drop start and end post objects
            for item in shearWall_values:
                item["post"]["end_rect_item"] = "post end"
                item["post"]["start_rect_item"] = "post start"
            self.data["tab"][i]["shearWall"] = shearWall_values

        # Save Seismic parameters
        seismic_parameters = ["S1", "Ss", "Fa", "Fv", "I", "T model", "R Factor", "Risk Category"]
        for i in range(len(seismic_parameters)):
            if i <= 6:
                self.data["seismic_parameters"][seismic_parameters[i]] = self.mainPage.spin_values[i]
            else:
                self.data["seismic_parameters"][seismic_parameters[i]] = self.mainPage.combo_values[0]

        # Save Load Sets
        self.data["load_set"] = self.mainPage.dialogPage2.all_set_load

        self.manage()

    def save_clicked(self):
        # SLOT
        for currentTab in range(len(self.mainPage.mainPage.grid)):
            self.mainPage.mainPage.grid[currentTab].run_control()
        self.save_data()

        # Open QFileDialog to choose where to save the json file
        file_name, _ = QFileDialog.getSaveFileName(self.mainPage.mainPage, 'Save JSON file', '', 'JSON Files (*.json)')

        # If a directory is selected, save the data as a json file
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(self.data, f)
