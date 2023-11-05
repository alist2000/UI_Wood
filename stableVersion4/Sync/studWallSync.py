import sqlite3
import string

from UI_Wood.stableVersion4.output.studWall_output import StudWall_output
from UI_Wood.stableVersion4.output.shearWall_output import EditLabel
from WOOD_DESIGN.mainstud import MainStud


class StudWallSync:
    def __init__(self, studWall, height):
        studWallEditedInstance = EditLabel(studWall, "studWall")
        studWallEdited = list(reversed(studWallEditedInstance.shearWalls_rev))
        self.studWallOutPut = StudWall_output(studWallEdited, height)
        print("*** STUD PROP IS HERE", self.studWallOutPut.studWallProperties)
        studInstance = MainStud()
        # print(studInstance.query)
        studWallId = 1
