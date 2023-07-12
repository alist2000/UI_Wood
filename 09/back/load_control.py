import sys

sys.path.append(r"D:\Learning\Qt\code\practice\UI_Wood\08.1")
from post_new import magnification_factor


class load_joist_on_beam:
    def __init__(self, joistLabel, joistLoad, intersection_range_joist_beam, tributary_depth_joist_beam, beamDirection,
                 beamJoistLoad):
        self.joistLabel = joistLabel
        self.joistLoad = joistLoad
        self.intersection_range_joist_beam = intersection_range_joist_beam
        self.tributary_depth_joist_beam = tributary_depth_joist_beam
        self.beamDirection = beamDirection
        self.beamJoistLoad_assignment = beamJoistLoad["assignment"]
        self.beamJoistLoad_load_map = beamJoistLoad["load_map"]
        # self.beamJoistLoad_assignment.clear()
        # self.beamJoistLoad_load_map.clear()
        total_area_load = self.joistLoad["total_area"]
        self.total_area_to_line(total_area_load)
        custom_area_load = self.joistLoad["custom_area"]
        self.custom_area_to_line(custom_area_load)
        load_map = self.joistLoad["load_map"]
        self.load_map_to_line(load_map)

    def total_area_to_line(self, loads):
        for load in loads:
            load_mag = load["magnitude"]
            Type = load["type"]
            tributary_depth = abs(self.tributary_depth_joist_beam[1] - self.tributary_depth_joist_beam[0])

            # convert area load to line load
            magnitude = load_mag * tributary_depth / magnification_factor
            start = min(self.intersection_range_joist_beam[0], self.intersection_range_joist_beam[1])
            end = max(self.intersection_range_joist_beam[0], self.intersection_range_joist_beam[1])
            self.beamJoistLoad_assignment.append(
                {"from": self.joistLabel, "type": Type, "magnitude": magnitude, "start": start, "end": end})

    def custom_area_to_line(self, loads):
        for load in loads:
            load_mag = load["magnitude"]
            Type = load["type"]
            range_x = (load["x1"], load["x2"])
            range_y = (load["y1"], load["y2"])
            if self.beamDirection == "N-S":
                print(range_y, self.tributary_depth_joist_beam)
                tributary_depth_range = range_intersection(range_x, self.tributary_depth_joist_beam)
                intersection_range = range_intersection(range_y, self.intersection_range_joist_beam)
            else:
                print(range_x, self.tributary_depth_joist_beam)
                tributary_depth_range = range_intersection(range_y, self.tributary_depth_joist_beam)
                intersection_range = range_intersection(range_x, self.intersection_range_joist_beam)

            # convert area load to line load
            if intersection_range and tributary_depth_range:
                tributary_depth = abs(tributary_depth_range[1] - tributary_depth_range[0])
                print(load_mag, tributary_depth)
                magnitude = load_mag * tributary_depth / magnification_factor
                start = min(intersection_range[0], intersection_range[1])
                end = max(intersection_range[0], intersection_range[1])
                self.beamJoistLoad_assignment.append(
                    {"from": self.joistLabel, "type": Type, "magnitude": magnitude, "start": start, "end": end})

    def load_map_to_line(self, loads):
        load_list = []
        for load_set in loads:
            range_x_load = load_set["range_x"]
            range_y_load = load_set["range_y"]

            if self.beamDirection == "N-S":
                print(range_y_load, self.tributary_depth_joist_beam)
                tributary_depth_range = range_intersection(range_x_load, self.tributary_depth_joist_beam)
                intersection_range = range_intersection(range_y_load, self.intersection_range_joist_beam)
            else:
                print(range_x_load, self.tributary_depth_joist_beam)
                tributary_depth_range = range_intersection(range_y_load, self.tributary_depth_joist_beam)
                intersection_range = range_intersection(range_x_load, self.intersection_range_joist_beam)
            if intersection_range and tributary_depth_range:
                tributary_depth = abs(tributary_depth_range[1] - tributary_depth_range[0])
                start = min(intersection_range[0], intersection_range[1])
                end = max(intersection_range[0], intersection_range[1])
                for load in load_set["load"]:
                    load_mag = load["magnitude"]
                    load_type = load["type"]
                    magnitude = load_mag * tributary_depth / magnification_factor
                    load_list.append({"type": load_type, "magnitude": magnitude})

                    print(load_mag, tributary_depth)

                self.beamJoistLoad_load_map.append(
                    {"from": self.joistLabel, "label": load_set["label"], "load": load_list, "start": start,
                     "end": end})


class load_on_joist:
    def __init__(self, joist, load):
        self.joist = joist
        self.load = load

        for joistProp in joist.values():
            joistProp["load"]["load_map"].clear()
            self.control_load_on_joist(joistProp)

    def control_load_on_joist(self, joistProp):
        range_y_joist = joistProp["line"]["properties"][0]["range"]
        range_x_joist = joistProp["line"]["properties"][1]["range"]
        print("llllllllloooooooaaaaaaaadddd", self.load)
        for loadProp in self.load.values():
            print("llllllllloooooooaaaaaaaadddd", loadProp)

            range_y_load = loadProp["line"]["properties"][0]["range"]
            range_x_load = loadProp["line"]["properties"][1]["range"]
            intersection_y = range_intersection(range_y_joist, range_y_load)
            intersection_x = range_intersection(range_x_joist, range_x_load)
            if intersection_x and intersection_y:
                joistProp["load"]["load_map"].append({"label": loadProp["label"],
                                                      "load": loadProp["load"],
                                                      "range_x": intersection_x,
                                                      "range_y": intersection_y})


def range_intersection(range1, range2):
    range1 = set(range(int(range1[0]), int(range1[1]) + 1))
    range2 = set(range(int(range2[0]), int(range2[1]) + 1))
    intersection = list(range1 & range2)
    if intersection:
        intersection = (min(intersection), max(intersection))
    return intersection
