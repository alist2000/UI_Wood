import sqlite3
import string

from UI_Wood.stableVersion2.output.studWall_output import StudWall_output
from UI_Wood.stableVersion2.output.shearWall_output import EditLabel


class StudWallSync:
    def __init__(self, studWall, height):
        studWallEditedInstance = EditLabel(studWall)
        studWallEdited = list(reversed(studWallEditedInstance.shearWalls_rev))
        self.studWallOutPut = StudWall_output(studWallEdited, height)
        print("*** STUD PROP IS HERE", self.studWallOutPut.studWallProperties)
        studWallId = 1
