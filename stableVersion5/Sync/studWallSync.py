import sqlite3
import string

from UI_Wood.stableVersion5.output.studWall_output import StudWall_output
from UI_Wood.stableVersion5.output.shearWall_output import EditLabel
from WOOD_DESIGN.mainstud import MainStud_version5


class StudWallSync:
    def __init__(self, studWall, height, story, db):
        EditLabel(studWall, height[0], "studWall")
        self.studWallOutPut = StudWall_output(studWall[-1], height[-1], story, db)
        self.studWallTab = self.studWallOutPut.studWallProperties_everyTab
        MainStud_version5(story)
