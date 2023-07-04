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
                        if shear_wall_prop["post"]["label_start"] == shear_wall_label_beam or shear_wall_prop["post"]["label_end"] == shear_wall_label_beam:
                            shear_wall_prop["beam"].append(
                                {"beam_label": beam_prop["label"], "post_label": shear_wall_label_beam,
                                 "beam_coordinate": beam_prop["coordinate"]})


class shearWall_control:
    def __init__(self, shearWall, joist, beam):
        self.shearWall = shearWall
        self.joist = joist
        self.beam = beam
        beam_control_joist(self.shearWall, self.joist)
        BeamOnShearWall(self.beam, self.shearWall)
