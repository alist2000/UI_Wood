import sys

sys.path.append(r"D:\Learning\Qt\code\practice\UI_Wood\08.")
from post_new import magnification_factor
from back.load_control import load_joist_on_beam, range_intersection


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
            if abs(width) > abs(height):
                direction = "E-W"
            else:
                direction = "N-S"
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
                is_support, post_range = self.main_is_point_on_line(postProp["coordinate"], start, end)
                if is_support:
                    beamProp["support"].append(
                        {"label": postProp["label"], "type": "post", "coordinate": postProp["coordinate"],
                         "range": post_range})

    def add_shearWall_post_support(self):
        for beamItem, beamProp in self.beam.items():
            start = beamProp["coordinate"][0]
            end = beamProp["coordinate"][1]
            # Control post support
            # Control ShearWall post support
            for shearWallItem, shearWallProp in self.shearWall.items():
                # note: start and end of shear wall also consider as post coordinate
                is_support1, post_range1 = self.main_is_point_on_line(shearWallProp["post"]["start_center"], start, end)
                is_support2, post_range2 = self.main_is_point_on_line(shearWallProp["coordinate"][0], start, end)
                if is_support1 or is_support2:
                    if is_support1:
                        post_range = post_range1
                        coordinate = shearWallProp["post"]["start_center"]
                    else:
                        post_range = post_range2
                        coordinate = shearWallProp["coordinate"][0]
                    beamProp["support"].append(
                        {"label": shearWallProp["post"]["label_start"], "type": "shearWall_post",
                         "coordinate": coordinate,
                         "range": post_range})
                is_support1, post_range1 = self.main_is_point_on_line(shearWallProp["post"]["end_center"], start, end)
                is_support2, post_range2 = self.main_is_point_on_line(shearWallProp["coordinate"][1], start, end)

                if is_support1 or is_support2:
                    if is_support1:
                        post_range = post_range1
                        coordinate = shearWallProp["post"]["end_center"]

                    else:
                        post_range = post_range2
                        coordinate = shearWallProp["coordinate"][1]

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
                    is_support, post_range = self.main_is_point_on_line(start, start2, end2)
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
                        if add:
                            beamProp["support"].append(
                                {"label": beamProp2["label"], "type": Type,
                                 "coordinate": start,
                                 "range": "start"})

                    # CONTROL END BEAM SUPPORT (BEAM TO BEAM)
                    is_support, post_range = self.main_is_point_on_line(end, start2, end2)
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
                        if add:
                            beamProp["support"].append(
                                {"label": beamProp2["label"], "type": Type,
                                 "coordinate": end,
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
    def is_point_on_line(point, line_point1, line_point2):
        (x0, y0) = point
        (x1, y1) = line_point1
        (x2, y2) = line_point2

        # Calculate the slopes
        if x2 - x1 == 0:  # To avoid division by zero
            return x0 == x1 and min(y1, y2) <= y0 <= max(y1, y2)
        if x0 - x1 == 0:
            return y0 == y1 and min(x1, x2) <= x0 <= max(x1, x2)
        slope1 = (y2 - y1) / (x2 - x1)
        slope2 = (y0 - y1) / (x0 - x1)

        return slope1 == slope2 and min(x1, x2) <= x0 <= max(x1, x2)

    def main_is_point_on_line(self, point, start, end):
        is_support = self.is_point_on_line(point, start, end)
        post_range = None
        if is_support:
            if point == start:
                post_range = "start"
            elif point == end:
                post_range = "end"
            else:
                post_range = "mid"
        return is_support, post_range


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
        self.control_intersection()

    def control_intersection(self):
        for beamProp in self.beam.values():
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
                    if slope_joist == slope_beam and c_joist == c_beam:
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

        # beam_control_length(self.beam)
        beam_control_direction_and_line(self.beam)
        beam_control_support(self.beam, self.post, self.shearWall)
        beam_control_joist(self.beam, self.joist)


# Beam = {"beamItem1": {"label": "B1", "coordinate": [(0, 0), (4, 3)]},
#         "beamItem2": {"label": "B2", "coordinate": [(0, 0), (10.4, 20)]}}
# Post = {"postItem1": {"label": "P1", "coordinate": (10.4, 20)},
#         "postItem2": {"label": "P2", "coordinate": (5, 10.4)}}
# ShearWall = {"<ShearWall.Rectangle(0x1e25840c970, pos=0,0) at 0x000001E2592E4140>": {'label': 'SW1',
#                                                                                      'coordinate': [(400.0, 59.0),
#                                                                                                     (400.0, 330.0)],
#                                                                                      'post': {'label_start': 'SWP1',
#                                                                                               'label_end': 'SWP2',
#                                                                                               'start_rect_item': "<PySide6.QtWidgets.QGraphicsRectItem(0x1e25840ca70, pos=0,0) at 0x000001E2592E46C0>",
#                                                                                               'end_rect_item': "<PySide6.QtWidgets.QGraphicsRectItem(0x1e25840c2b0, pos=0,0) at 0x000001E2592E4700>",
#                                                                                               'start_center': (
#                                                                                                   400.0, 69.0),
#                                                                                               'end_center': (
#                                                                                                   400.0, 320.0)},
#                                                                                      'direction': 'N-S',
#                                                                                      'interior_exterior': 'exterior'},
#              "<ShearWall.Rectangle(0x1e25840cf70, pos=0,0) at 0x000001E2592E43C0>": {'label': 'SW2',
#                                                                                      'coordinate': [(0.0, 197.0),
#                                                                                                     (0.0, 277.0)],
#                                                                                      'post': {'label_start': 'SWP3',
#                                                                                               'label_end': 'SWP4',
#                                                                                               'start_rect_item': "<PySide6.QtWidgets.QGraphicsRectItem(0x1e25840c3f0, pos=0,0) at 0x000001E2592E4C40>",
#                                                                                               'end_rect_item': "<PySide6.QtWidgets.QGraphicsRectItem(0x1e25840c530, pos=0,0) at 0x000001E2592E4C80>",
#                                                                                               'start_center': (
#                                                                                                   0.0, 207.0),
#                                                                                               'end_center': (
#                                                                                                   0.0, 267.0)},
#                                                                                      'direction': 'N-S',
#                                                                                      'interior_exterior': 'exterior'}}
# Beam = {"<Beam.Rectangle(0x1e25840ca30, pos=0,0) at 0x000001E2592CD980>": {'label': 'B1',
#                                                                            'coordinate': [(0.0, 0.0), (400.0, 0.0)]},
#         "<Beam.Rectangle(0x1e25840ce70, pos=0,0) at 0x000001E2592D06C0>": {'label': 'B2',
#                                                                            'coordinate': [(0.0, 0.0), (0.0, 400.0)]},
#         "<Beam.Rectangle(0x1e25840cbf0, pos=0,0) at 0x000001E2592E3480>": {'label': 'B3', 'coordinate': [(0.0, 400.0), (
#             400.0, 400.0)]}, "<Beam.Rectangle(0x1e25840cf30, pos=0,0) at 0x000001E2592E36C0>": {'label': 'B4',
#                                                                                                 'coordinate': [
#                                                                                                     (400.0, 400.0),
#                                                                                                     (400.0, 0.0)]},
#         "<Beam.Rectangle(0x1e25840c9b0, pos=0,0) at 0x000001E2592E38C0>": {'label': 'B5', 'coordinate': [(0.0, 197.0), (
#             400.0, 197.0)]}}
# Post = {
#     "<post_new.CustomRectItem(0x1e25840b570, pos=0,0, flags=(ItemIsMovable|ItemIsSelectable)) at 0x000001E2592CCB00>": {
#         'label': 'P1', 'coordinate': (0.0, 0.0)},
#     "<post_new.CustomRectItem(0x1e25840bb70, pos=0,0, flags=(ItemIsMovable|ItemIsSelectable)) at 0x000001E2592CD000>": {
#         'label': 'P2', 'coordinate': (0.0, 400.0)}}
# ShearWall = {"<ShearWall.Rectangle(0x1c31bbffa30, pos=0,0) at 0x000001C31C9AAF40>": {'label': 'SW1',
#                                                                                      'coordinate': [(400.0, 0.0),
#                                                                                                     (400.0, 140.0)],
#                                                                                      'post': {'label_start': 'SWP1',
#                                                                                               'label_end': 'SWP2',
#                                                                                               'start_rect_item': "<PySide6.QtWidgets.QGraphicsRectItem(0x1c31bbffaf0, pos=0,0) at 0x000001C31C9AB480>",
#                                                                                               'end_rect_item': "<PySide6.QtWidgets.QGraphicsRectItem(0x1c31bbff830, pos=0,0) at 0x000001C31C9AB4C0>",
#                                                                                               'start_center': (
#                                                                                                   400.0, 10.4.0),
#                                                                                               'end_center': (
#                                                                                                   400.0, 130.0)},
#                                                                                      'direction': 'N-S',
#                                                                                      'interior_exterior': 'exterior'},
#              "<ShearWall.Rectangle(0x1c31bc00070, pos=0,0) at 0x000001C31C9AB1C0>": {'label': 'SW2',
#                                                                                      'coordinate': [(47.0, 400.0),
#                                                                                                     (217.0, 400.0)],
#                                                                                      'post': {'label_start': 'SWP3',
#                                                                                               'label_end': 'SWP4',
#                                                                                               'start_rect_item': "<PySide6.QtWidgets.QGraphicsRectItem(0x1c31bbff2b0, pos=0,0) at 0x000001C31C9ABA00>",
#                                                                                               'end_rect_item': "<PySide6.QtWidgets.QGraphicsRectItem(0x1c31bbff8b0, pos=0,0) at 0x000001C31C9ABA40>",
#                                                                                               'start_center': (
#                                                                                                   57.0, 400.0),
#                                                                                               'end_center': (
#                                                                                                   207.0, 400.0)},
#                                                                                      'direction': 'E-W',
#                                                                                      'interior_exterior': 'exterior'}}
# Beam = {"<Beam.Rectangle(0x1c31bbfffb0, pos=0,0) at 0x000001C31C98CB80>": {'label': 'B1', 'coordinate': [(0.0, 400.0), (
#     400.0, 400.0)]}, "<Beam.Rectangle(0x1c31bbff9f0, pos=0,0) at 0x000001C31C9AA600>": {'label': 'B2',
#                                                                                         'coordinate': [(0.0, 0.0),
#                                                                                                        (400.0, 0.0)]},
#         "<Beam.Rectangle(0x1c31bbff4b0, pos=0,0) at 0x000001C31C9AA880>": {'label': 'B3', 'coordinate': [(217.0, 0.0), (
#             217.0, 400.0)]}}
# Post = {
#     "<post_new.CustomRectItem(0x1c31bbfff70, pos=0,0, flags=(ItemIsMovable|ItemIsSelectable)) at 0x000001C31C98C440>": {
#         'label': 'P1', 'coordinate': (0.0, 0.0)},
#     "<post_new.CustomRectItem(0x1c31bbff430, pos=0,0, flags=(ItemIsMovable|ItemIsSelectable)) at 0x000001C31C98C680>": {
#         'label': 'P2', 'coordinate': (-10.4.0, 400.0)}}
Beam = {"<Beam.Rectangle(0x1efd680d550, pos=0,0) at 0x000001EFD74D0E00>": {'label': 'B1', 'coordinate': [(0.0, 400.0), (
    338.0, 400.0)]}, "<Beam.Rectangle(0x1efd680cdd0, pos=0,0) at 0x000001EFD74D0E80>": {'label': 'B2',
                                                                                        'coordinate': [(302.0, 400.0),
                                                                                                       (302.0, 210.0)]},
        " <Beam.Rectangle(0x1efd680cb50, pos=0,0) at 0x000001EFD74D12C0>": {'label': 'B3', 'coordinate': [(202.0, 81.0),
                                                                                                          (202.0,
                                                                                                           275.0)]},
        " <Beam.Rectangle(0x1efd680c7d0, pos=0,0) at 0x000001EFD74D0AC0>": {'label': 'B4',
                                                                            'coordinate': [(302.0, 210.0),
                                                                                           (202.0, 210.0)]},
        "<Beam.Rectangle(0x1efd680ce90, pos=0,0) at 0x000001EFD74D1140>": {'label': 'B5', 'coordinate': [(202.0, 275.0),
                                                                                                         (
                                                                                                             29.0,
                                                                                                             275.0)]},
        "<Beam.Rectangle(0x1efd680d250, pos=0,0) at 0x000001EFD74D1B00>": {'label': 'B6',
                                                                           'coordinate': [(0.0, 400.0), (0.0, 93.0)]},
        "<Beam.Rectangle(0x1efd680cf50, pos=0,0) at 0x000001EFD74D1DC0>": {'label': 'B7', 'coordinate': [(0.0, 141.0), (
            202.0, 141.0)]}}

Post = {
    "<post_new.CustomRectItem(0x1efd680d790, pos=0,0, flags=(ItemIsMovable|ItemIsSelectable)) at 0x000001EFD74D0500>": {
        'label': 'P1', 'coordinate': (0.0, 400.0)},
    "<post_new.CustomRectItem(0x1efd680c810, pos=0,0, flags=(ItemIsMovable|ItemIsSelectable)) at 0x000001EFD74D0840>": {
        'label': 'P2', 'coordinate': (202.0, 81.0)},
    "<post_new.CustomRectItem(0x1efd680c550, pos=0,0, flags=(ItemIsMovable|ItemIsSelectable)) at 0x000001EFD74D2980>": {
        'label': 'P3', 'coordinate': (319.0, 90.0)}}

ShearWall = {}

# a = beam_control(Beam, Post, ShearWall)
# beams = a.beam
# for i in beams.values():
#     print(i["support"])
