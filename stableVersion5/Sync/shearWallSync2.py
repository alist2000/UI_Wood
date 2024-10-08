import sqlite3
from UI_Wood.stableVersion5.run.shearWall import ShearWallStoryBy
from PySide6.QtWidgets import QDialog
from UI_Wood.stableVersion5.path import PathHandler, shearWallOutputPath


class ShearWallSync2:
    def __init__(self, GridClass, storyName):
        ShearWallOutput = PathHandler(shearWallOutputPath)
        outputDB = sqlite3.connect(ShearWallOutput)
        self.cursorOutput = outputDB.cursor()
        data = self.exportWalls(storyName)
        for story, shearWalls in enumerate(list(data.values())):
            # storyName = list(data.keys())[story]
            self.shearWallStoryDesigned = ShearWallStoryBy(shearWalls, GridClass, storyName)
            if story == len(shearWalls) - 1:
                self.report = True

    def exportWalls(self, story):
        shearWallTable2 = "shearwalldesign"
        row = self.cursorOutput.execute(
            f"SELECT Story, Wall_Label, Coordinate_start, Coordinate_end,Shearwall_Type, Shear_DCR, tension_dcr_left,"
            f" comp_dcr_left, tension_dcr_right, comp_dcr_right, deflection_dcr_ FROM {shearWallTable2} WHERE Story = '{story}'")
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
                    "dcr_compression": maxComp,
                    "dcr_deflection": i[10]
                })
            else:
                MainDict[i[0]].append({
                    "story": i[0],
                    "label": i[1],
                    "coordinate": (i[2], i[3]),
                    "type": i[4],
                    "dcr_shear": i[5],
                    "dcr_tension": maxTension,
                    "dcr_compression": maxComp,
                    "dcr_deflection": i[10]
                })
        return MainDict
