import sys

sys.path.append(r"D:\Learning\Qt\code\practice\UI_Wood\11.5")
sys.path.append(r"D:\Learning\Qt\code\practice\UI_Wood\9")
from post_new import magnification_factor
from back.load_control import range_intersection


class beam_output:
    def __init__(self, beam):
        self.beam = beam

        # self.beamProperties = {}
        self.beamProperties = []
        # for beamItem, beamProp in beam.items():
        for beamProp in beam:
            beamOutput = beam_output_handler(beamProp)
            self.beamProperties.append(beamOutput.beamProp_dict)
            # self.beamProperties[beamItem] = beamOutput.beamProp_dict


class beam_output_handler:
    def __init__(self, beamProp):
        self.beamProp = beamProp
        self.length = beamProp["length"] / magnification_factor
        self.direction = beamProp["direction"]
        self.support_list = []
        if self.direction == "N-S":
            self.direction_index = 1
        else:
            self.direction_index = 0

        self.start = min(beamProp["coordinate"][0][self.direction_index],
                         beamProp["coordinate"][1][self.direction_index]) / magnification_factor
        self.end = max(beamProp["coordinate"][0][self.direction_index],
                       beamProp["coordinate"][1][self.direction_index]) / magnification_factor

        ControlSupport(beamProp, self.direction_index, self.support_list)
        self.support_list = list(set(self.support_list))
        # if beam have no support, we should ignore it.
        if self.support_list:
            self.pointLoad = ControlPointLoad(beamProp["load"]["point"], beamProp, self.direction_index)
            self.reactionLoad = ControlReactionLoad(beamProp["load"]["reaction"], beamProp, self.direction_index)
            self.finalPointLoad = CombinePointLoads(self.pointLoad.loadSet, self.reactionLoad.loadSet)
            self.distributedLoad = ControlDistributetLoad(beamProp["load"]["joist_load"]["load_map"], self.start)
            self.lineLoad = ControlLineLoad(beamProp["load"]["line"], beamProp, self.direction_index)
            print("loadset line load", self.lineLoad.loadSet)
            self.finalDistributedLoad = CombineDistributes(self.distributedLoad.loadSet, self.lineLoad.loadSet)

            self.beamProp_dict = {
                "label": beamProp["label"],
                "coordinate": [self.start, self.end],
                "length": self.end - self.start,
                "support": self.support_list,
                "load": {
                    "point": self.finalPointLoad.loadSet,
                    "distributed": self.finalDistributedLoad.loadSet
                }
            }
        else:
            self.beamProp_dict = {}


class ControlSupport:
    def __init__(self, beamProp, direction_index, support_list):
        for support in beamProp["support"]:
            loc = support["coordinate"][direction_index] / magnification_factor
            self.start = min(beamProp["coordinate"][0][direction_index],
                             beamProp["coordinate"][1][direction_index]) / magnification_factor
            self.length = beamProp["length"] / magnification_factor
            support_loc = loc - self.start
            support_loc = self.control_point_on_beam(support_loc)
            # THIS PART SHOULD BE DEVELOPED. USER SHOULD BE ABLE TO CHANGE SUPPORT TYPE.
            type_support = (1, 1, 0)  # PINNED
            if len(beamProp["support"]) == 1:
                type_support = (1, 1, 1)
            support_list.append((support_loc, type_support))

    def control_point_on_beam(self, loc):
        if loc > self.length:
            loc = self.length
        elif loc < 0:
            loc = 0
        return loc


