import sqlite3
from UI_Wood.stableVersion3.run.shearWall import ShearWallStoryBy
from PySide6.QtWidgets import QDialog


class ShearWallSync2:
    def __init__(self, GridClass):
        ShearWallInput = "D://git/Wood/Output/ShearWall_Input.db"
        ShearWallOutput = "D://git/Wood/Output/ShearWall_output.db"
        shearWallTable2 = "shearwalldesign"
        inputDB = sqlite3.connect(ShearWallInput)
        outputDB = sqlite3.connect(ShearWallOutput)
        self.cursorInput = inputDB.cursor()
        self.cursorOutput = outputDB.cursor()
        data = self.exportWalls()
        for story, shearWalls in enumerate(list(data.values())):
            shearWallStoryDesigned = ShearWallStoryBy(shearWalls, GridClass)
            if story == len(shearWalls) - 1:
                self.report = True
            if shearWallStoryDesigned.result == QDialog.Accepted:
                continue
            else:
                break

    def exportWalls(self):
        shearWallTable1 = "WallTable"

        row = self.cursorInput.execute(
            f"SELECT Story, Wall_Label, Coordinate_start, Coordinate_end FROM {shearWallTable1}")
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
            if i[0] == "Roof":
                MainDict["999999"].append({
                    "story": i[0],
                    "label": i[1],
                    "coordinate": (i[2], i[3])
                })
            else:
                MainDict[i[0]].append({
                    "story": i[0],
                    "label": i[1],
                    "coordinate": (i[2], i[3])
                })
        return MainDict
