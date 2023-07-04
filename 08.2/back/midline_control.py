from load_control import range_intersection


# midline_dict = [{"line": "grid line", "area": "area", "magnitude": "magnitude"}]


class midline_range:
    def __init__(self, direction, load_x_range, load_y_range, grid_range):
        self.direction = direction
        self.load_x_range = load_x_range
        self.load_y_range = load_y_range
        self.grid_range = grid_range
        self.control_direction()

        self.x_range = None
        self.y_range = None

    def control_direction(self):
        if self.direction in ["N-S", "vertical"]:
            self.y_range = self.load_y_range
            self.x_range = range_intersection(self.load_x_range, self.grid_range)
        else:
            self.x_range = self.load_x_range
            self.y_range = range_intersection(self.load_y_range, self.grid_range)


class midline_area_calc:
    def __init__(self, line, magnitude, x_range, y_range, Type):
        self.x_range = x_range
        self.y_range = y_range

        width = abs(self.x_range[1] - self.x_range[0])
        height = abs(self.y_range[1] - self.y_range[0])
        area = width * height

        self.midline_area_dict = {"line": line,
                                  "area": area,
                                  "magnitude": magnitude,
                                  "type": Type}


class joist_in_midline:
    def __init__(self, joist, grid):
        self.grid = grid
        self.joist = joist
        vertical_grid = grid["vertical"]
        horizontal_grid = grid["horizontal"]
        self.midline_dict = []
        for i in range(len(vertical_grid) - 2):
            x1 = vertical_grid[i]["position"]
            x2 = vertical_grid[i + 1]["position"]
            gridRange = x2 - x1
            control(joist, gridRange, vertical_grid, "N-S", self.midline_dict, i)
        for i in range(len(horizontal_grid) - 2):
            x1 = horizontal_grid[i]["position"]
            x2 = horizontal_grid[i + 1]["position"]
            gridRange = x2 - x1
            control(joist, gridRange, horizontal_grid, "E-W", self.midline_dict, i)
            # for JoistProp in joist.values():
            #     joist_range = JoistProp["line"]["properties"][1]["range"]
            #     joist_grid_intersection = range_intersection(gridRange, joist_range)
            #     if joist_grid_intersection:
            #         joistLoadTotal = JoistProp["load"]["total_area"]
            #         for load in joistLoadTotal:
            #             midline = midline_area_calc(vertical_grid[i]["label"], load["magnitude"],
            #                                         joist_grid_intersection,
            #                                         JoistProp["line"]["properties"][0]["range"], load["type"])
            #             self.midline_dict.append(midline.midline_area_dict)
            #
            #         joistLoadCustom = JoistProp["load"]["custom_area"]
            #         for load in joistLoadCustom:
            #             load_x_range = (load["x1"], load["x2"])
            #             load_y_range = (load["y1"], load["y2"])
            #             midlineRange = midline_range("N-S", load_x_range, load_y_range, gridRange)
            #
            #             x_range = midlineRange.x_range
            #             y_range = midlineRange.y_range
            #             midline = midline_area_calc(vertical_grid[i]["label"], load["magnitude"], x_range, y_range,
            #                                         load["type"])
            #             self.midline_dict.append(midline.midline_area_dict)


class control:
    def __init__(self, joist, gridRange, grid, direction, midline_dict, i):
        if direction == "N-S":
            free_range = 0  # vertical infinite
            limit_range = 1  # horizontal limited
        else:
            free_range = 1  # vertical infinite
            limit_range = 0  # horizontal limited
        for JoistProp in joist.values():
            joist_range = JoistProp["line"]["properties"][limit_range]["range"]
            joist_grid_intersection = range_intersection(gridRange, joist_range)
            if joist_grid_intersection:
                joistLoadTotal = JoistProp["load"]["total_area"]
                for load in joistLoadTotal:
                    midline = midline_area_calc(grid[i]["label"], load["magnitude"],
                                                joist_grid_intersection,
                                                JoistProp["line"]["properties"][free_range]["range"], load["type"])
                    midline_dict.append(midline.midline_area_dict)

                joistLoadCustom = JoistProp["load"]["custom_area"]
                for load in joistLoadCustom:
                    load_x_range = (load["x1"], load["x2"])
                    load_y_range = (load["y1"], load["y2"])
                    midlineRange = midline_range(direction, load_x_range, load_y_range, gridRange)

                    x_range = midlineRange.x_range
                    y_range = midlineRange.y_range
                    midline = midline_area_calc(grid[i]["label"], load["magnitude"], x_range, y_range,
                                                load["type"])
                    midline_dict.append(midline.midline_area_dict)
