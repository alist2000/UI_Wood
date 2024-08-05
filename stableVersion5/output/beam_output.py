from UI_Wood.stableVersion5.post_new import magnification_factor
from UI_Wood.stableVersion5.back.load_control import range_intersection


class beam_output:
    def __init__(self, beam):
        """
        The function initializes a class instance with a beam parameter, and then iterates over the beam properties to
        create a list of beam properties.

        :param beam: The `beam` parameter is a list that contains properties of a beam. Each item in the list represents a
        property of the beam
        """
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
        """
        The function initializes a beam object with properties such as length, direction, support, and loads, based on the
        input beam properties.

        :param beamProp: The `beamProp` parameter is a dictionary that contains properties of a beam. It has the following
        keys:
        """
        self.beamProp = beamProp
        self.length = beamProp["length"] / magnification_factor
        self.direction = beamProp["direction"]
        self.support_list = []
        if self.direction == "N-S":
            self.direction_index = 1
            constant_index = 0
        else:
            self.direction_index = 0
            constant_index = 1

        self.start = min(beamProp["coordinate"][0][self.direction_index],
                         beamProp["coordinate"][1][self.direction_index]) / magnification_factor
        self.end = self.start + self.length
        # self.end = max(beamProp["coordinate"][0][self.direction_index],
        #                beamProp["coordinate"][1][self.direction_index]) / magnification_factor
        constantCoordinate = beamProp["coordinate"][0][constant_index] / magnification_factor
        n1 = len(str(self.start).split(".")[1])
        n2 = len(str(self.end).split(".")[1])
        decimal_number = max(n1, n2)
        length = round(self.end - self.start, max(n1, n2))
        ControlSupport(beamProp, self.direction_index, self.support_list, length, self.end)
        self.support_list = list(set(self.support_list))
        if len(self.support_list) == 1:
            self.support_list[0] = [self.support_list[0][0], (1, 1, 1)]

        # if beam have no support, we should ignore it.
        if self.support_list:
            self.pointLoad = ControlPointLoad(beamProp["load"]["point"], beamProp, self.direction_index)
            self.reactionLoad = ControlReactionLoad(beamProp["load"]["reaction"], beamProp, self.direction_index)
            self.finalPointLoad = CombinePointLoads(self.pointLoad.loadSet, self.reactionLoad.loadSet, length)
            self.distributedLoad = ControlDistributetLoad(beamProp["load"]["joist_load"]["load_map"], self.start,
                                                          length)
            self.lineLoad = ControlLineLoad(beamProp["load"]["line"], beamProp, self.direction_index, length)
            print("loadset line load", self.lineLoad.loadSet)
            self.finalDistributedLoad = CombineDistributes(self.distributedLoad.loadSet, self.lineLoad.loadSet,
                                                           decimal_number)

            self.beamProp_dict = {
                "label": beamProp["label"],
                "coordinate": [self.start, self.end],
                "length": length,
                "support": self.support_list,
                "load": {
                    "point": self.finalPointLoad.loadSet,
                    "distributed": self.finalDistributedLoad.loadSet
                },
                "start": constantCoordinate,
                "direction": self.direction,
                "floor": beamProp["floor"],
                "coordinate_main": beamProp["coordinate"],
                "material": beamProp["material"]
            }
        else:
            self.beamProp_dict = {}


class ControlSupport:
    def __init__(self, beamProp, direction_index, support_list, length, end):
        """
        The function initializes a beam object with properties such as start and end coordinates, length, and support types.

        :param beamProp: The `beamProp` parameter is a dictionary that contains properties of a beam. It likely includes
        information such as the coordinates of the beam's start and end points, as well as information about any supports
        that are attached to the beam
        :param direction_index: The `direction_index` parameter is used to specify the index of the coordinate direction
        that is being considered. It is used to access the appropriate coordinate values from the `beamProp` dictionary
        :param support_list: The `support_list` parameter is a list that stores tuples containing the support location and
        support type for each support in the beam. Each tuple has two elements: the support location (`support_loc`) and the
        support type (`type_support`)
        """
        self.end = end
        self.length = length
        lengthDecimal = len(str(self.length).split(".")[1])
        n2 = len(str(self.end).split(".")[1])
        for support in beamProp["support"]:
            loc = [i / magnification_factor for i in support["coordinate"]]
            one = beamProp["coordinate"][0][direction_index]
            two = beamProp["coordinate"][1][direction_index]
            if one <= two:
                n1 = len(str(one).split(".")[1])
                self.start = [i / magnification_factor for i in beamProp["coordinate"][0]]
            else:
                n1 = len(str(two).split(".")[1])
                self.start = [i / magnification_factor for i in beamProp["coordinate"][1]]
            #
            # self.start = min(beamProp["coordinate"][0][direction_index],
            #                  beamProp["coordinate"][1][direction_index]) / magnification_factor

            # self.length = round(self.end - self.start, max(n1, n2))
            support_loc = round(((loc[1] - self.start[1]) ** 2 + (loc[0] - self.start[0]) ** 2) ** 0.5, lengthDecimal)
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


