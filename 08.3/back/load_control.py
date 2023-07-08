class load_joist_on_beam:
    def __init__(self, joistLabel, joistLoad, intersection_range_joist_beam, tributary_depth_joist_beam, beamDirection,
                 beamJoistLoad):
        self.joistLabel = joistLabel
        self.joistLoad = joistLoad
        self.intersection_range_joist_beam = intersection_range_joist_beam
        self.tributary_depth_joist_beam = tributary_depth_joist_beam
        self.beamDirection = beamDirection
        self.beamJoistLoad = beamJoistLoad

        total_area_load = self.joistLoad["total_area"]
        self.total_area_to_line(total_area_load)
        custom_area_load = self.joistLoad["custom_area"]
        self.custom_area_to_line(custom_area_load)

    def total_area_to_line(self, loads):
        for load in loads:
            load_mag = load["magnitude"]
            Type = load["type"]
            tributary_depth = abs(self.tributary_depth_joist_beam[1] - self.tributary_depth_joist_beam[0])

            # convert area load to line load
            magnitude = load_mag * tributary_depth
            start = min(self.intersection_range_joist_beam[0], self.intersection_range_joist_beam[1])
            end = max(self.intersection_range_joist_beam[0], self.intersection_range_joist_beam[1])
            self.beamJoistLoad.append(
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
                magnitude = load_mag * tributary_depth
                start = min(intersection_range[0], intersection_range[1])
                end = max(intersection_range[0], intersection_range[1])
                self.beamJoistLoad.append(
                    {"from": self.joistLabel, "type": Type, "magnitude": magnitude, "start": start, "end": end})


def range_intersection(range1, range2):
    range1 = set(range(int(range1[0]), int(range1[1]) + 1))
    range2 = set(range(int(range2[0]), int(range2[1]) + 1))
    intersection = list(range1 & range2)
    if intersection:
        intersection = (min(intersection), max(intersection))
    return intersection
