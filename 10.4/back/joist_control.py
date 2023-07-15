from back.beam_control import tributary, range_intersection


class joist_line_creator:
    def __init__(self, joist):
        self.joistProp = joist

        self.lines()

    def lines(self):
        self.joistProp["line"] = {}
        self.joistProp["line"]["point"] = []
        joints = self.joistProp["coordinate"]
        (line1, line_prop1), (line2, line_prop2), (line3, line_prop3), (line4, line_prop4) = self.find_line_points(
            joints)
        self.joistProp["line"]["point"].append(line1)
        self.joistProp["line"]["point"].append(line2)
        self.joistProp["line"]["point"].append(line3)
        self.joistProp["line"]["point"].append(line4)

        self.joistProp["line"]["properties"] = []
        self.joistProp["line"]["properties"].append(
            {"slope": line_prop1[0], "c": line_prop1[1], "range": line_prop1[2]})
        self.joistProp["line"]["properties"].append(
            {"slope": line_prop2[0], "c": line_prop2[1], "range": line_prop2[2]})
        self.joistProp["line"]["properties"].append(
            {"slope": line_prop3[0], "c": line_prop3[1], "range": line_prop3[2]})
        self.joistProp["line"]["properties"].append(
            {"slope": line_prop4[0], "c": line_prop4[1], "range": line_prop4[2]})

    def find_line_points(self, points):
        """
        points: [(x1, y1), (x1, y2), (x2, y2), (x2, y1)]
        """
        line1 = (points[0], points[1])
        line_prop1 = self.create_line(points[0], points[1])
        line2 = (points[1], points[2])
        line_prop2 = self.create_line(points[1], points[2])
        line3 = (points[2], points[3])
        line_prop3 = self.create_line(points[2], points[3])
        line4 = (points[3], points[0])
        line_prop4 = self.create_line(points[3], points[0])
        return (line1, line_prop1), (line2, line_prop2), (line3, line_prop3), (line4, line_prop4)

    @staticmethod
    def create_line(point1, point2):
        # point1 and point2 are tuples representing (x, y)
        (x1, y1) = point1
        (x2, y2) = point2
        if x2 - x1 == 0:
            # vertical line
            slope = False
            c = x1
            line_range = (min(y1, y2), max(y1, y2))
        else:
            if y2 - y1 == 0:
                slope = True  # slope = 0
                c = y1
            else:
                slope = (y2 - y1) / (x2 - x1)
                c = y1 - x1 * slope
            line_range = (min(x1, x2), max(x1, x2))

        return slope, c, line_range


class joist_support_control:
    def __init__(self, joist, beam, shearWall, studWall):
        self.joist = joist
        self.beam = beam
        self.shearWall = shearWall
        self.studWall = studWall
        for joistProp in self.joist.values():
            joistProp["support"] = []
        self.control_intersection(self.beam, "beam")
        self.control_intersection(self.shearWall, "shearWall")
        self.control_intersection(self.studWall, "studWall")

    def control_intersection(self, item, type_name):
        for itemProp in item.values():
            slope_beam = itemProp["line"]["properties"]["slope"]
            c_beam = itemProp["line"]["properties"]["c"]
            range_beam = itemProp["line"]["properties"]["range"]
            for joistProp in self.joist.values():
                lines = joistProp["line"]["properties"]
                for i in range(len(lines)):
                    slope_joist = lines[i]["slope"]
                    c_joist = lines[i]["c"]
                    range_joist_line = lines[i]["range"]
                    if slope_joist == slope_beam and c_joist == c_beam:
                        intersection_range = range_intersection(range_joist_line, range_beam)
                        if intersection_range:
                            joistProp["support"].append(
                                {"label": itemProp["label"], "type": type_name,
                                 "intersection_range": intersection_range})
