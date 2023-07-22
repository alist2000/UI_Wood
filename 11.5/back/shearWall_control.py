from back.beam_control import beam_control_joist


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
                    print(value, value2)
                    if value["post"]["start_center"] in [value2["post"]["start_center"], value2["coordinate"][0],
                                                         value2["post"]["end_center"], value2["coordinate"][1]] or \
                            value["coordinate"][0] in [value2["post"]["start_center"], value2["coordinate"][0],
                                                       value2["post"]["end_center"], value2["coordinate"][1]]:
                        value["shearWall_intersection"].append(
                            {"shearWall_label": value2["label"],
                             "post_label": value2["post"]["label_start"],
                             "coordinate": value["post"]["start_center"]}
                        )
                    elif value["post"]["end_center"] in [value2["post"]["start_center"], value2["coordinate"][0],
                                                         value2["post"]["end_center"], value2["coordinate"][1]] or \
                            value["coordinate"][1] in [value2["post"]["start_center"], value2["coordinate"][0],
                                                       value2["post"]["end_center"], value2["coordinate"][1]]:
                        value["shearWall_intersection"].append(
                            {"shearWall_label": value2["label"],
                             "post_label": value2["post"]["label_end"],
                             "coordinate": value["post"]["end_center"]}
                        )


class shearWall_control:
    def __init__(self, shearWall, joist, beam):
        self.shearWall = shearWall
        self.joist = joist
        self.beam = beam
        beam_control_joist(self.shearWall, self.joist)
        BeamOnShearWall(self.beam, self.shearWall)
        ShearWallPostIntersection(self.shearWall)
