from UI_Wood.stableVersion5.post_new import magnification_factor
from UI_Wood.stableVersion5.back.load_control import range_intersection

from UI_Wood.stableVersion5.output.beam_output import ControlDistributetLoad, ControlLineLoad, CombineDistributes
from UI_Wood.stableVersion5.output.studWallSql import studWallSQL


class StudWall_output:
    def __init__(self, studWalls, height):
        self.studWallProperties = {}
        self.studWallExistLine = {}

        self_weight_dict = {"I": 10, "E": 20}

        self.roof_level_number = len(studWalls)
        db = studWallSQL()
        db.createTable()
        db.createTable("Exterior")
        db.createTable("Interior4")
        db.createTable("Interior6")
        studWallId = 1
        for story, studWallsTab in enumerate(studWalls):
            self.Story = story + 1
            studWallProperties_everyTab = []
            if self.Story == self.roof_level_number:
                StoryName = "Roof"
            else:
                StoryName = self.Story
            self.studWallExistLine[str(StoryName)] = set()
            for StudWallItem in studWallsTab:
                label = StudWallItem["label"][2:]
                self.length = StudWallItem["length"] / magnification_factor
                opening_width = 0  # for now
                interior_exterior = StudWallItem["interior_exterior"][0].upper()
                self_weight = self_weight_dict[interior_exterior]
                direction = StudWallItem["direction"]
                if direction == "N-S":
                    orientation = "NS"
                    direction_index = 1
                    constant_index = 0
                else:
                    orientation = "EW"
                    direction_index = 0
                    constant_index = 1

                self.start = min(StudWallItem["coordinate"][0][direction_index],
                                 StudWallItem["coordinate"][1][direction_index]) / magnification_factor
                self.end = max(StudWallItem["coordinate"][0][direction_index],
                               StudWallItem["coordinate"][1][direction_index]) / magnification_factor
                constant = StudWallItem["coordinate"][0][constant_index] / magnification_factor
                if direction == "N-S":
                    coordinateStart = (constant, self.start)
                    coordinateEnd = (constant, self.end)
                else:
                    coordinateStart = (self.start, constant)
                    coordinateEnd = (self.end, constant)

                n1 = len(str(self.start).split(".")[1])
                n2 = len(str(self.end).split(".")[1])
                decimal_number = max(n1, n2)
                # distributed load control
                self.distributedLoad = ControlDistributetLoad(StudWallItem["load"]["joist_load"]["load_map"],
                                                              self.start)
                self.lineLoad = ControlLineLoad(StudWallItem["load"]["line"], StudWallItem, direction_index)
                print("loadset line load", self.lineLoad.loadSet)
                self.finalDistributedLoad = CombineDistributes(self.distributedLoad.loadSet, self.lineLoad.loadSet,
                                                               decimal_number)
                start_load, end_load, dead_load, live_load, lr_load, snow_load = self.create_string_for_loads(
                    self.finalDistributedLoad.loadSet)
                db.cursor.execute(
                    'INSERT INTO WallTable (ID, Story, Coordinate_start, Coordinate_end, Wall_Label,'
                    ' Wall_Length, Story_Height, Int_Ext,  Wall_Self_Weight, Wall_Width,'
                    ' start, end, Rd, Rl, Rlr, Rs, Wall_Orientation) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    [
                        studWallId, str(StoryName), str(coordinateStart), str(coordinateEnd), label,
                        round(self.end - self.start, max(n1, n2)),
                        height[story],
                        interior_exterior, self_weight, int(StudWallItem["thickness"][0]),
                        start_load,
                        end_load, dead_load, live_load,
                        lr_load,
                        snow_load, orientation
                    ])
                db.conn.commit()

                if interior_exterior == "E":
                    tableName = "Exterior"
                else:
                    if int(StudWallItem["thickness"][0]) == 4:
                        tableName = "Interior4"
                    else:
                        tableName = "Interior6"

                db.cursor.execute(
                    f'INSERT INTO {tableName} (ID, Story, Wall_Label,'
                    ' Wall_Length, Story_Height, Int_Ext,  Wall_Self_Weight, Wall_Width,'
                    ' start, end, Rd, Rl, Rlr, Rs, Wall_Orientation) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    [
                        studWallId, str(StoryName), label, round(self.end - self.start, max(n1, n2)),
                        height[story],
                        interior_exterior, self_weight, int(StudWallItem["thickness"][0]),
                        start_load,
                        end_load, dead_load, live_load,
                        lr_load,
                        snow_load, orientation
                    ])
                db.conn.commit()
                studWallId += 1
                self.studWall_dict = {
                    "label": label,
                    "coordinate": [self.start, self.end],
                    "story": StoryName,
                    "length": round(self.end - self.start, max(n1, n2)),
                    "height": height[story],
                    "interior_exterior": interior_exterior,
                    "self_weight": self_weight,
                    "thickness": StudWallItem["thickness"],
                    "direction": orientation,
                    "load": {
                        "distributed": self.finalDistributedLoad.loadSet
                    },
                }
                studWallProperties_everyTab.append(self.studWall_dict)
            self.studWallProperties[story] = studWallProperties_everyTab

    @staticmethod
    def create_string_for_loads(loadSet):
        startList = [i["start"] for i in loadSet]
        start_string = list_to_string(startList)

        endList = [i["end"] for i in loadSet]
        endList_string = list_to_string(endList)

        dead = []
        live = []
        lr = []
        snow = []
        for item in loadSet:
            load = item["load"]
            for Load in load:
                if Load["type"] == "Dead":
                    dead.append(Load["magnitude"])
                elif Load["type"] == "Live":
                    live.append(Load["magnitude"])
                elif Load["type"] == "Live Roof":
                    lr.append(Load["magnitude"])
                elif Load["type"] == "snow":
                    snow.append(Load["magnitude"])

        dead_string = list_to_string(dead)

        live_string = list_to_string(live)

        lr_string = list_to_string(lr)

        snow_string = list_to_string(snow)

        return start_string, endList_string, dead_string, live_string, lr_string, snow_string


def list_to_string(myList):
    s = ",".join(map(str, myList))
    return s
