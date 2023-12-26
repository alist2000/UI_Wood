import sys
import numpy as np

sys.path.append(r"D:\git\Wood\UI_Wood\11.5")
from UI_Wood.stableVersion4.post_new import magnification_factor
from UI_Wood.stableVersion4.back.load_control import distance


class reaction_types:
    def __init__(self, reactions):
        # self.dead, self.live, self.live_roof, self.snow, self.seismic = reactions
        # self.loads = [self.dead, self.live, self.live_roof, self.snow, self.seismic]
        # self.load_names = ["Dead", "Live", "Live Roof", "Snow", "Seismic"]
        self.loc = list(reactions.keys())
        self.loads = list(reactions.values())
        self.load_names = ["Dead", "Live", "Live Roof", "Seismic", "Snow"]


class Control_reaction(reaction_types):
    def __init__(self, reactions, beam, reaction_list):
        super(Control_reaction, self).__init__(reactions)
        self.reaction_list = reaction_list
        self.selected_beam = beam
        self.coordinate_beam = coordinate_beam = beam["coordinate"]
        direction = beam["direction"]
        if direction == "N-S":
            self.direction_index = 1
            self.constant_index = 0
            self.start_coordinate = min(coordinate_beam[0][self.direction_index],
                                        coordinate_beam[1][self.direction_index])

        elif direction == "E-W":
            self.direction_index = 0
            self.constant_index = 1
            self.start_coordinate = min(coordinate_beam[0][self.direction_index],
                                        coordinate_beam[1][self.direction_index])

        else:  # inclined
            self.direction_index = 2
            self.constant_index = 2
            one = coordinate_beam[0]
            two = coordinate_beam[1]
            if one[0] <= two[0]:
                self.start_coordinate_main = one
                self.start_coordinate = one[0]
            else:
                self.start_coordinate_main = two
                self.start_coordinate = two[0]

        # for i, load in enumerate(self.loads):
        for loc, load in reactions.items():
            self.control_every_reaction(loc, load)

        support = self.selected_beam["support"]
        for supportItem in support:
            if supportItem.get("reaction"):
                self.reaction_list.append(supportItem)

    def control_every_reaction(self, loc, load):
        reaction_distance = (float(loc) * magnification_factor) + self.start_coordinate
        support = self.selected_beam["support"]

        if self.direction_index == 1 or self.direction_index == 0:
            if self.direction_index == 1:
                reaction_coordinate = (
                    round(self.coordinate_beam[0][self.constant_index], 0), round(reaction_distance, 0))
            else:
                reaction_coordinate = (
                    round(reaction_distance, 0), round(self.coordinate_beam[0][self.constant_index], 0))

            for i, magnitude in enumerate(load):
                load_type = self.load_names[i]
                for supportItem in support:
                    if supportItem.get("reaction") is None:
                        supportItem["reaction"] = []
                    coordinate = tuple([round(i, 0) for i in supportItem["coordinate"]])
                    if coordinate == reaction_coordinate:
                        supportItem["reaction"].append({"magnitude": magnitude, "type": load_type})
        else:  # Inclined beam
            for i, magnitude in enumerate(load):
                load_type = self.load_names[i]
                for supportItem in support:
                    if supportItem.get("reaction") is None:
                        supportItem["reaction"] = []
                    coordinate = tuple([round(i, 0) for i in supportItem["coordinate"]])
                    SupportDist = distance(self.start_coordinate_main, coordinate) + self.start_coordinate
                    error = magnification_factor / 10
                    if abs(reaction_distance - SupportDist) <= error:
                        supportItem["reaction"].append({"magnitude": magnitude, "type": load_type})


class Reaction_On:
    def __init__(self, beams, posts, shearWalls, support):
        self.beams = beams
        self.posts = posts
        self.shearWalls = shearWalls
        self.support = support

    def do_beam(self):
        for beam in self.beams:
            beam["load"]["reaction"].clear()
        for supportItem in self.support:
            support_label = supportItem["label"]
            reaction = supportItem["reaction"]
            coordinate = supportItem["coordinate"]
            if "B" in support_label:
                Reaction_on_beam(self.beams, support_label, reaction, coordinate)

    def do_post(self):
        for post in list(self.posts.values())[0]:
            post["load"]["reaction"].clear()
        for shearWall in self.shearWalls:
            shearWall["load"]["reaction"].clear()
        for supportItem in self.support:
            support_label = supportItem["label"]
            reaction = supportItem["reaction"]
            coordinate = supportItem["coordinate"]
            support_type = supportItem["type"]

            if support_type == "post":
                Reaction_on_post(self.posts, support_label, reaction)
            elif "shearWall" in support_type:
                Reaction_on_shearWall_post(self.shearWalls, support_label, reaction, coordinate)


class Reaction_on_beam:
    def __init__(self, beams, support_label, reaction, coordinate):
        for beam in beams:
            if beam["label"] == support_label:
                beam["load"]["reaction"].append({
                    "start": coordinate,
                    "load": reaction
                })


class Reaction_on_post:
    def __init__(self, posts, support_label, reaction):
        for post in list(posts.values())[0]:
            if post["label"] == support_label:
                post["load"]["reaction"].extend(reaction
                                                )


class Reaction_on_shearWall_post:
    def __init__(self, shearWalls, support_label, reaction, coordinate):
        for shearWall in shearWalls:
            if shearWall["post"]["label_start"] == support_label or shearWall["post"]["label_end"] == support_label:
                shearWall["load"]["reaction"].append({
                    "start": coordinate,
                    "load": reaction
                })
