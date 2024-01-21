import copy

from back.load_control import range_intersection
import sys

sys.path.append(r"D:\Learning\Qt\code\practice\UI_Wood\08.1")
from post_new import magnification_factor


# midline_dict = [{"line": "grid line", "area": "area", "magnitude": "magnitude"}]


class midline_range:
    def __init__(self, direction, load_x_range, load_y_range, grid_range, limit_range_grid):
        self.direction = direction
        self.load_x_range = load_x_range
        self.load_y_range = load_y_range
        self.grid_range = grid_range
        self.limit_range_grid = limit_range_grid

        self.x_range = None
        self.y_range = None
        self.control_direction()

    def control_direction(self):
        if self.direction in ["N-S", "vertical"]:
            self.y_range = range_intersection(self.limit_range_grid, self.load_y_range)
            self.x_range = range_intersection(self.load_x_range, self.grid_range)
        else:
            self.x_range = range_intersection(self.limit_range_grid, self.load_x_range)
            self.y_range = range_intersection(self.load_y_range, self.grid_range)


class midline_area_calc:
    def __init__(self, magnitude, x_range, y_range):
        self.x_range = x_range
        self.y_range = y_range

        width = abs(self.x_range[1] - self.x_range[0])
        height = abs(self.y_range[1] - self.y_range[0])
        area = width * height / (magnification_factor ** 2)

        # self.midline_area_dict = {"area": area, "magnitude": magnitude, "type": Type}
        self.midline_area_dict = {"area": area, "magnitude": magnitude * 1000}


class joist_in_midline:
    def __init__(self, joist, grid):
        self.grid = grid
        self.joist = joist
        vertical_grid = grid["vertical"]
        horizontal_grid = grid["horizontal"]
        self.midline_dict = []
        control(joist, vertical_grid, horizontal_grid, "N-S", self.midline_dict)
        control(joist, horizontal_grid, vertical_grid, "E-W", self.midline_dict)


class control:
    def __init__(self, joist, grid, gridPerp, direction, midline_dict):

        for i in range(len(grid)):
            gridRange = self.GridRange(grid, i)
            limitRangeGrid = self.LimitRange(grid, gridPerp, i)
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

                    # WRONG CODE SHOULD DEVELOP LATER
                    joistLoadTotal = JoistProp["load"]["total_area"]
                    loadSetEdited = self.ControlDeadSuperExist(joistLoadTotal)
                    for load in loadSetEdited:
                        if load["type"] == "Dead Super":
                            midline = midline_area_calc(load["magnitude"],
                                                        joist_grid_intersection,
                                                        JoistProp["line"]["properties"][free_range]["range"],
                                                        )
                            lineProp.append(midline.midline_area_dict)

                    # WRONG CODE SHOULD DEVELOP LATER
                    joistLoadCustom = JoistProp["load"]["custom_area"]
                    loadSetEdited = self.ControlDeadSuperExist(joistLoadCustom)
                    for load in loadSetEdited:
                        load_x_range = (load["x1"], load["x2"])
                        load_y_range = (load["y1"], load["y2"])
                        midlineRange = midline_range(direction, load_x_range, load_y_range, gridRange)

                        x_range = midlineRange.x_range
                        y_range = midlineRange.y_range
                        if x_range and y_range:
                            if load["type"] == "Dead Super":
                                midline = midline_area_calc(load["magnitude"], x_range, y_range,
                                                            )
                                lineProp.append(midline.midline_area_dict)
                    joistLoadMap = JoistProp["load"]["load_map"]
                    for load_set in joistLoadMap:
                        load_x_range = load_set["range_x"]
                        load_y_range = load_set["range_y"]
                        midlineRange = midline_range(direction, load_x_range, load_y_range, gridRange, limitRangeGrid)

                        x_range = midlineRange.x_range
                        y_range = midlineRange.y_range
                        if x_range and y_range:
                            loadSetEdited = self.ControlDeadSuperExist(load_set["load"])
                            for load in loadSetEdited:

                                if load["type"] == "Dead Super":
                                    midline = midline_area_calc(load["magnitude"], x_range, y_range,
                                                                )
                                    lineProp.append(midline.midline_area_dict)

    @staticmethod
    def ControlDeadSuperExist(loads):
        loadTypes = []
        loadMags = []
        for load in loads:
            loadTypes.append(load["type"])
            loadMags.append(load["magnitude"])
        if "Dead Super" in loadTypes:
            return loads
        elif "Dead" in loadTypes:
            deadIndex = loadTypes.index("Dead")
            SuperDeadMag = loadMags[deadIndex] + 0.01  # consider dead super = dead + 10 psf
            loads.append({
                "type": "Dead Super",
                "magnitude": SuperDeadMag
            })
        return loads

    @staticmethod
    def GridRange(grids, i):
        posMain = grids[i]["position"]
        if i > 0:
            iNew = copy.deepcopy(i)
            while i - 1 >= 0 and grids[iNew - 1]["position"] == posMain:
                iNew = iNew - 1
            startPos = (posMain + grids[iNew - 1]["position"]) / 2

        else:
            # startPos = posMain
            startPos = -float("inf")

        if i < len(grids) - 1:
            iNew = copy.deepcopy(i)
            while i - 1 >= 0 and grids[iNew + 1]["position"] == posMain:
                iNew = iNew + 1
            endPos = (grids[iNew + 1]["position"] + posMain) / 2
        else:
            # endPos = posMain
            endPos = float("inf")
        return startPos, endPos

    @staticmethod
    def LimitRange(grids, gridPerp, i):
        startRange = gridPerp[0]["position"]
        endRange = gridPerp[-1]["position"]

        if grids[i]["start"] == startRange:
            startRange = -float("inf")
        else:
            startRange = grids[i]["start"]

        if grids[i]["end"] == endRange:
            endRange = float("inf")
        else:
            endRange = grids[i]["end"]

        return startRange, endRange


class EditGrid:
    def __init__(self, shearWall, grid):
        self.shearWallProp = shearWall.values()
        self.grid = grid
        shearWallLines = set()
        self.v_grid_labels = set()
        self.h_grid_labels = set()

        vGrid = grid["vertical"]
        hGrid = grid["horizontal"]
        for i in vGrid:
            self.v_grid_labels.add(i["label"])
        for i in hGrid:
            self.h_grid_labels.add(i["label"])

        for sw in self.shearWallProp:
            shearWallLines.add(sw["line_label"])
        vGridNewLabel = self.v_grid_labels & shearWallLines
        hGridNewLabel = self.h_grid_labels & shearWallLines
        vGridNew = [i for i in vGrid if i["label"] in vGridNewLabel]
        hGridNew = [i for i in hGrid if i["label"] in hGridNewLabel]
        self.vGridNew = self.controlStartEnd(vGridNew)
        self.hGridNew = self.controlStartEnd(hGridNew)

    @staticmethod
    def controlStartEnd(grid):
        for i, gridList in enumerate(grid):
            position = gridList["position"]
            if i < len(grid) - 1:
                nextGrid = grid[i + 1]
                positionNext = nextGrid["position"]
                if positionNext != position:  # there is no second line or void
                    gridList["end"] = float("inf")
                    gridList["start"] = -float("inf")
            else:
                behindGrid = grid[i - 1]
                positionBehind = behindGrid["position"]
                if positionBehind != position:  # there is no second line or void
                    gridList["end"] = float("inf")
                    gridList["start"] = -float("inf")
        return grid

    def output(self):
        return {"vertical": self.vGridNew, "horizontal": self.hGridNew}
