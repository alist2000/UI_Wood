from back.load_control import range_intersection


# midline_dict = [{"line": "grid line", "area": "area", "magnitude": "magnitude"}]


class midline_range:
    def __init__(self, direction, load_x_range, load_y_range, grid_range):
        self.direction = direction
        self.load_x_range = load_x_range
        self.load_y_range = load_y_range
        self.grid_range = grid_range

        self.x_range = None
        self.y_range = None
        self.control_direction()

    def control_direction(self):
        if self.direction in ["N-S", "vertical"]:
            self.y_range = self.load_y_range
            self.x_range = range_intersection(self.load_x_range, self.grid_range)
        else:
            self.x_range = self.load_x_range
            self.y_range = range_intersection(self.load_y_range, self.grid_range)


class midline_area_calc:
    def __init__(self, magnitude, x_range, y_range, Type):
        self.x_range = x_range
        self.y_range = y_range

        width = abs(self.x_range[1] - self.x_range[0])
        height = abs(self.y_range[1] - self.y_range[0])
        area = width * height

        self.midline_area_dict = {"area": area, "magnitude": magnitude, "type": Type}


class joist_in_midline:
    def __init__(self, joist, grid):
        self.grid = grid
        self.joist = joist
        vertical_grid = grid["vertical"]
        horizontal_grid = grid["horizontal"]
        self.midline_dict = []
        control(joist, vertical_grid, "N-S", self.midline_dict)
        control(joist, horizontal_grid, "E-W", self.midline_dict)


class control:
    def __init__(self, joist, grid, direction, midline_dict):

        for i in range(len(grid) - 1):
            x1 = grid[i]["position"]
            x2 = grid[i + 1]["position"]
            gridRange = (min(x1, x2), max(x1, x2))
            if direction == "N-S":
                free_range = 0  # vertical infinite
                limit_range = 1  # horizontal limited
            else:
                free_range = 1  # vertical infinite
                limit_range = 0  # horizontal limited
            lineProp = []
            midline_dict.append({grid[i]["label"]: lineProp})
            for JoistProp in joist.values():
                joist_range = JoistProp["line"]["properties"][limit_range]["range"]
                joist_grid_intersection = range_intersection(gridRange, joist_range)
                if joist_grid_intersection:
                    joistLoadTotal = JoistProp["load"]["total_area"]
                    for load in joistLoadTotal:
                        midline = midline_area_calc(load["magnitude"],
                                                    joist_grid_intersection,
                                                    JoistProp["line"]["properties"][free_range]["range"], load["type"])
                        lineProp.append(midline.midline_area_dict)

                    joistLoadCustom = JoistProp["load"]["custom_area"]
                    for load in joistLoadCustom:
                        load_x_range = (load["x1"], load["x2"])
                        load_y_range = (load["y1"], load["y2"])
                        midlineRange = midline_range(direction, load_x_range, load_y_range, gridRange)

                        x_range = midlineRange.x_range
                        y_range = midlineRange.y_range
                        if x_range and y_range:
                            midline = midline_area_calc(load["magnitude"], x_range, y_range,
                                                        load["type"])
                            lineProp.append(midline.midline_area_dict)
                    joistLoadMap = JoistProp["load"]["load_map"]
                    for load_set in joistLoadMap:
                        load_x_range = load_set["range_x"]
                        load_y_range = load_set["range_y"]
                        midlineRange = midline_range(direction, load_x_range, load_y_range, gridRange)

                        x_range = midlineRange.x_range
                        y_range = midlineRange.y_range
                        if x_range and y_range:
                            for load in load_set["load"]:
                                midline = midline_area_calc(load["magnitude"], x_range, y_range,
                                                            load["type"])
                                lineProp.append(midline.midline_area_dict)


