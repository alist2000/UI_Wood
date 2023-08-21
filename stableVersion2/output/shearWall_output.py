from UI_Wood.stableVersion2.post_new import magnification_factor
from UI_Wood.stableVersion2.back.load_control import range_intersection
from UI_Wood.stableVersion2.output.beam_output import ControlDistributetLoad, ControlLineLoad, CombineDistributes
from UI_Wood.stableVersion2.output.shearWallSql import shearWallSQL


class EditLabel:
    def __init__(self, shearWalls):
        self.shearWalls = shearWalls
        shearWalls_rev = list(reversed(shearWalls))
        self.shearWalls_rev = shearWalls_rev
        full_label, full_label_repeat_index = self.edit_label()
        self.edit_repeated_label(full_label_repeat_index, full_label)

    def edit_label(self):
        max_story = len(self.shearWalls_rev) - 1
        full_label_repeat_index = {}
        full_label = {}

        for i, shearWallTab in enumerate(self.shearWalls_rev):
            label_not_repeat_index = set()
            label_list = []
            for shearWall in shearWallTab:
                labelMain = shearWall["label"]
                base_coordinate = shearWall["coordinate"]
                label_list.append(labelMain)

                if i < max_story:
                    for num, shearWallBottom in enumerate(self.shearWalls_rev[i + 1]):
                        coordinate = shearWallBottom["coordinate"]

                        if coordinate == base_coordinate:
                            shearWallBottom["label"] = labelMain
                            label_not_repeat_index.add(num)

            full_label[str(i)] = label_list

            full_label_repeat_index[str(i + 1)] = list(label_not_repeat_index)

        return full_label, full_label_repeat_index

    def edit_repeated_label(self, repeated_labels_dict, labels):
        maxLabelNumberDict = {}
        for labelTab, labelItems in labels.items():
            label_number = [int(i[2:]) for i in labelItems]
            if label_number:
                max_label = max(label_number)
                maxLabelNumberDict[str(labelTab)] = max_label

        controlLabel = {}
        for tab, numberList in repeated_labels_dict.items():
            controlLabel[str(tab)] = []
            for number in numberList:
                controlLabel[str(tab)].append(labels[str(tab)][number])

        exist_repeated_tab = list(repeated_labels_dict.keys())

        for i, shearWallTab in enumerate(self.shearWalls_rev):
            if str(i) in exist_repeated_tab and shearWallTab:
                labelNumber = maxLabelNumberDict[str(i)]
                for num, shearWall in enumerate(shearWallTab):
                    if num not in repeated_labels_dict[str(i)] and shearWall["label"] in controlLabel[str(i)]:
                        shearWall["label"] = f"SW{str(labelNumber + 1)}"
                        labelNumber += 1


