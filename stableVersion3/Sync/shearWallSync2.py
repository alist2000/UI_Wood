import sqlite3
from UI_Wood.stableVersion3.run.shearWall import ShearWallStoryBy
from PySide6.QtWidgets import QDialog


class ShearWallSync2:
    def __init__(self, GridClass):
        ShearWallOutput = "D://git/Wood/Output/ShearWall_output.db"
        outputDB = sqlite3.connect(ShearWallOutput)
        self.cursorOutput = outputDB.cursor()
        data = self.exportWalls()
        for story, shearWalls in enumerate(list(data.values())):
            storyName = list(data.keys())[story]
            shearWallStoryDesigned = ShearWallStoryBy(shearWalls, GridClass, storyName)
            if story == len(shearWalls) - 1:
                self.report = True
            if shearWallStoryDesigned.result == QDialog.Accepted:
                continue
            else:
                break

    def exportWalls(self):
        shearWallTable2 = "shearwalldesign"
        row = self.cursorOutput.execute(
            f"SELECT Story, Wall_Label, Coordinate_start, Coordinate_end,Shearwall_Type, Shear_DCR, tension_dcr_left,"
            f" comp_dcr_left, tension_dcr_right, comp_dcr_right, deflection_dcr_ FROM {shearWallTable2}")
        data = row.fetchall()

        stories = set()
        if data:
            for i in data:
                if i[0] == "Roof":
                    story = "999999"
                else:
                    story = i[0]
                stories.add(story)
        storiesList = list(stories)
        storiesList.sort()

        stories = set(storiesList)

        MainDict = {}
        for i in stories:
            MainDict[i] = []

        for i in data:
            try:
                maxComp = max(round(float(i[7]), 2), round(float(i[9]), 2))
            except:
                maxComp = "-"
            try:
                maxTension = max(round(float(i[6]), 2), round(float(i[8]), 2))
            except:
                maxTension = "-"
            if i[0] == "Roof":

                MainDict["999999"].append({
                    "story": i[0],
                    "label": i[1],
                    "coordinate": (i[2], i[3]),
                    "type": i[4],
                    "dcr_shear": i[5],
                    "dcr_tension": maxTension,
                    "dcr_compression": maxComp
                })
            else:
                MainDict[i[0]].append({
                    "story": i[0],
                    "label": i[1],
                    "coordinate": (i[2], i[3]),
                    "type": i[4],
                    "dcr_shear": i[5],
                    "dcr_tension": maxTension,
                    "dcr_compression": maxComp
                })
        return MainDict
