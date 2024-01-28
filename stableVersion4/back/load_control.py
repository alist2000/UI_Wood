import sys

sys.path.append(r"D:\Learning\Qt\code\practice\UI_Wood\08.1")
from post_new import magnification_factor
from sympy import Point, Polygon, Segment, Line


class load_joist_on_beam:
    def __init__(self, joistLabel, joistLoad, intersection_range_joist_beam, tributary_depth_joist_beam, beamDirection,
                 beamJoistLoad, joistOrientation=None, beamStart=None):
        self.joistLabel = joistLabel
        self.joistLoad = joistLoad
        self.joistOrientation = joistOrientation
        self.beamStart = beamStart
        self.intersection_range_joist_beam = intersection_range_joist_beam
        self.tributary_depth_joist_beam = tributary_depth_joist_beam
        self.beamDirection = beamDirection
        self.beamJoistLoad_assignment = beamJoistLoad["assignment"]
        self.beamJoistLoad_load_map = beamJoistLoad["load_map"]
        # self.beamJoistLoad_assignment.clear()
        # self.beamJoistLoad_load_map.clear()
        try:
            if self.beamDirection == "N-S":
                self.intersection_range_joist_beam = (
                    min(self.intersection_range_joist_beam[0][1], self.intersection_range_joist_beam[1][1]),
                    max(self.intersection_range_joist_beam[0][1], self.intersection_range_joist_beam[1][1]))
        except:
            pass
        try:
            if self.beamDirection == "E-W":
                self.intersection_range_joist_beam = (
                    min(self.intersection_range_joist_beam[0][0], self.intersection_range_joist_beam[1][0]),
                    max(self.intersection_range_joist_beam[0][0], self.intersection_range_joist_beam[1][0]))
        except:
            pass
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
        for load_set in loads:
            load_list = []
            range_x_load = load_set["range_x"]
            range_y_load = load_set["range_y"]

            if self.beamDirection == "N-S":
                print(range_y_load, self.tributary_depth_joist_beam)
                tributary_depth_range = range_intersection(range_x_load, self.tributary_depth_joist_beam)
                intersection_range = range_intersection(range_y_load, self.intersection_range_joist_beam)
            elif self.beamDirection == "E-W":
                print(range_x_load, self.tributary_depth_joist_beam)
                tributary_depth_range = range_intersection(range_y_load, self.tributary_depth_joist_beam)
                intersection_range = range_intersection(range_x_load, self.intersection_range_joist_beam)
            else:  # Inclined
                instance = LoadOnInclinedBeam(self.joistOrientation, range_y_load, range_x_load,
                                              self.tributary_depth_joist_beam, self.intersection_range_joist_beam)
                first_intersection_range, tributary_depth_range = instance.output()

                startIntersection = distance(self.beamStart, first_intersection_range[0])
                secondIntersection = distance(self.beamStart, first_intersection_range[1])
                intersection_range = (startIntersection + self.beamStart[0], secondIntersection + self.beamStart[0])

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


class LoadOnInclinedBeam:
    def __init__(self, joistOrientation, range_y_load, range_x_load, tributaryDepth, intersectionRange):
        self.joistOrientation = joistOrientation
        self.range_y_load = range_y_load
        self.range_x_load = range_x_load
        self.tributaryDepth = tributaryDepth
        self.intersectionRange = intersectionRange
        if joistOrientation == "N-S":
            tributaryDepthLoad = range_y_load
            intersectionLoad = range_x_load
            intersectionBeam = (intersectionRange[0][0], intersectionRange[1][0])
        else:
            tributaryDepthLoad = range_x_load
            intersectionLoad = range_y_load
            intersectionBeam = (intersectionRange[0][1], intersectionRange[1][1])

        self.tributary_depth_range = range_intersection(tributaryDepthLoad, tributaryDepth)
        intersection_range = range_intersection(intersectionBeam, intersectionLoad)
        if joistOrientation == "N-S":
            point1 = self.line(intersection_range[0], "x")
            point2 = self.line(intersection_range[1], "x")
            self.intersection_range_final = ((intersection_range[0], point1), (intersection_range[1], point2))

        else:
            point1 = self.line(intersection_range[0], "y")
            point2 = self.line(intersection_range[1], "y")
            self.intersection_range_final = ((point1, intersection_range[0]), (point2, intersection_range[1]))

    def output(self):
        return self.intersection_range_final, self.tributary_depth_range

    def line(self, var, x_or_y):
        point1, point2 = self.intersectionRange
        if x_or_y == "x":
            m, c = line_equation_y_per_x(point1, point2)
        else:
            m, c = line_equation_x_per_y(point1, point2)
        return m * var + c


def distance(start, end):
    return ((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2) ** 0.5


def line_equation_y_per_x(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    m = (y2 - y1) / (x2 - x1)
    c = y1 - m * x1
    return m, c


def line_equation_x_per_y(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    m = (x2 - x1) / (y2 - y1)
    c = x1 - m * y1
    return m, c


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
    x1_primary, x2_primary = range1
    y1_primary, y2_primary = range2
    x1 = min(x1_primary, x2_primary)
    x2 = max(x1_primary, x2_primary)
    y1 = min(y1_primary, y2_primary)
    y2 = max(y1_primary, y2_primary)
    start = max(x1, y1)
    end = min(x2, y2)
    if x2 >= start and start <= y2 and end >= x1 and y1 <= end and start < end:
        intersection = (start, end)
    else:
        intersection = ()
    return intersection


def length_point(point1, point2):
    try:
        x1 = point1.args[0]
    except:
        x1 = point1[0]
    try:
        y1 = point1.args[1]
    except:
        y1 = point1[1]
    try:
        x2 = point2.args[0]
    except:
        x2 = point2[0]
    try:
        y2 = point2.args[1]
    except:
        y2 = point2[1]

    length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return length
