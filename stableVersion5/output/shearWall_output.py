from UI_Wood.stableVersion5.post_new import magnification_factor
from UI_Wood.stableVersion5.output.beam_output import ControlDistributetLoad, ControlLineLoad, CombineDistributes
import copy
from UI_Wood.stableVersion5.output.shearwall_share_post_load import ShearWall, distribute_loads
from typing import List, Dict, Any


class EditLabel:
    def __init__(self, shearWalls_rev, aboveHeight, transferLoad, itemName="shearWall"):
        # self.shearWalls = shearWalls
        self.itemName = itemName
        self.aboveHeight = aboveHeight
        # shearWalls_rev = list(reversed(shearWalls))
        self.shearWalls_rev = shearWalls_rev
        self.transferLoad = transferLoad
        if all(self.shearWalls_rev):
            self.edit_label()

    def edit_label_old(self):
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
                pointLoadControlInstance = LoadFromAbove(shearWall)

                if i < max_story:
                    for num, shearWallBottom in enumerate(self.shearWalls_rev[i + 1]):
                        coordinate = shearWallBottom["coordinate"]

                        if coordinate == base_coordinate:
                            shearWallBottom["label"] = labelMain
                            label_not_repeat_index.add(num)
                            shearWallBottom = pointLoadControlInstance.pointLoadOnSW(shearWallBottom)

            full_label[str(i)] = label_list

            full_label_repeat_index[str(i + 1)] = list(label_not_repeat_index)

        return full_label, full_label_repeat_index

    def edit_label(self):
        max_story = len(self.shearWalls_rev) - 1
        full_label_repeat_index = {}
        full_label = {}
        labelStory = []
        if self.itemName == "shearWall":
            labelName = "SW"
        else:
            labelName = "ST"
        # labelName = self.shearWalls_rev[0][0]["label"][:2]
        for i, shearWallTab in enumerate(self.shearWalls_rev):
            label = [int(shearWall["label"][2:]) for shearWall in shearWallTab]
            if label:
                labelStory.append(max(label))
            else:
                labelStory.append(0)

        for i, shearWallTab in enumerate(self.shearWalls_rev):
            label_not_repeat_index = set()
            label_list = []
            for shearWall in shearWallTab:
                labelMain = shearWall["label"]
                base_coordinate = shearWall["coordinate"]
                label_list.append(labelMain)
                if self.transferLoad:
                    LoadControlInstance = LoadFromAbove(shearWall, self.aboveHeight)
                transferred = False
                if i < max_story:
                    maxLabel = labelStory[i + 1]
                    for num, shearWallBottom in enumerate(self.shearWalls_rev[i + 1]):
                        coordinate = shearWallBottom["coordinate"]
                        if coordinate == base_coordinate:
                            # if not self.transferLoad:
                            #     shearWallBottom["label"] = labelMain
                            if self.transferLoad:
                                shearWallBottom = LoadControlInstance.pointLoadOnSW(shearWallBottom)
                                shearWallBottom = LoadControlInstance.distLoadOnSW(shearWallBottom)
                            # Self wall weight  also should be transfer from above.
                            # Transfer shear should be done here

                            # # control repeated label
                            # if not self.transferLoad:
                            #     for num1, shearWallBottom1 in enumerate(self.shearWalls_rev[i + 1]):
                            #         if num1 != num and shearWallBottom1["label"] == labelMain:
                            #             maxLabel += 1
                            #             labelStory[i + 1] = maxLabel
                            #             shearWallBottom1["label"] = labelName + str(maxLabel)
                            #             break
                            #
                            #     # label_not_repeat_index.add(num)
                            #
                            #     transferred = True
                            # break

                    if not transferred:  # control and check for transfer manually.
                        pass
            #
            # full_label[str(i)] = label_list
            #
            # full_label_repeat_index[str(i + 1)] = list(label_not_repeat_index)
        #
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
        if self.itemName == "shearWall":
            labelTitle = "SW"
        else:
            labelTitle = "ST"
        for i, shearWallTab in enumerate(self.shearWalls_rev):
            if str(i) in exist_repeated_tab and shearWallTab:
                labelNumber = maxLabelNumberDict[str(i)]
                for num, shearWall in enumerate(shearWallTab):
                    if num not in repeated_labels_dict[str(i)] and shearWall["label"] in controlLabel[str(i)]:
                        shearWall["label"] = f"{labelTitle}{str(labelNumber + 1)}"
                        labelNumber += 1


