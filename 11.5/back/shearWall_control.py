import sys

sys.path.append(r"D:\git\Wood\UI_Wood\11.5")
from back.beam_control import beam_control_joist
from back.load_control import range_intersection

from post_new import magnification_factor


class BeamOnShearWall:
    def __init__(self, beam, shear_wall):
        shear_wall_values = shear_wall.values()
        for shear_wall_Prop in shear_wall_values:
            shear_wall_Prop["beam"] = []
        for beam_prop in beam.values():
            supports = beam_prop["support"]
            for support in supports:
                if support["type"] == "shearWall_post":
                    shear_wall_label_beam = support["label"]
                    for shear_wall_prop in shear_wall_values:
                        if shear_wall_prop["post"]["label_start"] == shear_wall_label_beam or shear_wall_prop["post"][
                            "label_end"] == shear_wall_label_beam:
                            shear_wall_prop["beam"].append(
                                {"beam_label": beam_prop["label"], "post_label": shear_wall_label_beam,
                                 "beam_coordinate": beam_prop["coordinate"]})


class ShearWallPostIntersection:
    def __init__(self, shear_wall):
        for item, value in shear_wall.items():
            value["shearWall_intersection"] = []
            for item2, value2 in shear_wall.items():
                if item != item2:
                    CheckIntersection(value, value2)


class shearWall_control:
    def __init__(self, shearWall, joist, beam):
        self.shearWall = shearWall
        self.joist = joist
        self.beam = beam
        beam_control_joist(self.shearWall, self.joist)
        BeamOnShearWall(self.beam, self.shearWall)
        ShearWallPostIntersection(self.shearWall)


# WORK ON START END AND COORDINATE OF INTERSECTION AND AREA AND SOMETHING LIKE THIS
class CheckIntersection:
    def __init__(self, shearWall1, shearWall12):
        self.shearWall1 = shearWall1
        self.shearWall2 = shearWall12
        range1_1, range1_2 = self.check_intersection(shearWall1, 1)
        range2_1, range2_2 = self.check_intersection(shearWall12, 2)
        post_coord_intersect = self.checkRangesFinal(range1_1, range1_2, range2_1, range2_2)
        if post_coord_intersect:
            shearWall1["shearWall_intersection"].append(
                {"shearWall_label": shearWall12["label"],
                 "coordinate": post_coord_intersect,
                 "line_label": shearWall12["line_label"]}
            )

    def checkRangesFinal(self, range1_1, range1_2, range2_1, range2_2):
        x1 = (range1_1[0][0] + range1_1[0][1]) / 2
        y1 = (range1_1[1][0] + range1_1[1][1]) / 2
        x2 = (range1_2[0][0] + range1_2[0][1]) / 2
        y2 = (range1_2[1][0] + range1_2[1][1]) / 2
        checkStart = self.check_ranges((range1_1, range2_1))
        checkStart2 = self.check_ranges((range1_1, range2_2))
        if checkStart or checkStart2:
            return x1, y1
        checkEnd = self.check_ranges((range1_2, range2_1))
        checkEnd2 = self.check_ranges((range1_2, range2_2))
        if checkEnd or checkEnd2:
            return x2, y2

        return None

    @staticmethod
    def check_intersection(shearWall, i):
        if shearWall["direction"] == "N-S":
            direction1_index = 1
            constant_index = 0
        else:
            direction1_index = 0
            constant_index = 1

        coord1 = shearWall["coordinate"][0][direction1_index]
        coord1_c = shearWall["coordinate"][0][constant_index]
        coord2 = shearWall["coordinate"][1][direction1_index]
        coord2_c = shearWall["coordinate"][1][constant_index]
        start = min(coord1, coord2)
        start_c = min(coord1_c, coord2_c)
        end = max(coord1, coord2)
        end_c = max(coord1_c, coord2_c)
        post_coord1 = shearWall["post"]["start_center"][direction1_index]
        post_coord2 = shearWall["post"]["end_center"][direction1_index]
        post_start = min(post_coord1, post_coord2)
        post_end = max(post_coord1, post_coord2)
        if direction1_index:  # 1
            x_range1 = ((start_c - magnification_factor / 2), (start_c + magnification_factor / 2))
            y_range1 = (start, start + 2 * abs(start - post_start))
            x_range2 = ((end_c - magnification_factor / 2), (end_c + magnification_factor / 2))
            y_range2 = (end - 2 * abs(end - post_end), end)
        else:  # 0
            y_range1 = ((start_c - magnification_factor / 2), (start_c + magnification_factor / 2))
            x_range1 = (start, start + 2 * abs(start - post_start))
            y_range2 = ((end_c - magnification_factor / 2), (end_c + magnification_factor / 2))
            x_range2 = (end - 2 * abs(end - post_end), end)
        return (x_range1, y_range1), (x_range2, y_range2)

    @staticmethod
    def check_ranges(ranges):
        x_range1 = ranges[0][0]
        x_range2 = ranges[1][0]
        y_range1 = ranges[0][1]
        y_range2 = ranges[1][1]
        x_intersection = range_intersection(x_range1, x_range2)
        y_intersection = range_intersection(y_range1, y_range2)
        if x_intersection and y_intersection:
            return True
