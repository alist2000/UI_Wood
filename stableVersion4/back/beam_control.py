from UI_Wood.stableVersion4.post_new import magnification_factor
from UI_Wood.stableVersion4.back.load_control import load_joist_on_beam, range_intersection
from sympy import Point, Polygon, Segment, Line
from UI_Wood.stableVersion4.back.load_control import length_point


class beam_control_length:
    def __init__(self, beam):
        self.beam = beam
        self.add_length()

    def add_length(self):
        for beamItem, beamProp in self.beam.items():
            start = beamProp["coordinate"][0]
            end = beamProp["coordinate"][1]
            l = self.length(start, end)
            self.beam[beamItem]["length"] = l

    @staticmethod
    def length(start, end):
        x1 = start[0]
        x2 = end[0]
        y1 = start[1]
        y2 = end[1]
        l = (((y2 - y1) ** 2) + ((x2 - x1) ** 2)) ** 0.5
        return round(l, 2)


class beam_control_direction_and_line:
    def __init__(self, beam):
        self.beam = beam
        self.add_direction()

    def add_direction(self):
        for beamItem, beamProp in self.beam.items():
            beam_line_creator(beamProp)
            start = beamProp["coordinate"][0]
            end = beamProp["coordinate"][1]
            x1, y1 = start[0], start[1]
            x2, y2 = end[0], end[1]
            width = x2 - x1
            height = y2 - y1
            if x1 == x2 or y1 == y2:
                if abs(width) > abs(height):
                    direction = "E-W"
                else:
                    direction = "N-S"
            else:
                direction = "Inclined"

            self.beam[beamItem]["direction"] = direction