# The `ControlDistributetLoad` class is used to distribute and control the load based on given ranges and load values.
class ControlDistributetLoad:
    def __init__(self, load, start, length=False):
        """
        The function initializes a class instance and processes a given load to create a load set.

        :param load: The `load` parameter is a list of dictionaries. Each dictionary represents a load item and contains the
        following keys:
        :param start: The "start" parameter is the starting point or reference point for the load. It is used to calculate
        the relative positions of the load items
        """
        # beamLength is for check

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
                if length:
                    self.length = length
                    self.lengthDecimal = len(str(self.length).split(".")[1])
                    startLoad = round(rangeItem[0] - start, self.lengthDecimal)
                    endLoad = round(rangeItem[1] - start, self.lengthDecimal)
                    if endLoad > self.length:
                        endLoad = self.length
                else:
                    startLoad = rangeItem[0] - start
                    endLoad = rangeItem[1] - start
                self.loadSet.append({
                    "start": startLoad,
                    "end": endLoad,
                    "load": loadList
                })
        ControlLoadType(self.loadSet)


class ControlLineLoad:
    def __init__(self, load, beamProp, direction_index, length=False):
        """
        The function initializes a class instance with load, beam properties, and direction index, and then performs various
        calculations and operations on the load and beam properties.

        :param load: The `load` parameter is a list of dictionaries. Each dictionary represents a load and contains the
        following keys:
        :param beamProp: The `beamProp` parameter is a dictionary that contains information about the beam's properties. It
        has the following structure:
        :param direction_index: The `direction_index` parameter is an index that specifies the direction of the beam. It is
        used to access the appropriate coordinate values from the `beamProp` dictionary
        """
        self.start = min(beamProp["coordinate"][0][direction_index],
                         beamProp["coordinate"][1][direction_index]) / magnification_factor
        if length:
            beamLength = length
            self.end = self.start + beamLength
        else:
            self.end = max(beamProp["coordinate"][0][direction_index],
                           beamProp["coordinate"][1][direction_index]) / magnification_factor
            n1 = len(str(self.start).split(".")[1])
            n2 = len(str(self.end).split(".")[1])
            beamLength = round(self.end - self.start, max(n1, n2))
        n1 = len(str(self.start).split(".")[1])
        n2 = len(str(self.end).split(".")[1])
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
                distance = abs(load_item["distance"] + load_item["length"] - beamLength * magnification_factor)
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
                    distance = abs(loadItem["distance"] + loadItem["length"] - beamLength * magnification_factor)
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
                    "start": round(rangeItem[0], max(n1, n2)),
                    "end": round(rangeItem[1], max(n1, n2)),
                    "load": loadList
                })
        ControlLoadType(self.loadSet)


class CombineDistributes:
    def __init__(self, distributeLoad, lineLoad, decimalNumber, length=False):
        """
        The function initializes some variables and creates a load set based on the given distributeLoad and lineLoad
        inputs.

        :param distributeLoad: The `distributeLoad` parameter is a list of dictionaries. Each dictionary represents a load
        with the following keys:
        :param lineLoad: The `lineLoad` parameter is a list of dictionaries. Each dictionary represents a line load and has
        the following keys:
        :param decimalNumber: The parameter `decimalNumber` is used to specify the number of decimal places to round the
        start and end values of the load ranges. It is used in the `round()` function calls in the code snippet
        """
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
                    "start": round(rangeItem[0], decimalNumber),
                    "end": round(rangeItem[1], decimalNumber),
                    "load": loadList
                })
        if length:
            uniform = UniformAllLoad(self.loadSet, length)
            self.loadSet = uniform.loadSet
        ControlLoadType(self.loadSet)


class ControlPointLoad:
    def __init__(self, load, beamProp, direction_index):
        """
        The function initializes a class instance with a load, beam properties, and a direction index, and then performs
        some calculations and creates a load set based on the input data.

        :param load: The `load` parameter is a list of dictionaries. Each dictionary represents a load and contains the
        following keys:
        :param beamProp: The parameter `beamProp` is a dictionary that contains information about the beam. It has the
        following structure:
        :param direction_index: The `direction_index` parameter is an index that specifies the direction in which the beam
        is being analyzed. It is used to access the appropriate coordinate values from the `beamProp` dictionary
        """
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
            # self.end = max(beamProp["coordinate"][0][direction_index],
            #                beamProp["coordinate"][1][direction_index]) / magnification_factor
            # beamLength = self.end - (start / magnification_factor)
            beamLength = (((beamProp["coordinate"][0][0] - beamProp["coordinate"][1][
                0]) / magnification_factor) ** 2 + ((beamProp["coordinate"][0][1] - beamProp["coordinate"][1][
                1]) / magnification_factor) ** 2) ** 0.5
            if start == beamProp["coordinate"][0][direction_index]:
                distance = load[item[0]]['distance'] / magnification_factor
            else:
                distance = abs(beamLength * magnification_factor - load[item[0]]['distance']) / magnification_factor
            self.loadSet.append({
                "start": distance,
                "load": loads_types
            })

        ControlLoadType(self.loadSet)