# joist = {"<joist_new.joistRectangle(0x29616f25bb0, pos=0,0) at 0x0000029617CDB000>": {'label': 'J1',
#                                                                                       'coordinate': [(35.0, 95.0),
#                                                                                                      (35.0, 303.0),
#                                                                                                      (408.0, 303.0),
#                                                                                                      (408.0, 95.0)],
#                                                                                       'direction': 'N-S', 'load': {
#         'total_area': [{'type': 'Dead', 'magnitude': 2.0}],
#         'custom_area': [{'type': 'Dead', 'magnitude': 4.0, 'x1': 35.0, 'y1': 95.0, 'x2': 115.0, 'y2': 215.0}]},
#                                                                                       'line': {'point': [
#                                                                                           ((35.0, 95.0), (35.0, 303.0)),
#                                                                                           ((35.0, 303.0),
#                                                                                            (408.0, 303.0)), (
#                                                                                               (408.0, 303.0),
#                                                                                               (408.0, 95.0)), (
#                                                                                               (408.0, 95.0),
#                                                                                               (35.0, 95.0))],
#                                                                                           'properties': [
#                                                                                               {'slope': False,
#                                                                                                'c': 35.0,
#                                                                                                'range': (
#                                                                                                    95.0, 303.0)},
#                                                                                               {'slope': True,
#                                                                                                'c': 303.0,
#                                                                                                'range': (
#                                                                                                    35.0, 408.0)},
#                                                                                               {'slope': False,
#                                                                                                'c': 408.0,
#                                                                                                'range': (
#                                                                                                    95.0, 303.0)},
#                                                                                               {'slope': True,
#                                                                                                'c': 95.0,
#                                                                                                'range': (
#                                                                                                    35.0, 408.0)}]},
#                                                                                       'support': []},
#          "<joist_new.joistRectangle(0x29616f25230, pos=0,0) at 0x0000029617CEE940>": {'label': 'J2',
#                                                                                       'coordinate': [(-28.0, 200.0),
#                                                                                                      (-28.0, 360.0),
#                                                                                                      (158.0, 360.0),
#                                                                                                      (158.0, 200.0)],
#                                                                                       'direction': 'N-S', 'load': {
#                  'total_area': [{'type': 'Dead', 'magnitude': 2.0}], 'custom_area': [
#                      {'type': 'Dead', 'magnitude': 7.0, 'x1': 80.0, 'y1': 200.0, 'x2': 120.0, 'y2': 280.0}]}, 'line': {
#                  'point': [((-28.0, 200.0), (-28.0, 360.0)), ((-28.0, 360.0), (158.0, 360.0)),
#                            ((158.0, 360.0), (158.0, 200.0)), ((158.0, 200.0), (-28.0, 200.0))],
#                  'properties': [{'slope': False, 'c': -28.0, 'range': (200.0, 360.0)},
#                                 {'slope': True, 'c': 360.0, 'range': (-28.0, 158.0)},
#                                 {'slope': False, 'c': 158.0, 'range': (200.0, 360.0)},
#                                 {'slope': True, 'c': 200.0, 'range': (-28.0, 158.0)}]}, 'support': []}}


