import sqlite3
import string

from UI_Wood.stableVersion5.output.shearWallSql import MidlineSQL, SeismicParamsSQL
from UI_Wood.stableVersion5.output.shearWall_output import ShearWall_output, EditLabel


class ShearWallSync:
    def __init__(self, shearWall, height, story, db, edit_label=True):
        if edit_label:
            EditLabel(shearWall, height[0])
        self.shearWallOutPut = ShearWall_output(shearWall[-1], height[-1], story, db)
        self.shearWallTab = self.shearWallOutPut.shearWallProperties_everyTab


class ControlSeismicParameter:
    def __init__(self, seismicPara, storyName, areaLoad, magLoad, areaJoist, DB):
        self.seismicPara = seismicPara
        self.seismicPara["story_name"] = storyName
        self.seismicPara["load_area"] = areaLoad
        self.seismicPara["load_magnitude"] = magLoad
        self.seismicPara["joist_area"] = areaJoist

        # DB = DataBaseSeismic()
        # DB.SeismicParams(seismicPara)
        DB.Loads(storyName, areaLoad, magLoad, areaJoist)


class DataBaseSeismic:
    def __init__(self):
        self.seismicParamsDB = SeismicParamsSQL()

    def SeismicParams(self, seismicParams):
        self.seismicParamsDB.seismicParams()
        self.seismicParamsDB.cursor.execute(
            'INSERT INTO seismicParams (S1, Ss, Fa, Fv,'
            ' I, T_model, R_factor, risk_category, Regular_Building) values(?, ?, ?, ?, ?, ?, ?, ?, ?)',
            [seismicParams["S1"],
             seismicParams["Ss"],
             seismicParams["Fa"],
             seismicParams["Fv"],
             seismicParams["I"],
             seismicParams["T model"],
             seismicParams["R Factor"],
             seismicParams["Risk Category"],
             seismicParams["Regular Building"],
             ])
        self.seismicParamsDB.conn.commit()

    def Loads(self, storyName, areaLoad, magLoad, areaJoist):
        for i, storyNameItem in enumerate(storyName):
            tableName = self.seismicParamsDB.loadData(storyNameItem)
            for j in range(len(areaLoad[i])):
                self.seismicParamsDB.cursor.execute(
                    f'INSERT INTO {tableName} (Story, joist_area, load_area, load_magnitude) values(?, ?, ?, ?)',
                    [storyNameItem,
                     areaJoist[i],
                     areaLoad[i][j],
                     magLoad[i][j],
                     ])
            self.seismicParamsDB.conn.commit()


class ControlMidLine:
    def __init__(self, midline):
        DB = DataBaseMidline()
        DB.Loads(midline)


class DataBaseMidline:
    def __init__(self):
        self.midLineDB = MidlineSQL()

    def Loads(self, midLine):
        for storyName, lineProp in midLine.items():
            for line in lineProp:
                lineName = list(line.keys())[0]
                lineLoads = line[lineName]
                tableName = self.midLineDB.loadData(storyName, lineName)
                for loadItem in lineLoads:
                    area = loadItem["area"]
                    mag = loadItem["magnitude"]
                    self.midLineDB.cursor.execute(
                        f'INSERT INTO {tableName} (Story, Line, load_area, load_magnitude) values(?, ?, ?, ?)',
                        [storyName,
                         lineName,
                         area,
                         mag,
                         ])
                self.midLineDB.conn.commit()


class MidlineEdit:
    def __init__(self, lineNames, midLine, noShearWallLines):
        self.names = lineNames
        self.midLine = midLine
        self.noShearWallLines = noShearWallLines
        self.names.sort()

        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.boundaryLineNoShearWall = {}

        self.names = self.sort_data_names()
        nameString = []
        nameNum = []
        for item in self.names:
            if item[0] in alphabet:
                nameString.append(item)
            else:
                nameNum.append(item)
        nameString.sort(key=len)
        nameNum.sort(key=len)
        firstLast = [nameString[0], nameString[-1], nameNum[0], nameNum[-1]]
        self.newNamesDict = {}
        for level, lines in midLine.items():
            self.boundaryLineNoShearWall[level] = list(set(noShearWallLines[level]) & set(firstLast))
            self.newNamesDict[level] = []
            for line in lines:
                lineLabel = list(line.keys())[0]
                if lineLabel not in noShearWallLines[level] or lineLabel in firstLast:
                    self.newNamesDict[level].append(lineLabel)
                else:
                    self.newNamesDict[level].append(0)

        new_midlines, before_dict = self.generate_final_midlines(
            [nameString[0], nameString[-1], nameNum[0], nameNum[-1]])

        self.update_midlines(new_midlines, before_dict)

        # OUTPUT
        self.newMidline = new_midlines

    def sort_data_names(self):
        alphabet = string.ascii_uppercase
        name_string = sorted([item for item in self.names if item[0] in alphabet], key=len)
        name_num = sorted([item for item in self.names if item[0] not in alphabet], key=len)
        return name_num + name_string

    def generate_final_midlines(self, firstLast):
        new_midlines = {}
        before_dict = {}
        for level, lines in self.midLine.items():
            new_midlines[level] = []
            before_label_list = []
            for line in lines:
                line_label = list(line.keys())[0]
                if line_label not in firstLast and line_label in self.noShearWallLines[level]:
                    index_label = self.names.index(line_label)
                    i = 1
                    before_label = self.newNamesDict[level][index_label - i]
                    while not before_label:
                        i += 1
                        before_label = self.newNamesDict[level][index_label - i]
                    before_label_list.append({before_label: list(line.values())[0]})
                if line_label not in self.noShearWallLines[level] or line_label in firstLast:
                    new_midlines[level].append(line)
            before_dict[level] = before_label_list
        return new_midlines, before_dict

    @staticmethod
    def update_midlines(new_midlines, before_dict):
        for level, lines in new_midlines.items():
            lines2 = before_dict[level]
            for line in lines:
                for line2 in lines2:
                    line_label = list(line.keys())[0]
                    line_label2 = list(line2.keys())[0]
                    if line_label == line_label2:
                        line[line_label] += line2[line_label2]


def NoShearWallLines(shearWallLines, names_set):
    noShearWalls = {}
    for story, lines in shearWallLines.items():
        noShearWalls[story] = set()
        noShearWalls[story] = names_set - lines
        noShearWalls[story] = list(noShearWalls[story])
        noShearWalls[story].sort()
    return noShearWalls


class ShearWallStoryCount:
    storyFinal = 1