class ControlReactionLoad:
    def __init__(self, load, beamProp, direction_index):
        """
        The function initializes a class instance with a load, beam properties, and a direction index, and creates a load
        set based on the load and beam properties.

        :param load: The `load` parameter is a list of dictionaries. Each dictionary represents a load and contains two
        key-value pairs:
        :param beamProp: The `beamProp` parameter is a dictionary that contains information about the beam properties. It
        has the following structure:
        :param direction_index: The `direction_index` parameter is an index that specifies the direction in which the load
        is applied. It is used to access the appropriate coordinate values from the `beamProp` dictionary
        """
        self.load = load
        self.loadSet = []

        for i in range(len(load)):
            one = beamProp["coordinate"][0][direction_index]
            two = beamProp["coordinate"][1][direction_index]
            if one <= two:
                start = beamProp["coordinate"][0]
            else:
                start = beamProp["coordinate"][1]
            # start = min(beamProp["coordinate"][0][direction_index],
            #             beamProp["coordinate"][1][direction_index])
            # distance = abs(start - load[i]['start'][direction_index]) / magnification_factor
            distance = abs(((start[0] - load[i]['start'][0]) ** 2 + (
                    start[1] - load[i]['start'][1]) ** 2) ** 0.5) / magnification_factor
            self.loadSet.append({
                "start": distance,
                "load": load[i]['load']
            })


class CombinePointLoads:
    def __init__(self, pointLoad, reactionLoad, length):
        """
        The above function initializes a class instance with point loads and reaction loads, combines them based on their
        start coordinates, and adds them to a load set.

        :param pointLoad: The parameter "pointLoad" is a list of dictionaries. Each dictionary represents a point load and
        has two keys: "start" and "load"
        :param reactionLoad: The parameter "reactionLoad" is a list of dictionaries. Each dictionary represents a reaction
        load and has two key-value pairs: "start" and "load"
        """
        start1 = [i["start"] if i["start"] <= length else length for i in pointLoad]
        start2 = [i["start"] if i["start"] <= length else length for i in reactionLoad]
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
        loads = []
        for loadItem in load:
            if loadItem["start"] == start:
                loads += loadItem["load"]
        return loads


class ControlLoadType:
    def __init__(self, loadList):
        """
        The function takes a list of dictionaries as input, extracts the "type" and "magnitude" values from each dictionary,
        groups the dictionaries based on their "type" value, sums the "magnitude" values for each group, and updates the
        original list of dictionaries with the grouped and summed values.

        :param loadList: The `loadList` parameter is a list of dictionaries. Each dictionary represents an item and contains
        a key "load" which maps to a list of dictionaries. Each dictionary in the "load" list represents a load and contains
        keys "type" and "magnitude" which map to the type and magnitude
        """
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


class UniformAllLoad:
    def __init__(self, loadSet, length):
        self.loadSet = loadSet
        self.length = length
        self.uniform_all_load()

    def uniform_all_load(self):
        """   [{'end': 7.75, 'load': [{'magnitude': 0.516885363028146, 'type': 'Dead'},
        {'magnitude': 0.5743170700312735, 'type': 'Live Roof'},
         {'magnitude': 0.5743170700312735, 'type': 'Dead Super'}], 'start': 0.0}]"""
        loadList = []
        loadTypes = {}
        for load in self.loadSet:
            start = load["start"]
            end = load["end"]
            loadLength = abs(end - start)
            insideLoads = []
            for loadInside in load["load"]:
                newLoad = {"type": loadInside["type"], "magnitude": loadInside["magnitude"] * loadLength / self.length}
                if loadTypes.get(loadInside["type"]):
                    loadTypes[loadInside["type"]].append(loadInside["magnitude"] * loadLength / self.length)
                    insideLoads.append(newLoad)
                else:
                    loadTypes[loadInside["type"]] = []
                    loadTypes[loadInside["type"]].append(loadInside["magnitude"] * loadLength / self.length)
            new_start = 0.0
            new_end = self.length
            loadList.append({
                "start": new_start,
                "end": new_end,
                "load": insideLoads
            })
        new_start = 0.0
        new_end = self.length
        new_load = []
        for typeLoad, magnitude in loadTypes.items():
            new_load.append({"type": typeLoad, "magnitude": sum(magnitude)})

        self.loadSet = [{
            "start": new_start,
            "end": new_end,
            "load": new_load
        }]


def create_range(load):
    range_list1 = [(load_item['start'], load_item["end"]) for load_item
                   in load]
    first_list = [i[0] for i in range_list1]
    second_list = [i[1] for i in range_list1]
    full_start_end = first_list + second_list
    return full_start_end
