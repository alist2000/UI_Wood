from UI_Wood.stableVersion2.post_new import magnification_factor
from UI_Wood.stableVersion2.back.load_control import range_intersection
from UI_Wood.stableVersion2.output.beam_output import ControlDistributetLoad
from UI_Wood.stableVersion2.output.joistSql import joistSQL, WriteJoistInputSQL


class Joist_output:
    def __init__(self, joists):
        mainJoist = FindJoistInArea(joists)
        self.Joists = mainJoist.allJoists
        pass


class FindJoistInArea:
    def __init__(self, joists):
        self.allJoists = []
        joistAreaId = 1
        joistDB = joistSQL()
        for story, joistTab in enumerate(joists):
            tabJoists = []
            for joist in joistTab:
                direction = joist["direction"]
                if direction == "N-S":
                    self.direction_index = 1
                    self.constant_index = 0
                    self.line_index = 0
                else:
                    self.direction_index = 0
                    self.constant_index = 1
                    self.line_index = 1
                self.start = None
                self.end = None
                floor = joist["floor"]
                length = self.length(joist)
                self.support = [(0, (1, 1, 0), (length, (1, 1, 0)))]
                self.loadSets = self.joist_seperator(joist)
                self.finalLoadSet = []
                for load in self.loadSets:
                    item = ControlDistributetLoad(load, self.start)
                    self.finalLoadSet.append(item.loadSet)

                # distributed = ControlDistributetLoad(self.loadSets, self.start)
                # self.loadSets = distributed.loadSet

                joistProp = {
                    "label": joist["label"],
                    "story": story + 1,
                    "coordinate": joist["coordinate"],
                    "direction": joist["direction"],
                    "length": length,
                    "joist_item": []
                }

                joistId = 1
                WriteJoistInputSQLInstance = WriteJoistInputSQL(joistProp, joistAreaId, joistDB)

                for load in self.finalLoadSet:
                    joistItem = {"length": length, "support": self.support, "load": load, "floor": floor}
                    joistProp["joist_item"].append(joistItem)
                    WriteJoistInputSQLInstance.distLoadTable(joistId, joistItem)
                    joistId += 1
                tabJoists.append(joistProp)
                joistAreaId += 1
            self.allJoists.append(tabJoists)

    def length(self, joist):
        lengthRange = joist["line"]["properties"][self.line_index]["range"]
        self.start = min(lengthRange[0], lengthRange[1]) / magnification_factor
        self.end = max(lengthRange[0], lengthRange[1]) / magnification_factor
        n1 = len(str(self.start).split(".")[1])
        n2 = len(str(self.end).split(".")[1])
        decimal_number = max(n1, n2)
        length = round(abs(self.start - self.end), decimal_number)
        return length

    def joist_seperator(self, joist):
        if self.constant_index:  # 1
            load_range = "range_y"
            intersection_range = "range_x"
        else:
            load_range = "range_x"
            intersection_range = "range_y"

        loadRanges = []
        loadIntersectionRanges = []
        loadProps = []
        for load in joist["load"]["load_map"]:
            loadRanges.append(load[load_range])
            loadIntersectionRanges.append(load[intersection_range])
            loadProps.append(load["load"])
        starts = [i[0] for i in loadRanges]
        ends = [i[1] for i in loadRanges]
        start_end = sorted(list(set(starts + ends)))
        first_load_ranges = [(start_end[i], start_end[i + 1]) for i in range(len(start_end[:-1]))]
        loadSets = self.control_load_range(first_load_ranges, loadRanges, loadIntersectionRanges,
                                           loadProps,
                                           self.start)
        return loadSets

    @staticmethod
    def control_load_range(loadRanges, mainRanges, loadIntersectionRanges,
                           loadProps, start):
        loadSetMain = []
        finalLoadRanges = []
        for Range in loadRanges:
            loadSet = []
            for i, itemRange in enumerate(mainRanges):
                intersection = range_intersection(Range, itemRange)
                if intersection:
                    if Range not in finalLoadRanges:
                        finalLoadRanges.append(Range)

                    loadSet.append({
                        "start": loadIntersectionRanges[i][0],
                        "end": loadIntersectionRanges[i][1],
                        "load": loadProps[i]
                    })
            if loadSet:
                loadSetMain.append(loadSet)
        return loadSetMain
