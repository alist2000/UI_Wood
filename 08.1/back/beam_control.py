class beam_control:
    def __init__(self, beam, post_position, shearWall_post_position):
        self.beam = beam
        self.post_position = post_position
        self.shearWall_post_position = shearWall_post_position

        self.add_length()
        self.add_direction()

    def add_length(self):
        for beamItem, beamProp in self.beam.items():
            start = beamProp["coordinate"][0]
            end = beamProp["coordinate"][1]
            l = self.length(start, end)
            self.beam[beamItem]["length"] = l
        print(self.beam)

    def add_direction(self):
        for beamItem, beamProp in self.beam.items():
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
        print(self.beam)

    @staticmethod
    def length(start, end):
        x1 = start[0]
        x2 = end[0]
        y1 = start[1]
        y2 = end[1]
        l = (((y2 - y1) ** 2) + ((x2 - x1) ** 2)) ** 0.5
        return round(l, 2)


Beam = {"beamItem1": {"label": "B1", "coordinate": [(0, 0), (4, 3)]},
        "beamItem2": {"label": "B2", "coordinate": [(0, 0), (10, 20)]}}
beam_control(Beam, "", "")
