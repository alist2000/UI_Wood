import sys

sys.path.append(r"D:\Learning\Qt\code\practice\UI_Wood\10")
sys.path.append(r"D:\Learning\Qt\code\practice\UI_Wood\9")
from post_new import magnification_factor
from back.load_control import range_intersection


class beam_output:
    def __init__(self, beam):
        self.beam = beam
        self.beamProperties = {}
        for beamItem, beamProp in beam.items():
            beamOutput = beam_output_handler(beamProp)
            self.beamProperties[beamItem] = beamOutput.beamProp_dict


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
        self.pointLoad = ControlPointLoad(beamProp["load"]["point"])
        self.distributedLoad = ControlDistributetLoad(beamProp["load"]["joist_load"]["load_map"], self.start)
        self.lineLoad = ControlLineLoad(beamProp["load"]["point"], self.length)
        self.finalDistributedLoad = CombineDistributes(self.distributedLoad.loadSet, self.lineLoad.loadSet)

        self.beamProp_dict = {
            "label": beamProp["label"],
            "coordinate": [self.start, self.end],
            "length": self.length,
            "support": self.support_list,
            "load": {
                "point": self.pointLoad.loadSet,
                "distributed": self.finalDistributedLoad.loadSet
            }
        }


class ControlSupport:
    def __init__(self, beamProp, direction_index, support_list):
        for support in beamProp["support"]:
            loc = support["coordinate"][direction_index] / magnification_factor
            start = beamProp["coordinate"][0][direction_index] / magnification_factor
            # THIS PART SHOULD BE DEVELOPED. USER SHOULD BE ABLE TO CHANGE SUPPORT TYPE.
            type_support = (1, 1, 0)  # PINNED
            if len(beamProp["support"]) == 1:
                type_support = (1, 1, 1)
            support_list.append((loc - start, type_support))


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
    def __init__(self, load, beamLength):
        self.load = load
        self.all_indexes = []
        self.loadSet = []
        for load_item in load:
            start = load_item["distance"] / magnification_factor
            loadLength = load_item["length"] / magnification_factor
            print(start, loadLength)
            end = start + loadLength
            print(end)
            # control input
            if end > beamLength:
                load_item["length"] = (beamLength - start) * magnification_factor
                print(load_item["length"])
        range_list = [(load_item['distance'] / magnification_factor,
                       (load_item['distance'] + load_item["length"]) / magnification_factor) for load_item in load]
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
                rangeLoad = (loadItem["distance"] / magnification_factor,
                             (loadItem['distance'] + loadItem["length"]) / magnification_factor)
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
    def __init__(self, load):
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
            self.loadSet.append({
                "start": load[item[0]]['distance'],
                "load": loads_types
            })

        ControlLoadType(self.loadSet)


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


# lineload = [{'type': 'Dead', 'magnitude': 4.0, 'distance': 160.0, 'length': 222.0},
#             {'type': 'Dead', 'magnitude': 2.0, 'distance': 140.0, 'length': 222.0},
#             {'type': 'Live', 'magnitude': 3.0, 'distance': 130.0, 'length': 5.0}]
#
# b = ControlLineLoad(lineload, 5.55)
# print(b.loadSet)
myBeam = {"beam number one":
              {'label': 'B1', 'coordinate': [(0.0, 0.0), (400.0, 0.0)], 'load': {'point': [], 'line': [],
                                                                                 'joist_load': {'assignment': [],
                                                                                                'load_map': [
                                                                                                    {'from': 'J1',
                                                                                                     'label': 'ROOF',
                                                                                                     'load': [{
                                                                                                         'type': 'Dead',
                                                                                                         'magnitude': 0.2},
                                                                                                         {
                                                                                                             'type': 'Live',
                                                                                                             'magnitude': 0.6}],
                                                                                                     'start': 276,
                                                                                                     'end': 352},
                                                                                                    {'from': 'J4',
                                                                                                     'label': 'ROOF',
                                                                                                     'load': [{
                                                                                                         'type': 'Dead',
                                                                                                         'magnitude': 0.1},
                                                                                                         {
                                                                                                             'type': 'Live',
                                                                                                             'magnitude': 0.3}],
                                                                                                     'start': 45,
                                                                                                     'end': 276}]}},
               'length': 400.0, 'line': {'properties': {'slope': True, 'c': 0.0, 'range': (0.0, 400.0)}},
               'direction': 'E-W',
               'support': [{'label': 'P1', 'type': 'post', 'coordinate': (400.0, 0.0), 'range': 'end'},
                           {'label': 'P2', 'type': 'post', 'coordinate': (0.0, 0.0), 'range': 'start'}],
               'joist': [{'label': 'J1', 'intersection_range': (276, 400), 'tributary_depth': (0.0, 80.0)},
                         {'label': 'J4', 'intersection_range': (0, 276), 'tributary_depth': (0.0, 40.0)}]}
          }