class ControlDistributetLoad:
    def __init__(self, load, start):
        self.load = load
        self.all_indexes = []
        self.loadSet = []

        range_list = [(load_item['start'] / magnification_factor, load_item["end"] / magnification_factor) for load_item
                      in load]
        first_list = [i[0] for i in range_list]
        second_list = [i[1] for i in range_list]
        full_start_end = first_list + second_list
        full_start_end_sorted = sorted(set(full_start_end))
        range_final = []
        for i in range(len(full_start_end_sorted) - 1):
            range_final.append((full_start_end_sorted[i], full_start_end_sorted[i + 1]))
        for rangeItem in range_final:
            loadList = []
            for loadItem in load:
                rangeLoad = (loadItem["start"] / magnification_factor, loadItem["end"] / magnification_factor)
                intersection = range_intersection(rangeLoad, rangeItem)
                if intersection:
                    for load_value in loadItem["load"]:
                        loadList.append(load_value)
            if loadList:
                self.loadSet.append({
                    "start": rangeItem[0] - start,
                    "end": rangeItem[1] - start,
                    "load": loadList
                })
        ControlLoadType(self.loadSet)


class ControlLineLoad:
    def __init__(self, load, beamProp, direction_index):
        beamLength = beamProp["length"] / magnification_factor
        self.load = load
        self.all_indexes = []
        self.loadSet = []
        range_list = []
        for load_item in load:

            loadLength = load_item["length"] / magnification_factor
            start_main = min(beamProp["coordinate"][0][direction_index],
                             beamProp["coordinate"][1][direction_index])
            if start_main == beamProp["coordinate"][0][direction_index]:
                distance = load_item["distance"]
            else:
                distance = abs(load_item["distance"] + load_item["length"] - beamProp["length"])
            print("distance = ", distance)
            start = distance / magnification_factor
            end = start + loadLength
            print(end)
            # control input
            if end > beamLength:
                load_item["length"] = (beamLength - start) * magnification_factor
                print(load_item["length"])
            range_list.append((start, start + load_item["length"] / magnification_factor))
        # range_list = [(load_item['distance'] / magnification_factor,
        #                (load_item['distance'] + load_item["length"]) / magnification_factor) for load_item in load]
        print(range_list)
        first_list = [i[0] for i in range_list]
        second_list = [i[1] for i in range_list]
        full_start_end = first_list + second_list
        full_start_end_sorted = sorted(set(full_start_end))
        range_final = []
        for i in range(len(full_start_end_sorted) - 1):
            range_final.append((full_start_end_sorted[i], full_start_end_sorted[i + 1]))
        for rangeItem in range_final:
            loadList = []
            for loadItem in load:
                loadLength = loadItem["length"] / magnification_factor
                start_main = min(beamProp["coordinate"][0][direction_index],
                                 beamProp["coordinate"][1][direction_index])
                if start_main == beamProp["coordinate"][0][direction_index]:
                    distance = loadItem["distance"]
                else:
                    distance = abs(loadItem["distance"] + loadItem["length"] - beamProp["length"])
                start = distance / magnification_factor
                end = start + loadLength

                rangeLoad = (start,
                             end)
                intersection = range_intersection(rangeLoad, rangeItem)
                if intersection:
                    loadList.append({
                        "type": loadItem["type"],
                        "magnitude": loadItem["magnitude"]
                    })
            if loadList:
                self.loadSet.append({
                    "start": rangeItem[0],
                    "end": rangeItem[1],
                    "load": loadList
                })
        ControlLoadType(self.loadSet)


class CombineDistributes:
    def __init__(self, distributeLoad, lineLoad):
        self.distributeLoad = distributeLoad
        self.lineLoad = lineLoad
        self.all_indexes = []
        self.loadSet = []

        full_start_end1 = create_range(distributeLoad)
        full_start_end2 = create_range(lineLoad)
        full_start_end = full_start_end1 + full_start_end2
        full_start_end_sorted = sorted(set(full_start_end))
        range_final = []
        for i in range(len(full_start_end_sorted) - 1):
            range_final.append((full_start_end_sorted[i], full_start_end_sorted[i + 1]))
        for rangeItem in range_final:
            loadList = []
            for loadItem in distributeLoad:
                rangeLoad = (loadItem["start"], loadItem["end"])
                intersection = range_intersection(rangeLoad, rangeItem)
                if intersection:
                    for load in loadItem["load"]:
                        loadList.append(load)
            for loadItem in lineLoad:
                rangeLoad = (loadItem["start"], loadItem["end"])
                intersection = range_intersection(rangeLoad, rangeItem)
                if intersection:
                    for load in loadItem["load"]:
                        loadList.append(load)
            if loadList:
                self.loadSet.append({
                    "start": rangeItem[0],
                    "end": rangeItem[1],
                    "load": loadList
                })
        ControlLoadType(self.loadSet)