class LoadFromAbove:
    def __init__(self, swTop, aboveHeight):
        self.swTop = swTop
        self.aboveHeight = aboveHeight

    def pointLoadOnSW(self, swBottom):
        swBottom = swBottom
        reactionLoadsBottom = swBottom["load"]["reaction"]
        reactionLoadsTop = copy.deepcopy(self.swTop["load"]["reaction"])
        editedReactionLoadsTop = []
        for load in reactionLoadsTop:
            load["Transferred"] = True
            editedReactionLoadsTop.append(load)
        reactionLoadsBottom.extend(editedReactionLoadsTop)
        swBottom["load"]["reaction"] = reactionLoadsBottom
        return swBottom

    def distLoadOnSW(self, swBottom):
        swBottom = swBottom

        # Load Map
        loadMapBottom = swBottom["load"]["joist_load"]["load_map"]
        loadMapTop = copy.deepcopy(self.swTop["load"]["joist_load"]["load_map"])
        editedLoadMapTop = []
        for load in loadMapTop:
            load["Transferred"] = True
            editedLoadMapTop.append(load)

        loadMapBottom.extend(editedLoadMapTop)
        swBottom["load"]["joist_load"]["load_map"] = loadMapBottom

        # Line Load
        lineLoadBottom = swBottom["load"]["line"]
        lineLoadTop = copy.deepcopy(self.swTop["load"]["line"])
        editedLineLoadTop = []
        for load in lineLoadTop:
            load["Transferred"] = True
            editedLineLoadTop.append(load)

        lineLoadBottom.extend(editedLineLoadTop)
        swBottom["load"]["line"] = lineLoadBottom

        # SELF WEIGHT
        if self.swTop["interior_exterior"] == "exterior":
            deadLoad = 0.02  # ksf
        else:
            deadLoad = 0.01  # ksf

        coordinateTop = swBottom["coordinate"]
        direction = swBottom["direction"]
        if direction == "N-S":
            swRange = (coordinateTop[0][1], coordinateTop[1][1])
        else:
            swRange = (coordinateTop[0][0], coordinateTop[1][0])
        swStart = min(swRange)
        swEnd = max(swRange)
        # swBottom["load"]["line"].append({"distance": 0, "length": swBottom["length"],
        #                                  "magnitude": deadLoad * self.aboveHeight,
        #                                  "type": "Dead", "Transferred": True})
        swBottom["load"]["joist_load"]["load_map"].append(
            {'from': self.swTop["label"], 'label': 'Self Weight',
             'load': [{'type': 'Dead', 'magnitude': deadLoad * self.aboveHeight}], 'start': swStart,
             'end': swEnd, "Transferred": True})

        return swBottom

    def transferShearLoad(self, swBottom, transfer):
        # sw = {"transfer":[ {"label":"sw5", "percent": 50}, {"label":"sw6", "percent": 50} ]}
        # sw = {"pe_abv": 10}
        # sw = {"pe_main": 10} --> after design calculated and added
        swBottom["pe_abv"] = self.swTop["pe_main"] * transfer["percent"] / 100
        return swBottom

    # for loadItem in reactionLoadsBottom:
    #     start = loadItem["start"]
    #     loads = loadItem["load"]
    #     for loadItemTop in reactionLoadsTop:
    #         startTop = loadItemTop["start"]
    #         loadsTop = loadItemTop["load"]
    #         if start == startTop:
    #             for load in loads:
    #                 mag = load["magnitude"]
    #                 loadType = load["type"]
    #                 for loadTop in loadsTop:
    #                     magTop = loadTop["magnitude"]
    #                     loadTypeTop = loadTop["type"]
    #                     if loadType == loadTypeTop:
    #                         mag += magTop
    #                         break
    #             break

    def loadOnBeam(self, beam):
        pass


