import copy

from UI_Wood.stableVersion5.back.load_control import range_intersection
import sys

from UI_Wood.stableVersion5.post_new import magnification_factor


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
        if vertical_grid and horizontal_grid:
            control(joist, vertical_grid, horizontal_grid, "N-S", self.midline_dict)
            control(joist, horizontal_grid, vertical_grid, "E-W", self.midline_dict)


class control:
    def __init__(self, joist, grid, gridPerp, direction, midline_dict):
        grid_edited = []
        for gridItem in grid:
            grid_edited.append(GridLine(name=gridItem["label"], position=gridItem["position"], start=gridItem["start"],
                                        end=gridItem["end"]))
        gridRange1 = GridLineManager(grid_edited)
        for i, line in enumerate(gridRange1.grid_lines):
            perpendicular_ranges = gridRange1.get_perpendicular_ranges(i)
            print(f"Grid line at position {line.position} (start: {line.start}, end: {line.end}):")
            for j, range in enumerate(perpendicular_ranges):
                print(f"  Range {j + 1}: {range}")
        # for i in range(len(grid)):
        #     perpendicular_range = gridRange1.get_perpendicular_range(i)
        #     print(f"Grid line at position {grid[i]['position']}: Perpendicular range = {perpendicular_range}")

        for i, line in enumerate(gridRange1.grid_lines):
            grid_range = gridRange1.get_perpendicular_ranges(i)

            # gridRange = self.GridRange(grid, i)
            # limitRangeGrid = self.LimitRange(grid, gridPerp, i)
            if direction == "N-S":
                free_range = 0  # vertical infinite
                limit_range = 1  # horizontal limited
            else:
                free_range = 1  # vertical infinite
                limit_range = 0  # horizontal limited
            lineProp = []
            midline_dict.append({gridRange1.grid_lines[i].name: lineProp})
            # D = [PerpendicularRange(start=-inf, end=2270.0, left_boundary=2001.6699999999998, right_boundary=2533.3379999999997), PerpendicularRange(start=2270.0, end=3266.668, left_boundary=-inf, right_boundary=2533.3379999999997), PerpendicularRange(start=3266.668, end=inf, left_boundary=2110.836, right_boundary=2533.3379999999997)]
            for grid_item in grid_range:
                gridRange = (grid_item.left_boundary, grid_item.right_boundary)
                limitRangeGrid = (grid_item.start, grid_item.end)
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
                            midlineRange = midline_range(direction, load_x_range, load_y_range, gridRange,
                                                         limitRangeGrid)

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
        endDefaultY = max([i["position"] for i in hGridNew])

        endDefaultX = max([i["position"] for i in vGridNew])

        self.vGridNew = self.controlStartEnd(vGridNew, endDefaultY)
        self.hGridNew = self.controlStartEnd(hGridNew, endDefaultX)

    @staticmethod
    def controlStartEnd(grid, end_default):
        for i, gridList in enumerate(grid):
            start = gridList["start"]
            if not start:
                gridList["start"] = -float("inf")
            end = gridList["end"]
            if round(end, 2) == round(end_default, 2):
                gridList["end"] = float("inf")

            # if i < len(grid) - 1:
            #     nextGrids = grid[i + 1:]
            # else:
            #     nextGrids = grid[:i]  # Behind
            # void = False
            # for j, OtherGrid in enumerate(grid):
            #     if i != j:
            #         positionNext = OtherGrid["position"]
            #         if round(positionNext, 2) == round(position, 2):  # there is no second line or void
            #             void = True
            #             break
            # if not void:
            #     gridList["end"] = float("inf")
            #     gridList["start"] = -float("inf")
            # else:
            #     void = True
            #     behindGrids = grid[:i]
            #     for behindGrid in behindGrids:
            #         positionBehind = behindGrid["position"]
            #         if round(positionBehind, 2) == round(position, 2):  # there is no second line or void
            #             void = False
            #             break
            #     if not void:
            #         gridList["end"] = float("inf")
            #         gridList["start"] = -float("inf")
        return grid

    def output(self):
        return {"vertical": self.vGridNew, "horizontal": self.hGridNew}


from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class GridLine:
    position: float
    start: float
    end: float
    name: str = ""


@dataclass
class PerpendicularRange:
    start: float
    end: float
    left_boundary: float
    right_boundary: float


class GridLineManager:
    def __init__(self, grid_lines: List[GridLine]):
        self.grid_lines = sorted(grid_lines, key=lambda x: x.position)

    def get_perpendicular_ranges(self, index: int) -> List[PerpendicularRange]:
        current_line = self.grid_lines[index]
        prev_lines = self._find_prev_different_lines(index)
        next_lines = self._find_next_different_lines(index)

        ranges = []
        current_start = current_line.start

        while current_start < current_line.end:
            prev_line = self._find_overlapping_line(prev_lines, current_start)
            next_line = self._find_overlapping_line(next_lines, current_start)

            left_boundary = self._calculate_midpoint(prev_line, current_line) if prev_line else float("-inf")
            right_boundary = self._calculate_midpoint(current_line, next_line) if next_line else float("inf")

            range_end = min(
                current_line.end,
                next_line.end if next_line else float("inf"),
                prev_line.end if prev_line else float("inf")
            )

            ranges.append(PerpendicularRange(current_start, range_end, left_boundary, right_boundary))
            current_start = range_end

            # Check if we need to create a new range due to gaps in neighboring lines
            if current_start < current_line.end:
                next_prev_line = self._find_next_overlapping_line(prev_lines, current_start)
                next_next_line = self._find_next_overlapping_line(next_lines, current_start)

                if next_prev_line and next_prev_line.start > current_start:
                    ranges.append(
                        PerpendicularRange(current_start, next_prev_line.start, float("-inf"), right_boundary))
                    current_start = next_prev_line.start
                elif next_next_line and next_next_line.start > current_start:
                    ranges.append(PerpendicularRange(current_start, next_next_line.start, left_boundary, float("inf")))
                    current_start = next_next_line.start

        return ranges

    def _find_prev_different_lines(self, index: int) -> List[GridLine]:
        return [line for line in reversed(self.grid_lines[:index])
                if line.position != self.grid_lines[index].position]

    def _find_next_different_lines(self, index: int) -> List[GridLine]:
        return [line for line in self.grid_lines[index + 1:]
                if line.position != self.grid_lines[index].position]

    @staticmethod
    def _find_overlapping_line(lines: List[GridLine], point: float) -> Optional[GridLine]:
        return next((line for line in lines if line.start <= point < line.end), None)

    @staticmethod
    def _find_next_overlapping_line(lines: List[GridLine], point: float) -> Optional[GridLine]:
        return next((line for line in lines if line.start > point), None)

    @staticmethod
    def _calculate_midpoint(line1: GridLine, line2: GridLine) -> float:
        return (line1.position + line2.position) / 2


# Example usage:
grid_lines = [
    GridLine(position=1940, start=0, end=3000, name="A"),  # Line D
    GridLine(position=1880, start=0, end=2270, name="B"),  # Line behind D (partial)
    GridLine(position=1860, start=3500, end=4000, name="C"),  # Line behind D (partial)
    GridLine(position=2400, start=0, end=4000, name="D"),  # Line in front of D
]

manager = GridLineManager(grid_lines)
for i, line in enumerate(grid_lines):
    perpendicular_ranges = manager.get_perpendicular_ranges(i)
    print(f"Grid line at position {line.position} (start: {line.start}, end: {line.end}, name: {line.name}):")
    for j, range in enumerate(perpendicular_ranges):
        print(f"  Range {j + 1}: {range}")
    print()
