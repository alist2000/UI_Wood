from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
import json
import sys


class Save:
    def __init__(self, mainPage):
        self.mainPage = mainPage

    def save_clicked(self):
        # Define the data to save
        data = {
            'general_information': 'value1',
            'general_properties': self.mainPage.mainPage.inputs,
            "seismic_parameters": {},
            "load_set": "",
            'tab': {}
        }

        # Save every thing user draw
        for i in range(len(self.mainPage.mainPage.grid)):
            data["tab"][i] = {}
            data["tab"][i]["post"] = list(self.mainPage.mainPage.grid[i].post_instance.post_prop.values())
            data["tab"][i]["beam"] = list(self.mainPage.mainPage.grid[i].beam_instance.beam_rect_prop.values())
            data["tab"][i]["joist"] = list(self.mainPage.mainPage.grid[i].joist_instance.rect_prop.values())
            data["tab"][i]["studWall"] = list(
                self.mainPage.mainPage.grid[i].studWall_instance.studWall_rect_prop.values())
            data["tab"][i]["loadMap"] = list(self.mainPage.mainPage.grid[i].load_instance.rect_prop.values())
            shearWall_values = list(self.mainPage.mainPage.grid[i].shearWall_instance.shearWall_rect_prop.values())
            # drop start and end post objects
            for item in shearWall_values:
                item["post"]["end_rect_item"] = "post end"
                item["post"]["start_rect_item"] = "post start"
            data["tab"][i]["shearWall"] = shearWall_values

        # Save Seismic parameters
        seismic_parameters = ["S1", "Ss", "Fa", "Fv", "T model", "R Factor", "Risk Category"]
        for i in range(len(seismic_parameters)):
            if i <= 5:
                data["seismic_parameters"][seismic_parameters[i]] = self.mainPage.spin_values[i]
            else:
                data["seismic_parameters"][seismic_parameters[i]] = self.mainPage.combo_values[0]

        # Save Load Sets
        data["load_set"] = self.mainPage.dialogPage2.all_set_load

        # Open QFileDialog to choose where to save the json file
        file_name, _ = QFileDialog.getSaveFileName(self.mainPage.mainPage, 'Save JSON file', '', 'JSON Files (*.json)')

        # If a directory is selected, save the data as a json file
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(data, f)