class ShearWall_output:
    def __init__(self, shearWalls: List[Dict[str, Any]], height: float, story: str, db):
        self.shearWallProperties = {}
        self.shearWallExistLine = {}
        self_weight_dict = {"I": 10, "E": 20}
        self.roof_level_number = len(shearWalls)
        self.Story = story
        StoryName = story
        self.shearWallExistLine[str(StoryName)] = set()
        self.shearWallProperties_everyTab = []
        # Create ShearWall objects
        shear_wall_objects = []
        for ShearWallItem in shearWalls:
            label = ShearWallItem["label"][2:]
            line = ShearWallItem["line_label"]
            direction = ShearWallItem["direction"]
            self.length = ShearWallItem["length"] / magnification_factor
            if direction == "N-S":
                orientation = "NS"
                direction_index = 1
                constant_index = 0
            else:
                orientation = "EW"
                direction_index = 0
                constant_index = 1
            self.shearWallExistLine[str(StoryName)].add(line)
            self.start = min(ShearWallItem["coordinate"][0][direction_index],
                             ShearWallItem["coordinate"][1][direction_index]) / magnification_factor
            self.end = max(ShearWallItem["coordinate"][0][direction_index],
                           ShearWallItem["coordinate"][1][direction_index]) / magnification_factor
            # Create ShearWall object
            sw = ShearWall(name=label)
            share_post = self.intersection_control(ShearWallItem["shearWall_intersection"], direction_index)

            # Set connections
            if share_post["left"]:
                sw.left_top = share_post["left"].split("-")[-1]
            if share_post["right"]:
                sw.right_bottom = share_post["right"].split("-")[-1]

            # Set initial loads
            load_type = "reaction"
            pl_right = 0
            pl_left = 0
            plr_right = 0
            plr_left = 0
            if load_type in ShearWallItem["load"]:
                for loads in ShearWallItem["load"][load_type]:
                    coordinate = abs((loads["start"][direction_index] / magnification_factor) - self.start)
                    side = self.side_control(coordinate, self.end, self.length)
                    for load in loads["load"]:
                        load_value = load["magnitude"]
                        if load["type"] == "Dead":
                            if side == "left":
                                sw.pd_left += load_value
                            else:
                                sw.pd_right += load_value
                        elif load["type"] == "Live":
                            if side == "left":
                                pl_left += load_value
                            else:
                                pl_right += load_value
                        elif load["type"] == "Seismic":
                            if side == "left":
                                sw.pe_left += load_value
                            else:
                                sw.pe_right += load_value
                        elif load["type"] == "Live Roof":
                            if side == "left":
                                plr_left += load_value
                            else:
                                plr_right += load_value
                    # set priority for live in roof or other.
                    if self.Story != "Roof":
                        if pl_right:
                            live_right = pl_right
                        else:
                            live_right = plr_right
                        if pl_left:
                            live_left = pl_left
                        else:
                            live_left = plr_left
                    else:
                        if plr_right:
                            live_right = plr_right
                        else:
                            live_right = pl_right
                        if plr_left:
                            live_left = plr_left
                        else:
                            live_left = pl_left
                    if side == "left":
                        sw.pl_left += live_left
                    else:
                        sw.pl_right += live_right

            shear_wall_objects.append(sw)

        # Distribute loads
        updated_shear_walls = distribute_loads(shear_wall_objects)

        # Process updated shear walls
        for sw, ShearWallItem in zip(updated_shear_walls, shearWalls):
            self.process_shear_wall(sw, ShearWallItem, height, StoryName, self_weight_dict, db)

    def process_shear_wall(self, sw: ShearWall, ShearWallItem: Dict[str, Any], height: float, StoryName: str,
                           self_weight_dict: Dict[str, int], db):
        label = sw.name
        self.length = ShearWallItem["length"] / magnification_factor
        line = ShearWallItem["line_label"]
        opening_width = 0  # for now
        interior_exterior = ShearWallItem["interior_exterior"][0].upper()
        self_weight = self_weight_dict[interior_exterior]
        direction = ShearWallItem["direction"]
        v_abv = 0
        pe_abv = 0

        if direction == "N-S":
            orientation = "NS"
            direction_index = 1
            constant_index = 0
        else:
            orientation = "EW"
            direction_index = 0
            constant_index = 1

        self.start = min(ShearWallItem["coordinate"][0][direction_index],
                         ShearWallItem["coordinate"][1][direction_index]) / magnification_factor
        self.end = max(ShearWallItem["coordinate"][0][direction_index],
                       ShearWallItem["coordinate"][1][direction_index]) / magnification_factor
        constant = ShearWallItem["coordinate"][0][constant_index] / magnification_factor

        if direction == "N-S":
            coordinateStart = (constant, self.start)
            coordinateEnd = (constant, self.end)
        else:
            coordinateStart = (self.start, constant)
            coordinateEnd = (self.end, constant)

        # Share post check
        share_post = self.intersection_control(ShearWallItem["shearWall_intersection"], direction_index)

        n1 = len(str(self.start).split(".")[1])
        n2 = len(str(self.end).split(".")[1])
        decimal_number = max(n1, n2)

        # Distributed load control
        self.distributedLoad = ControlDistributetLoad(ShearWallItem["load"]["joist_load"]["load_map"],
                                                      self.start, self.length)
        self.lineLoad = ControlLineLoad(ShearWallItem["load"]["line"], ShearWallItem, direction_index)
        self.finalDistributedLoad = CombineDistributes(self.distributedLoad.loadSet, self.lineLoad.loadSet,
                                                       decimal_number, self.length)
        start_load, end_load, dead_load, live_load, lr_load, snow_load = self.create_string_for_loads(
            self.finalDistributedLoad.loadSet)

        # Insert into database
        db.cursor.execute(
            'INSERT INTO WallTable (ID, Story, Coordinate_start, Coordinate_end, Line, Wall_Label,'
            ' Wall_Length, Story_Height, Opening_Width, Int_Ext,  Wall_Self_Weight,'
            ' start, end, Rd, Rl, Rlr, Rs, Left_Bottom_End,'
            ' Right_Top_End, Po_Left, Pl_Left, Pe_Left, Po_Right, Pl_Right, Pe_Right, Wall_Orientation, v_abv, pe_abv) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            [
                label, str(StoryName), str(coordinateStart), str(coordinateEnd), line, label,
                round(self.length, 1), height, str(opening_width), interior_exterior, self_weight,
                start_load, end_load, dead_load, live_load, lr_load, snow_load,
                str(share_post["left"]), str(share_post["right"]),
                str(sw.pd_left), str(sw.pl_left), str(sw.pe_left),
                str(sw.pd_right), str(sw.pl_right), str(sw.pe_right),
                orientation, v_abv, pe_abv
            ])
        db.conn.commit()

        self.shearWall_dict = {
            "label": label,
            "coordinate": [self.start, self.end],
            "story": StoryName,
            "line_label": line,
            "length": round(self.length, 1),
            "height": height,
            "opening_width": opening_width,
            "interior_exterior": interior_exterior,
            "self_weight": self_weight,
            "direction": orientation,
            "load": {
                "distributed": self.finalDistributedLoad.loadSet,
                "reaction": {
                    "Dead": {"left": sw.pd_left, "right": sw.pd_right},
                    "Live": {"left": sw.pl_left, "right": sw.pl_right},
                    "Seismic": {"left": sw.pe_left, "right": sw.pe_right}
                }
            },
            "share_post": share_post
        }
        self.shearWallProperties_everyTab.append(self.shearWall_dict)

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
            deadCheck = False
            liveCheck = False
            lrCheck = False
            snowCheck = False
            for Load in load:
                if Load["type"] == "Dead":
                    dead.append(Load["magnitude"])
                    deadCheck = True
                elif Load["type"] == "Live":
                    live.append(Load["magnitude"])
                    liveCheck = True
                elif Load["type"] == "Live Roof":
                    lr.append(Load["magnitude"])
                    lrCheck = True
                elif Load["type"] == "snow":
                    snow.append(Load["magnitude"])
                    snowCheck = True

            if not deadCheck:
                dead.append(0)
            if not liveCheck:
                live.append(0)
            if not lrCheck:
                lr.append(0)
            if not snowCheck:
                snow.append(0)

        dead_string = list_to_string(dead)
        live_string = list_to_string(live)
        lr_string = list_to_string(lr)
        snow_string = list_to_string(snow)

        return start_string, endList_string, dead_string, live_string, lr_string, snow_string


# Assuming these functions are defined elsewhere in your code
def list_to_string(lst):
    return ",".join(map(str, lst))
