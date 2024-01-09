from back.beam_control import beam_control
from back.joist_control import joist_support_control
from back.shearWall_control import shearWall_control
from back.midline_control import joist_in_midline
from back.load_control import load_on_joist
from UI_Wood.stableVersion4.back.midline_control import EditGrid


class receiver:
    def __init__(self, grid, post, beam, joist, shearWall, studWall, load):
        self.grid = grid
        self.post = post
        self.beam = beam
        self.joist = joist
        self.shearWall = shearWall
        self.studWall = studWall
        self.load = load

        # SUPPORT TYPE 1: POST
        post_position = set()
        shearWall_post_position = set()

        # SUPPORT TYPE 2: BEAM TO BEAM CONNECTION
        load_on_joist(joist, load)
        self.beam_properties = beam_control(beam, post, shearWall, joist)
        self.joist_properties = joist_support_control(joist, beam, shearWall, studWall)
        self.shearWall_properties = shearWall_control(shearWall, joist, beam, grid)
        self.studWall_properties = shearWall_control(studWall, joist, beam, item="studWall")
        gridInstance = EditGrid(shearWall, grid)
        editedGrid = gridInstance.output()
        self.midline = joist_in_midline(joist, editedGrid)

    # def beam_control(self):
    #     beam = self.beam
    #     beam["direction"] = None
    #     beam["support"] = []
    #     beam["joist"] = []
    #
    #     # FOR EVERY SUPPORT
    #     support_label = None
    #     support_type = None
    #     support_pos = (None, None)
    #     support_item = {"label": support_label, "type": support_type, "position": support_pos}
    #     beam["support"].append(support_item)