class ControlPointLoad:
    def __init__(self, load, beamProp, direction_index):
        self.load = load
        self.all_indexes = []
        self.loadSet = []

        distance_list = [load_item['distance'] for load_item in load]
        checked_indexes = set()  # set for efficient searching

        num_distances = len(distance_list)  # calculating length once and reusing

        for i in range(num_distances):
            if i not in checked_indexes:  # Control check
                current_distance = distance_list[i]
                index_list = [j for j in range(i, num_distances) if distance_list[j] == current_distance]
                checked_indexes.update(index_list)

                self.all_indexes.append(index_list)

        for item in self.all_indexes:
            loads_types = [{'type': load[i]['type'], 'magnitude': load[i]['magnitude']} for i in item]
            start = min(beamProp["coordinate"][0][direction_index],
                        beamProp["coordinate"][1][direction_index])
            if start == beamProp["coordinate"][0][direction_index]:
                distance = load[item[0]]['distance'] / magnification_factor
            else:
                distance = abs(beamProp["length"] - load[item[0]]['distance']) / magnification_factor
            self.loadSet.append({
                "start": distance,
                "load": loads_types
            })

        ControlLoadType(self.loadSet)


class ControlReactionLoad:
    def __init__(self, load, beamProp, direction_index):
        self.load = load
        self.loadSet = []

        for i in range(len(load)):
            start = min(beamProp["coordinate"][0][direction_index],
                        beamProp["coordinate"][1][direction_index])
            distance = abs(start - load[i]['start'][direction_index]) / magnification_factor
            self.loadSet.append({
                "start": distance,
                "load": load[i]['load']
            })


class CombinePointLoads:
    def __init__(self, pointLoad, reactionLoad):
        start1 = [i["start"] for i in pointLoad]
        start2 = [i["start"] for i in reactionLoad]
        start = list(set(start1 + start2))
        self.loadSet = []
        for coordinate in start:
            load1 = self.add_load(pointLoad, coordinate)
            load2 = self.add_load(reactionLoad, coordinate)

            self.loadSet.append({
                "start": coordinate,
                "load": load1 + load2
            })
        ControlLoadType(self.loadSet)

    @staticmethod
    def add_load(load, start):
        for loadItem in load:
            if loadItem["start"] == start:
                return loadItem["load"]
        return []


class ControlLoadType:
    def __init__(self, loadList):
        self.all_indexes2 = []

        for item in loadList:
            self.all_indexes2.clear()
            type_list = [load_item['type'] for load_item in item["load"]]
            magnitude_list = [load_item['magnitude'] for load_item in item["load"]]
            checked_indexes = set()  # set for efficient searching

            num_type = len(type_list)  # calculating length once and reusing

            for i in range(num_type):
                if i not in checked_indexes:  # Control check
                    current_type = type_list[i]
                    index_list = [j for j in range(i, num_type) if type_list[j] == current_type]
                    checked_indexes.update(index_list)

                    self.all_indexes2.append(index_list)

            load_list = []
            for Item in self.all_indexes2:
                load_mag = 0
                for i in Item:
                    load_mag += magnitude_list[i]
                load_list.append({
                    "type": type_list[i],
                    "magnitude": load_mag
                })
            item["load"] = load_list


def create_range(load):
    range_list1 = [(load_item['start'], load_item["end"]) for load_item
                   in load]
    first_list = [i[0] for i in range_list1]
    second_list = [i[1] for i in range_list1]
    full_start_end = first_list + second_list
    return full_start_end