myBeam = {"b": {'label': 'B1', 'coordinate': [(0.0, 0.0), (400.0, 0.0)], 'load': {'point': [], 'line': [],
                                                                                  'joist_load': {'assignment': [],
                                                                                                 'load_map': [
                                                                                                     {'from': 'J1',
                                                                                                      'label': 't',
                                                                                                      'load': [{
                                                                                                          'type': 'Dead',
                                                                                                          'magnitude': 0.24500000000000002},
                                                                                                          {
                                                                                                              'type': 'Live',
                                                                                                              'magnitude': 0.49000000000000005}],
                                                                                                      'start': 268,
                                                                                                      'end': 315},
                                                                                                     {'from': 'J2',
                                                                                                      'label': 't',
                                                                                                      'load': [{
                                                                                                          'type': 'Dead',
                                                                                                          'magnitude': 0.1},
                                                                                                          {
                                                                                                              'type': 'Live',
                                                                                                              'magnitude': 0.2}],
                                                                                                      'start': 33,
                                                                                                      'end': 268}]}},
                'length': 400.0, 'line': {'properties': {'slope': True, 'c': 0.0, 'range': (0.0, 400.0)}},
                'direction': 'E-W',
                'support': [{'label': 'P1', 'type': 'post', 'coordinate': (0.0, 0.0), 'range': 'start'},
                            {'label': 'P2', 'type': 'post', 'coordinate': (400.0, 0.0), 'range': 'end'}],
                'joist': [{'label': 'J1', 'intersection_range': (268, 400), 'tributary_depth': (0.0, 98.5)},
                          {'label': 'J2', 'intersection_range': (0, 268), 'tributary_depth': (0.0, 40.0)}]}
          }