class beam_control_support:
    def __init__(self, beam, post, shearWall):
        self.beam = beam
        self.post = post
        self.shearWall = shearWall

        self.add_post_support()
        self.add_shearWall_post_support()
        self.add_beam_support()
        self.edit_support()

    def add_post_support(self):
        for beamItem, beamProp in self.beam.items():
            start = beamProp["coordinate"][0]
            end = beamProp["coordinate"][1]
            beamProp["support"] = []
            # Control post support
            for postItem, postProp in self.post.items():
                is_support, post_range, coord = self.main_is_point_on_line(postProp["coordinate"], start, end, lineType=beamProp["direction"])
                if is_support:
                    beamProp["support"].append(
                        {"label": postProp["label"], "type": "post", "coordinate": coord,
                         "range": post_range})

    def add_shearWall_post_support(self):
        for beamItem, beamProp in self.beam.items():
            start = beamProp["coordinate"][0]
            end = beamProp["coordinate"][1]
            # Control post support
            # Control ShearWall post support
            for shearWallItem, shearWallProp in self.shearWall.items():
                # note: start and end of shear wall also consider as post coordinate
                is_support1, post_range1, coord1 = self.main_is_point_on_line(shearWallProp["post"]["start_center"],
                                                                              start, end,
                                                                              lineType=shearWallProp["direction"])
                is_support2, post_range2, coord2 = self.main_is_point_on_line(shearWallProp["coordinate"][0], start,
                                                                              end, lineType=shearWallProp["direction"])
                if is_support1 or is_support2:
                    if is_support1:
                        post_range = post_range1
                        # coordinate = shearWallProp["post"]["start_center"]
                        coordinate = coord1
                    else:
                        post_range = post_range2
                        coordinate = coord2
                        # coordinate = shearWallProp["coordinate"][0]
                    coords = [i["coordinate"] for i in beamProp["support"]]
                    if coordinate not in coords:
                        beamProp["support"].append(
                            {"label": shearWallProp["post"]["label_start"], "type": "shearWall_post",
                             "coordinate": coordinate,
                             "range": post_range})
                is_support1, post_range1, coord1 = self.main_is_point_on_line(shearWallProp["post"]["end_center"],
                                                                              start, end,
                                                                              lineType=shearWallProp["direction"])
                is_support2, post_range2, coord2 = self.main_is_point_on_line(shearWallProp["coordinate"][1], start,
                                                                              end, lineType=shearWallProp["direction"])

                if is_support1 or is_support2:
                    if is_support1:
                        post_range = post_range1
                        # coordinate = shearWallProp["post"]["end_center"]
                        coordinate = coord1

                    else:
                        post_range = post_range2
                        # coordinate = shearWallProp["coordinate"][1]
                        coordinate = coord2
                    coords = [i["coordinate"] for i in beamProp["support"]]
                    if coordinate not in coords:
                        beamProp["support"].append(
                            {"label": shearWallProp["post"]["label_end"], "type": "shearWall_post",
                             "coordinate": coordinate,
                             "range": post_range})

    def add_beam_support(self):
        for beamItem, beamProp in self.beam.items():
            start = beamProp["coordinate"][0]
            end = beamProp["coordinate"][1]
            label_number = float(beamProp["label"][1:])
            for beamItem2, beamProp2 in self.beam.items():
                if beamItem2 is not beamItem:
                    start2 = beamProp2["coordinate"][0]
                    end2 = beamProp2["coordinate"][1]
                    label_number2 = float(beamProp2["label"][1:])

                    # CONTROL START BEAM SUPPORT (BEAM TO BEAM)
                    is_support, post_range, coord = self.main_is_point_on_line(start, start2, end2,
                                                                               magnification_factor / 10,
                                                                               beamProp2["direction"])
                    if is_support:
                        if post_range == "mid":
                            Type = "beam_mid_support"
                            add = True
                        else:
                            if post_range == "start":
                                Type = "beam_start_support"
                            else:
                                Type = "beam_end_support"
                            if label_number > label_number2:
                                add = True
                            else:
                                add = False
                        coords = [i["coordinate"] for i in beamProp["support"]]

                        if add and coord not in coords:
                            if post_range == "mid":
                                if label_number > label_number2:
                                    beamProp["support"].append(
                                        {"label": beamProp2["label"], "type": Type,
                                         "coordinate": coord,
                                         "range": "start"})
                                else:
                                    beamProp2["support"].append(
                                        {"label": beamProp["label"], "type": Type,
                                         "coordinate": coord,
                                         "range": "mid"})
                            else:
                                beamProp["support"].append(
                                    {"label": beamProp2["label"], "type": Type,
                                     "coordinate": coord,
                                     "range": "start"})

                    # CONTROL END BEAM SUPPORT (BEAM TO BEAM)
                    is_support, post_range, coord = self.main_is_point_on_line(end, start2, end2,
                                                                               magnification_factor / 10,
                                                                               beamProp2["direction"])
                    if is_support:
                        if post_range == "mid":
                            Type = "beam_mid_support"
                            add = True
                        else:
                            if post_range == "start":
                                Type = "beam_start_support"
                            else:
                                Type = "beam_end_support"
                            if label_number > label_number2:
                                add = True
                            else:
                                add = False
                        coords = [i["coordinate"] for i in beamProp["support"]]
                        if add and coord not in coords:
                            if post_range == "mid":
                                if label_number > label_number2:
                                    beamProp["support"].append(
                                        {"label": beamProp2["label"], "type": Type,
                                         "coordinate": coord,
                                         "range": "end"})
                                else:
                                    beamProp2["support"].append(
                                        {"label": beamProp["label"], "type": Type,
                                         "coordinate": coord,
                                         "range": "mid"})
                            else:
                                beamProp["support"].append(
                                    {"label": beamProp2["label"], "type": Type,
                                     "coordinate": coord,
                                     "range": "end"})

    def edit_support(self):
        for beamProp in self.beam.values():
            post_supports = []
            beam_supports = []
            extra_support_index = []
            supports = beamProp["support"]
            for support in supports:
                if support["type"] == "post":
                    post_supports.append(support)
                else:
                    beam_supports.append(support)
            for i in range(len(beam_supports)):
                for post_support in post_supports:
                    post_cor = post_support["coordinate"]
                    if beam_supports[i]["coordinate"] == post_cor:
                        extra_support_index.append(i)
            for j in extra_support_index:
                try:
                    del beam_supports[j]
                except:
                    pass
            final_support = post_supports + beam_supports
            beamProp["support"] = final_support

    @staticmethod
    def is_point_on_line(point, line_point1, line_point2, error=magnification_factor / 5):
        (x0, y0) = point
        (x1, y1) = line_point1
        (x2, y2) = line_point2
        range_x = (min(x1, x2), max(x1, x2))
        range_y = (min(y1, y2), max(y1, y2))
        p1, p2 = Point(x1, y1), Point(x2, y2)

        # Define a line through the two points
        line = Line(p1, p2)
        distance = float(line.distance(point))
        # Define a tolerance value
        tolerance = error
        xRangeCondition = range_x[0] <= x0 <= range_x[1]
        if range_x[1] - range_x[0] < tolerance:
            xRangeCondition = True

        yRangeCondition = range_y[0] <= y0 <= range_y[1]
        if range_y[1] - range_y[0] < tolerance:
            yRangeCondition = True

        if distance <= tolerance and xRangeCondition and yRangeCondition:
            projection = line.projection(point)
            x_1, y_1 = float(projection.args[0]), float(projection.args[1])
            return True, (x_1, y_1)
        else:
            return False, ("", "")
        # # Calculate the slopes
        # if x2 - x1 == 0:  # To avoid division by zero
        #     different = abs(x0 - x1)
        #     return different < error and min(y1, y2) <= y0 <= max(y1, y2), (x1, y0)
        # if x0 - x1 == 0:
        #     different = abs(y0 - y1)
        #     return different < error and min(x1, x2) <= x0 <= max(x1, x2), (x0, y1)
        # slope1 = (y2 - y1) / (x2 - x1)
        # slope2 = (y0 - y1) / (x0 - x1)
        # different = abs(y0 - y1)
        #
        # return different < error and min(x1, x2) <= x0 <= max(x1, x2), (x0, y1)

    @staticmethod
    def is_point_on_line_straight(point, line_point1, line_point2, error=magnification_factor / 5):
        (x0, y0) = point
        (x1, y1) = line_point1
        (x2, y2) = line_point2

        # Calculate the slopes
        if x2 - x1 == 0:  # To avoid division by zero
            different = abs(x0 - x1)
            return different < error and min(y1, y2) <= y0 <= max(y1, y2), (x1, y0)
        if x0 - x1 == 0:
            different = abs(y0 - y1)
            return different < error and min(x1, x2) <= x0 <= max(x1, x2), (x0, y1)
        slope1 = (y2 - y1) / (x2 - x1)
        slope2 = (y0 - y1) / (x0 - x1)
        different = abs(y0 - y1)

        return different < error and min(x1, x2) <= x0 <= max(x1, x2), (x0, y1)

    def main_is_point_on_line(self, point, start, end, error=magnification_factor / 5, lineType="N-S"):
        if lineType == "N-S" or lineType == "E-W":
            is_support, coord = self.is_point_on_line_straight(point, start, end, error)
        else:
            is_support, coord = self.is_point_on_line(point, start, end, error)
        post_range = None
        if is_support:
            if point == start:
                post_range = "start"
            elif point == end:
                post_range = "end"
            else:
                post_range = "mid"
        return is_support, post_range, coord


