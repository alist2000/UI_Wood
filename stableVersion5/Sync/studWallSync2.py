import sqlite3
from UI_Wood.stableVersion5.run.studWall import StudWallStoryBy
from PySide6.QtWidgets import QDialog


class StudWallSync2:
    def __init__(self, GridClass):
        StudWallOutput = "D://git/Wood/Output/stud_report.db"
        outputDB = sqlite3.connect(StudWallOutput)
        self.cursorOutput = outputDB.cursor()
        data = self.exportWalls()
        for story, studWalls in enumerate(list(data.values())):
            storyName = list(data.keys())[story]
            studWallStoryDesigned = StudWallStoryBy(studWalls, GridClass, storyName)
            if story == len(studWalls) - 1:
                self.report = True
            if studWallStoryDesigned.result == QDialog.Accepted:
                continue
            else:
                break

    def exportWalls(self):
        studWallTable2 = "STUD_REPORT_FILE"
        row = self.cursorOutput.execute(
            f"SELECT story, label, Coordinate_start, Coordinate_end, size, dc, dcr_b,"
            f" d_comb FROM {studWallTable2}")
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
                    "coordinate": (i[2], i[3]),
                    "size": i[4],
                    "dcr_comp": i[5],
                    "dcr_bend": i[6],
                    "dcr_comb": i[7]
                })
            else:
                MainDict[i[0]].append({
                    "story": i[0],
                    "label": i[1],
                    "coordinate": (i[2], i[3]),
                    "size": i[4],
                    "dcr_comp": i[5],
                    "dcr_bend": i[6],
                    "dcr_comb": i[7]
                })
        return MainDict