myBeam = {"b": {'label': 'B1', 'coordinate': [(0.0, 0.0), (400.0, 0.0)], 'load': {'point': [], 'line': [],
                                                                                  'joist_load': {'assignment': [],
                                                                                                 'load_map': [
                                                                                                     {'from': 'J2',
                                                                                                      'label': 'roof',
                                                                                                      'load': [{
                                                                                                                   'type': 'Dead',
                                                                                                                   'magnitude': 0.19},
                                                                                                               {
                                                                                                                   'type': 'Live',
                                                                                                                   'magnitude': 0.38},
                                                                                                               {
                                                                                                                   'type': 'Dead',
                                                                                                                   'magnitude': 0.38},
                                                                                                               {
                                                                                                                   'type': 'Live',
                                                                                                                   'magnitude': 0.5700000000000001},
                                                                                                               {
                                                                                                                   'type': 'Dead Super',
                                                                                                                   'magnitude': 0.95}],
                                                                                                      'start': 258,
                                                                                                      'end': 400},
                                                                                                     {'from': 'J2',
                                                                                                      'label': 'roof ',
                                                                                                      'load': [{
                                                                                                                   'type': 'Dead',
                                                                                                                   'magnitude': 0.19},
                                                                                                               {
                                                                                                                   'type': 'Live',
                                                                                                                   'magnitude': 0.38},
                                                                                                               {
                                                                                                                   'type': 'Dead',
                                                                                                                   'magnitude': 0.38},
                                                                                                               {
                                                                                                                   'type': 'Live',
                                                                                                                   'magnitude': 0.5700000000000001},
                                                                                                               {
                                                                                                                   'type': 'Dead Super',
                                                                                                                   'magnitude': 0.95}],
                                                                                                      'start': 258,
                                                                                                      'end': 310},
                                                                                                     {'from': 'J3',
                                                                                                      'label': 'roof',
                                                                                                      'load': [{
                                                                                                                   'type': 'Dead',
                                                                                                                   'magnitude': 0.1},
                                                                                                               {
                                                                                                                   'type': 'Live',
                                                                                                                   'magnitude': 0.2},
                                                                                                               {
                                                                                                                   'type': 'Dead',
                                                                                                                   'magnitude': 0.2},
                                                                                                               {
                                                                                                                   'type': 'Live',
                                                                                                                   'magnitude': 0.3},
                                                                                                               {
                                                                                                                   'type': 'Dead Super',
                                                                                                                   'magnitude': 0.5},
                                                                                                               {
                                                                                                                   'type': 'Dead',
                                                                                                                   'magnitude': 0.1},
                                                                                                               {
                                                                                                                   'type': 'Live',
                                                                                                                   'magnitude': 0.2}],
                                                                                                      'start': 218,
                                                                                                      'end': 258},
                                                                                                     {'from': 'J3',
                                                                                                      'label': 'roof ',
                                                                                                      'load': [{
                                                                                                                   'type': 'Dead',
                                                                                                                   'magnitude': 0.1},
                                                                                                               {
                                                                                                                   'type': 'Live',
                                                                                                                   'magnitude': 0.2},
                                                                                                               {
                                                                                                                   'type': 'Dead',
                                                                                                                   'magnitude': 0.2},
                                                                                                               {
                                                                                                                   'type': 'Live',
                                                                                                                   'magnitude': 0.3},
                                                                                                               {
                                                                                                                   'type': 'Dead Super',
                                                                                                                   'magnitude': 0.5},
                                                                                                               {
                                                                                                                   'type': 'Dead',
                                                                                                                   'magnitude': 0.1},
                                                                                                               {
                                                                                                                   'type': 'Live',
                                                                                                                   'magnitude': 0.2}],
                                                                                                      'start': 70,
                                                                                                      'end': 258},
                                                                                                     {'from': 'J3',
                                                                                                      'label': 'roof',
                                                                                                      'load': [{
                                                                                                                   'type': 'Dead',
                                                                                                                   'magnitude': 0.1},
                                                                                                               {
                                                                                                                   'type': 'Live',
                                                                                                                   'magnitude': 0.2},
                                                                                                               {
                                                                                                                   'type': 'Dead',
                                                                                                                   'magnitude': 0.2},
                                                                                                               {
                                                                                                                   'type': 'Live',
                                                                                                                   'magnitude': 0.3},
                                                                                                               {
                                                                                                                   'type': 'Dead Super',
                                                                                                                   'magnitude': 0.5},
                                                                                                               {
                                                                                                                   'type': 'Dead',
                                                                                                                   'magnitude': 0.1},
                                                                                                               {
                                                                                                                   'type': 'Live',
                                                                                                                   'magnitude': 0.2}],
                                                                                                      'start': 0,
                                                                                                      'end': 45}]}},
                'length': 400.0, 'line': {'properties': {'slope': True, 'c': 0.0, 'range': (0.0, 400.0)}},
                'direction': 'E-W',
                'support': [{'label': 'P1', 'type': 'post', 'coordinate': (0.0, 0.0), 'range': 'start'},
                            {'label': 'P2', 'type': 'post', 'coordinate': (400.0, 0.0), 'range': 'end'}],
                'joist': [{'label': 'J2', 'intersection_range': (258, 400), 'tributary_depth': (0.0, 76.5)},
                          {'label': 'J3', 'intersection_range': (0, 258), 'tributary_depth': (0.0, 40.0)}]}
          }

a = beam_output(myBeam)
print(a.beamProperties)