# joist = {"<joist_new.joistRectangle(0x14fde4f7b90, pos=0,0) at 0x0000014FDF1A4080>": {'label': 'J2',
#                                                                                       'coordinate': [(-44.0, 71.0),
#                                                                                                      (-44.0, 271.0),
#                                                                                                      (126.0, 271.0),
#                                                                                                      (126.0, 71.0)],
#                                                                                       'direction': 'N-S', 'load': {
#         'total_area': [{'type': 'Dead', 'magnitude': 1.0}],
#         'custom_area': [{'type': 'Dead', 'magnitude': 2.0, 'x1': 0.0, 'y1': 71.0, 'x2': 80.0, 'y2': 111.0}]}, 'line': {
#         'point': [((-44.0, 71.0), (-44.0, 271.0)), ((-44.0, 271.0), (126.0, 271.0)), ((126.0, 271.0), (126.0, 71.0)),
#                   ((126.0, 71.0), (-44.0, 71.0))], 'properties': [{'slope': False, 'c': -44.0, 'range': (71.0, 271.0)},
#                                                                   {'slope': True, 'c': 271.0, 'range': (-44.0, 126.0)},
#                                                                   {'slope': False, 'c': 126.0, 'range': (71.0, 271.0)},
#                                                                   {'slope': True, 'c': 71.0, 'range': (-44.0, 126.0)}]},
#                                                                                       'support': []},
#          " <joist_new.joistRectangle(0x14fde4f8790, pos=0,0) at 0x0000014FDF1A4400>": {'label': 'J3',
#                                                                                        'coordinate': [(195.0, 124.0),
#                                                                                                       (195.0, 223.0),
#                                                                                                       (312.0, 223.0),
#                                                                                                       (312.0, 124.0)],
#                                                                                        'direction': 'N-S',
#                                                                                        'load': {'total_area': [],
#                                                                                                 'custom_area': [
#                                                                                                     {'type': 'Dead',
#                                                                                                      'magnitude': 4.0,
#                                                                                                      'x1': 195.0,
#                                                                                                      'y1': 124.0,
#                                                                                                      'x2': 235.0,
#                                                                                                      'y2': 164.0}]},
#                                                                                        'line': {'point': [((195.0,
#                                                                                                             124.0), (
#                                                                                                            195.0,
#                                                                                                            223.0)), ((
#                                                                                                                      195.0,
#                                                                                                                      223.0),
#                                                                                                                      (
#                                                                                                                      312.0,
#                                                                                                                      223.0)),
#                                                                                                           ((312.0,
#                                                                                                             223.0), (
#                                                                                                            312.0,
#                                                                                                            124.0)), ((
#                                                                                                                      312.0,
#                                                                                                                      124.0),
#                                                                                                                      (
#                                                                                                                      195.0,
#                                                                                                                      124.0))],
#                                                                                                 'properties': [
#                                                                                                     {'slope': False,
#                                                                                                      'c': 195.0,
#                                                                                                      'range': (
#                                                                                                      124.0, 223.0)},
#                                                                                                     {'slope': True,
#                                                                                                      'c': 223.0,
#                                                                                                      'range': (
#                                                                                                      195.0, 312.0)},
#                                                                                                     {'slope': False,
#                                                                                                      'c': 312.0,
#                                                                                                      'range': (
#                                                                                                      124.0, 223.0)},
#                                                                                                     {'slope': True,
#                                                                                                      'c': 124.0,
#                                                                                                      'range': (
#                                                                                                      195.0, 312.0)}]},
#                                                                                        'support': []},
#          "<joist_new.joistRectangle(0x14fde4f8690, pos=0,0) at 0x0000014FDF1A4E80>": {'label': 'J4',
#                                                                                       'coordinate': [(355.0, 284.0),
#                                                                                                      (355.0, 411.0),
#                                                                                                      (531.0, 411.0),
#                                                                                                      (531.0, 284.0)],
#                                                                                       'direction': 'N-S', 'load': {
#                  'total_area': [{'type': 'Dead', 'magnitude': 5.0}],
#                  'custom_area': [{'type': 'Dead', 'magnitude': 7.0, 'x1': 355.0, 'y1': 284.0, 'x2': 435.0, 'y2': 284.0},
#                                  {'type': 'Dead', 'magnitude': 8.0, 'x1': 355.0, 'y1': 284.0, 'x2': 435.0,
#                                   'y2': 364.0}]}, 'line': {
#                  'point': [((355.0, 284.0), (355.0, 411.0)), ((355.0, 411.0), (531.0, 411.0)),
#                            ((531.0, 411.0), (531.0, 284.0)), ((531.0, 284.0), (355.0, 284.0))],
#                  'properties': [{'slope': False, 'c': 355.0, 'range': (284.0, 411.0)},
#                                 {'slope': True, 'c': 411.0, 'range': (355.0, 531.0)},
#                                 {'slope': False, 'c': 531.0, 'range': (284.0, 411.0)},
#                                 {'slope': True, 'c': 284.0, 'range': (355.0, 531.0)}]}, 'support': []}}
# joist = {"<joist_new.joistRectangle(0x14b61d9c6f0, pos=0,0) at 0x0000014B62A806C0>": {'label': 'J1', 'coordinate': [(98.0, 54.0), (98.0, 170.0), (247.0, 170.0), (247.0, 54.0)], 'direction': 'N-S', 'load': {'total_area': [{'type': 'Dead', 'magnitude': 1.0}], 'custom_area': [{'type': 'Dead', 'magnitude': 1.0, 'x1': 138.0, 'y1': 54.0, 'x2': 138.0, 'y2': 54.0}]}, 'line': {'point': [((98.0, 54.0), (98.0, 170.0)), ((98.0, 170.0), (247.0, 170.0)), ((247.0, 170.0), (247.0, 54.0)), ((247.0, 54.0), (98.0, 54.0))], 'properties': [{'slope': False, 'c': 98.0, 'range': (54.0, 170.0)}, {'slope': True, 'c': 170.0, 'range': (98.0, 247.0)}, {'slope': False, 'c': 247.0, 'range': (54.0, 170.0)}, {'slope': True, 'c': 54.0, 'range': (98.0, 247.0)}]}, 'support': []}, "<joist_new.joistRectangle(0x14b61d9ce70, pos=0,0) at 0x0000014B62A81200>": {'label': 'J2', 'coordinate': [(40.0, 216.0), (40.0, 345.0), (145.0, 345.0), (145.0, 216.0)], 'direction': 'N-S', 'load': {'total_area': [], 'custom_area': []}, 'line': {'point': [((40.0, 216.0), (40.0, 345.0)), ((40.0, 345.0), (145.0, 345.0)), ((145.0, 345.0), (145.0, 216.0)), ((145.0, 216.0), (40.0, 216.0))], 'properties': [{'slope': False, 'c': 40.0, 'range': (216.0, 345.0)}, {'slope': True, 'c': 345.0, 'range': (40.0, 145.0)}, {'slope': False, 'c': 145.0, 'range': (216.0, 345.0)}, {'slope': True, 'c': 216.0, 'range': (40.0, 145.0)}]}, 'support': []}, "<joist_new.joistRectangle(0x14b61d9d4b0, pos=0,0) at 0x0000014B62A81B40>": {'label': 'J3', 'coordinate': [(174.0, 289.0), (174.0, 478.0), (498.0, 478.0), (498.0, 289.0)], 'direction': 'N-S', 'load': {'total_area': [], 'custom_area': []}, 'line': {'point': [((174.0, 289.0), (174.0, 478.0)), ((174.0, 478.0), (498.0, 478.0)), ((498.0, 478.0), (498.0, 289.0)), ((498.0, 289.0), (174.0, 289.0))], 'properties': [{'slope': False, 'c': 174.0, 'range': (289.0, 478.0)}, {'slope': True, 'c': 478.0, 'range': (174.0, 498.0)}, {'slope': False, 'c': 498.0, 'range': (289.0, 478.0)}, {'slope': True, 'c': 289.0, 'range': (174.0, 498.0)}]}, 'support': []}}
#
# grid = {'vertical': [{'label': 'A', 'position': 0}, {'label': 'B', 'position': 400}],
#         'horizontal': [{'label': '1', 'position': 0}, {'label': '2', 'position': 400}]}
#
# instance = joist_in_midline(joist, grid)
# print(instance.midline_dict)