class beam_line_creator:
    def __init__(self, beam):
        self.beamProp = beam

        self.lines()

    def lines(self):
        self.beamProp["line"] = {}
        joints = self.beamProp["coordinate"]
        line_prop = self.find_line_points(
            joints)
        self.beamProp["line"]["properties"] = {"slope": line_prop[0], "c": line_prop[1], "range": line_prop[2]}

    def find_line_points(self, points):
        """
        points: [(x1, y1), (x1, y2)]
        """
        line1 = (points[0], points[1])
        line_prop1 = self.create_line(points[0], points[1])
        return line_prop1

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


class beam_control_joist:
    def __init__(self, beam, joist):
        self.beam = beam
        self.joist = joist
        for beamProp in self.beam.values():
            if beamProp["direction"] == "Inclined":
                self.control_intersection(beamProp)
            else:
                self.control_intersection_straight(beamProp)

    def control_intersection_straight(self, beamProp):
        beamProp["joist"] = []
        beamProp["load"]["joist_load"] = {"assignment": [], "load_map": []}
        slope_beam = beamProp["line"]["properties"]["slope"]
        c_beam = beamProp["line"]["properties"]["c"]
        range_beam = beamProp["line"]["properties"]["range"]
        for joistProp in self.joist.values():
            lines = joistProp["line"]["properties"]
            for i in range(len(lines)):
                slope_joist = lines[i]["slope"]
                c_joist = lines[i]["c"]
                range_joist_line = lines[i]["range"]
                startPointTolerate = abs(c_joist - c_beam)
                if startPointTolerate < 15:
                    startStatus = True
                else:
                    startStatus = False
                if slope_joist == slope_beam and startStatus:
                    intersection_range = range_intersection(range_joist_line, range_beam)
                    if intersection_range:
                        # for tributary calculation
                        try:
                            range_other_direction = lines[i + 1]["range"]
                        except:
                            range_other_direction = lines[i - 1]["range"]

                        tributary_depth = tributary(joistProp["direction"], beamProp["direction"],
                                                    range_other_direction, beamProp["line"]["properties"]["c"])

                        beamProp["joist"].append(
                            {"label": joistProp["label"], "intersection_range": intersection_range,
                             "tributary_depth": tributary_depth})

                        load_joist_on_beam(joistProp["label"], joistProp["load"], intersection_range,
                                           tributary_depth, beamProp["direction"], beamProp["load"]["joist_load"])

    def control_intersection(self, beamProp):
        beamProp["joist"] = []
        beamProp["load"]["joist_load"] = {"assignment": [], "load_map": []}
        beamPoint1 = Point(beamProp["coordinate"][0][0], (beamProp["coordinate"][0][1]))
        beamPoint2 = Point(beamProp["coordinate"][1][0], beamProp["coordinate"][1][1])
        beamSegment = Segment(beamPoint1, beamPoint2)
        slope_beam = beamProp["line"]["properties"]["slope"]
        c_beam = beamProp["line"]["properties"]["c"]
        range_beam = beamProp["line"]["properties"]["range"]
        for joistProp in self.joist.values():
            joistCoords = joistProp["coordinate"]
            joistArea = Polygon(*joistCoords)
            intersection = joistArea.intersection(beamSegment)
            # line_in_polygon = len(intersection) == 1 and intersection[0] == beamSegment
            intersection_range = []
            if len(intersection) == 1 and intersection[0] == beamSegment:
                intersection_range = [[float(i) for i in intersection[0].args[0].args],
                                      [float(i) for i in intersection[0].args[1].args]]

            elif len(intersection) == 2:
                intersection_range = [[float(i) for i in intersection[0].args],
                                      [float(i) for i in intersection[1].args]]

            elif len(intersection) == 1:
                point1_in_joist = joistArea.encloses_point(beamPoint1)
                point2_in_joist = joistArea.encloses_point(beamPoint2)

                if point1_in_joist:
                    l = length_point(intersection[0], beamPoint1)
                    if l > 0:
                        intersection_range = [[float(i) for i in intersection[0].args],
                                              [float(i) for i in beamProp["coordinate"][0]]]
                elif point2_in_joist:
                    l = length_point(intersection[0], beamPoint2)
                    if l > 0:
                        intersection_range = [[float(i) for i in intersection[0].args],
                                              [float(i) for i in beamProp["coordinate"][1]]]


            else:
                point1_in_joist = joistArea.encloses_point(beamPoint1)
                point2_in_joist = joistArea.encloses_point(beamPoint2)
                print("jaflskdjfljsd")
                if point1_in_joist and point2_in_joist:
                    print("what the fuck")
                    intersection_range = (
                        [float(i) for i in beamProp["coordinate"][0]],
                        [float(i) for i in beamProp["coordinate"][1]])

            if intersection_range:
                if joistProp["direction"] == "N-S":
                    c = (intersection_range[0][1] + intersection_range[1][1]) / 2
                    joistRange1 = abs(c - joistProp["coordinate"][0][1])
                    joistRange2 = abs(c - joistProp["coordinate"][2][1])
                    if joistRange1 > joistRange2:
                        joistRange = (joistProp["coordinate"][0][1], c)
                    else:
                        joistRange = (c, joistProp["coordinate"][2][1])
                else:
                    c = (intersection_range[0][0] + intersection_range[1][0]) / 2
                    joistRange1 = abs(c - joistProp["coordinate"][0][0])
                    joistRange2 = abs(c - joistProp["coordinate"][2][0])
                    if joistRange1 > joistRange2:
                        joistRange = (joistProp["coordinate"][0][0], c)
                    else:
                        joistRange = (c, joistProp["coordinate"][2][0])

                tributary_depth = tributary(joistProp["direction"], beamProp["direction"], joistRange, c)
                # if joistProp["direction"] == "N-S":
                #     tributary_index = 1
                # else:
                #     tributary_index = 0
                # if beamProp["direction"] == "N-S":
                #     tributary_index = 0
                # elif beamProp["direction"] == "E-W":
                #     tributary_index = 1
                # else:
                #     tributary_index = tributary_index
                #
                # joistStart = joistProp["coordinate"][0][tributary_index]
                # joistEnd = joistProp["coordinate"][2][tributary_index]
                # midBeam = (beamProp["coordinate"][0][tributary_index] + beamProp["coordinate"][1][
                #     tributary_index]) / 2
                # tributary1 = joistStart - midBeam
                # tributary2 = joistEnd - midBeam
                # if beamProp["direction"] == "Inclined":
                #     if abs(tributary2) > abs(tributary1):
                #
                #         tributary_depth_number = tributary2
                #     else:
                #         tributary_depth_number = tributary1
                #
                #     range_other_direction = (
                #         min(tributary_depth_number, midBeam), max(tributary_depth_number, midBeam))
                #     tributary_depth = tributary(joistProp["direction"], beamProp["direction"],
                #                                 range_other_direction, midBeam)
                beamProp["joist"].append(
                    {"label": joistProp["label"], "intersection_range": intersection_range,
                     "tributary_depth": tributary_depth})
                load_joist_on_beam(joistProp["label"], joistProp["load"], intersection_range,
                                   tributary_depth, beamProp["direction"],
                                   beamProp["load"]["joist_load"])
                # else:
                #     if tributary1:
                #         range_other_direction = (min(joistStart, midBeam), max(joistStart, midBeam))
                #         tributary1_depth = tributary(joistProp["direction"], beamProp["direction"],
                #                                      range_other_direction, midBeam)
                #         beamProp["joist"].append(
                #             {"label": joistProp["label"], "intersection_range": intersection_range,
                #              "tributary_depth": tributary1_depth})
                #         load_joist_on_beam(joistProp["label"], joistProp["load"], intersection_range,
                #                            tributary1_depth, beamProp["direction"],
                #                            beamProp["load"]["joist_load"])
                #
                #     if tributary2:
                #         range_other_direction = (min(joistEnd, midBeam), max(joistEnd, midBeam))
                #
                #         tributary2_depth = tributary(joistProp["direction"], beamProp["direction"],
                #                                      range_other_direction, midBeam)
                #         # tributary2_depth = (min(joistEnd, midBeam), (joistEnd + midBeam) / 2)
                #         beamProp["joist"].append(
                #             {"label": joistProp["label"], "intersection_range": intersection_range,
                #              "tributary_depth": tributary2_depth})
                #         load_joist_on_beam(joistProp["label"], joistProp["load"], intersection_range,
                #                            tributary2_depth, beamProp["direction"],
                #                            beamProp["load"]["joist_load"])
            # else:
            #     lines = joistProp["line"]["properties"]
            #     for i in range(len(lines)):
            #         slope_joist = lines[i]["slope"]
            #         c_joist = lines[i]["c"]
            #         range_joist_line = lines[i]["range"]
            #         startPointTolerate = abs(c_joist - c_beam)
            #         if startPointTolerate < 15:
            #             startStatus = True
            #         else:
            #             startStatus = False
            #         if slope_joist == slope_beam and startStatus:
            #             intersection_range = range_intersection(range_joist_line, range_beam)
            #             if intersection_range:
            #                 # for tributary calculation
            #                 try:
            #                     range_other_direction = lines[i + 1]["range"]
            #                 except:
            #                     range_other_direction = lines[i - 1]["range"]
            #
            #                 tributary_depth = tributary(joistProp["direction"], beamProp["direction"],
            #                                             range_other_direction, beamProp["line"]["properties"]["c"])
            #
            #                 beamProp["joist"].append(
            #                     {"label": joistProp["label"], "intersection_range": intersection_range,
            #                      "tributary_depth": tributary_depth})
            #
            #                 load_joist_on_beam(joistProp["label"], joistProp["load"], intersection_range,
            #                                    tributary_depth, beamProp["direction"],
            #                                    beamProp["load"]["joist_load"])


def tributary(direction_joist, direction_beam, main_range, c):
    if direction_beam == direction_joist:
        # TRIBUTARY AREA IS A CONSTANT NUMBER HERE.
        start_min = min(main_range[0], main_range[1])
        if c > start_min:
            tributary_depth = c - 1 * magnification_factor
        else:
            tributary_depth = c + 1 * magnification_factor


    else:
        tributary_depth = (main_range[1] + main_range[0]) / 2
    start_range = min(c, tributary_depth)
    end_range = max(c, tributary_depth)
    return start_range, end_range


class beam_control:
    def __init__(self, beam, post, shearWall, joist):
        self.beam = beam
        self.post = post
        self.shearWall = shearWall
        self.joist = joist

        beam_control_length(self.beam)
        beam_control_direction_and_line(self.beam)
        beam_control_support(self.beam, self.post, self.shearWall)
        beam_control_joist(self.beam, self.joist)