class ShearWall_output:
    def __init__(self, shearWalls, height):
        self.shearWallProperties = {}
        self.shearWallExistLine = {}

        self_weight_dict = {"I": 10, "E": 20}

        self.roof_level_number = len(shearWalls)
        db = shearWallSQL()
        db.createTable()
        shearWallId = 1
        for story, shearWallsTab in enumerate(shearWalls):
            self.Story = story + 1
            shearWallProperties_everyTab = []
            if self.Story == self.roof_level_number:
                StoryName = "Roof"
            else:
                StoryName = self.Story
            self.shearWallExistLine[str(StoryName)] = set()
            for ShearWallItem in shearWallsTab:
                label = ShearWallItem["label"][2:]
                self.length = ShearWallItem["length"] / magnification_factor
                line = ShearWallItem["line_label"]
                self.shearWallExistLine[str(StoryName)].add(line)
                opening_width = 0  # for now
                interior_exterior = ShearWallItem["interior_exterior"][0].upper()
                self_weight = self_weight_dict[interior_exterior]
                direction = ShearWallItem["direction"]
                if direction == "N-S":
                    orientation = "NS"
                    direction_index = 1
                else:
                    orientation = "EW"
                    direction_index = 0

                self.start = min(ShearWallItem["coordinate"][0][direction_index],
                                 ShearWallItem["coordinate"][1][direction_index]) / magnification_factor
                self.end = max(ShearWallItem["coordinate"][0][direction_index],
                               ShearWallItem["coordinate"][1][direction_index]) / magnification_factor

                # reaction control
                Pd, Pl, Pe = self.reaction_control(ShearWallItem["load"]["reaction"], direction_index)

                # share post check
                share_post = self.intersection_control(ShearWallItem["shearWall_intersection"], direction_index)

                n1 = len(str(self.start).split(".")[1])
                n2 = len(str(self.end).split(".")[1])
                decimal_number = max(n1, n2)
                # distributed load control
                self.distributedLoad = ControlDistributetLoad(ShearWallItem["load"]["joist_load"]["load_map"],
                                                              self.start)
                self.lineLoad = ControlLineLoad(ShearWallItem["load"]["line"], ShearWallItem, direction_index)
                print("loadset line load", self.lineLoad.loadSet)
                self.finalDistributedLoad = CombineDistributes(self.distributedLoad.loadSet, self.lineLoad.loadSet,
                                                               decimal_number)
                start_load, end_load, dead_load, live_load, lr_load, snow_load = self.create_string_for_loads(
                    self.finalDistributedLoad.loadSet)
                db.cursor.execute(
                    'INSERT INTO WallTable (ID, Story, Line, Wall_Label,'
                    ' Wall_Length, Story_Height, Opening_Width, Int_Ext,  Wall_Self_Weight,'
                    ' start, end, Rd, Rl, Rlr, Rs, Left_Bottom_End,'
                    ' Right_Top_End, Po_Left, Pl_Left, Pe_Left, Po_Right, Pl_Right, Pe_Right, Wall_Orientation) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,  ?)',
                    [
                        shearWallId, str(StoryName), line, label, round(self.end - self.start, max(n1, n2)),
                        height[story],
                        str(opening_width), interior_exterior, self_weight, start_load, end_load, dead_load, live_load,
                        lr_load,
                        snow_load, str(share_post["left"]),
                        str(share_post["right"]),
                        str(Pd["left"]), str(Pl["left"]), str(Pe["left"]), str(Pd["right"]), str(Pl["right"]),
                        str(Pe["right"]), orientation
                    ])
                db.conn.commit()
                shearWallId += 1
                self.shearWall_dict = {
                    "label": label,
                    "coordinate": [self.start, self.end],
                    "story": StoryName,
                    "line_label": line,
                    "length": round(self.end - self.start, max(n1, n2)),
                    "height": height[story],
                    "opening_width": opening_width,
                    "interior_exterior": interior_exterior,
                    "self_weight": self_weight,
                    "direction": orientation,

                    "load": {
                        "distributed": self.finalDistributedLoad.loadSet,
                        "reaction": {"Dead": Pd, "Live": Pl, "Seismic": Pe}
                    },
                    "share_post": share_post
                }
                shearWallProperties_everyTab.append(self.shearWall_dict)
            self.shearWallProperties[story] = shearWallProperties_everyTab

    def reaction_control(self, reaction, direction_index):
        Pd = {"left": None, "right": None}
        Pl = {"left": None, "right": None}
        Pe = {"left": None, "right": None}
        for load in reaction:
            coordinate = abs((load["start"][direction_index] / magnification_factor) - self.start)
            side = self.side_control(coordinate, self.end, self.length)
            loads = load["load"]
            mag_live_roof = mag_live = 0
            for item in loads:
                loadType = item["type"]
                if loadType == "Dead":
                    Pd[side] = item["magnitude"]
                elif loadType == "Seismic":
                    Pe[side] = item["magnitude"]
                elif loadType == "Live":
                    mag_live = item["magnitude"]
                else:
                    mag_live_roof = item["magnitude"]
            if self.Story < self.roof_level_number:
                if mag_live:
                    Pl[side] = mag_live
                else:
                    Pl[side] = mag_live_roof
            else:
                if mag_live_roof:
                    Pl[side] = mag_live_roof
                else:
                    Pl[side] = mag_live
        return Pd, Pl, Pe

    def intersection_control(self, shearWall_intersection, direction_index):
        share_post = {"left": None, "right": None}
        for shearWall in shearWall_intersection:
            coordinate = abs((shearWall["coordinate"][direction_index] / magnification_factor) - self.start)
            side = self.side_control(coordinate, self.end, self.length)
            label = shearWall["shearWall_label"][2:]
            line_label = shearWall["line_label"]
            share_post[side] = line_label + "-" + label
        return share_post

    @staticmethod
    def side_control(coordinate, end, length):
        acceptable_range = length / 4
        start_consider_range = (0, acceptable_range)
        end_consider_range = (end - acceptable_range, end)
        if start_consider_range[0] <= coordinate <= start_consider_range[1]:
            side = "left"
        else:
            side = "right"
        return side

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
