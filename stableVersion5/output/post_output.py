from abc import ABC, abstractmethod
import sys

from UI_Wood.stableVersion5.post_new import magnification_factor
from UI_Wood.stableVersion5.output.postSql import PostSQL, WritePostInputSQL


class post_output:
    def __init__(self, posts, height, topPosts, story):
        self.posts = posts
        self.height = height  # should be checked.
        self.story = story
        self.postProperties = []
        pointLoadCalculator = PointLoadCalculator()
        reactionLoadCalculator = ReactionLoadCalculator()
        if topPosts:
            LoadRoot(posts, topPosts, pointLoadCalculator, reactionLoadCalculator)

        self.create_dict()

    def create_dict(self):
        # for i, postTab in self.posts:
        for Post in self.posts:
            loadSet = Post["load"]["point"] + Post["load"]["reaction"]
            loadControl = ControlLoadType(loadSet)
            properties = {
                "label": Post["label"],
                "coordinate": (
                    Post["coordinate"][0] / magnification_factor, Post["coordinate"][1] / magnification_factor),
                "story": self.story + 1,
                "width": float(Post["wall_width"][0]),
                "height": self.height,
                "load": loadControl.load_list
            }
            self.postProperties.append(properties)

    def create_dict2(self):
        postId = 1
        for i, postTab in enumerate(self.posts):
            for Post in list(postTab.values())[0]:
                loadSet = Post["load"]["point"] + Post["load"]["reaction"]
                loadControl = ControlLoadType(loadSet)
                properties = {
                    "label": Post["label"],
                    "coordinate": (
                        Post["coordinate"][0] / magnification_factor, Post["coordinate"][1] / magnification_factor),
                    "story": i + 1,
                    "width": float(Post["wall_width"][0]),
                    "height": self.height[i],
                    "load": loadControl.load_list
                }
                self.postProperties.append(properties)
                WritePostInputSQL(properties, postId, self.inputDB)
                postId += 1


class LoadCalculator(ABC):
    # Define the interface
    @abstractmethod
    def calculate(self, post, Post_top):
        pass


class PointLoadCalculator(LoadCalculator):
    # Strategy #1: Calculate point load
    def calculate(self, post, Post_top):
        return Post_top["load"]["point"] + post["load"]["point"]


class ReactionLoadCalculator(LoadCalculator):
    # Strategy #2: Calculate reaction load
    def calculate(self, post, Post_top):
        return Post_top["load"]["reaction"] + post["load"]["reaction"]


# The `LoadRoot` class calculates point loads and reaction loads for posts in a hierarchical structure.
class LoadRoot:
    def __init__(self, posts, topPosts, point_load_calculator, reaction_load_calculator):
        self.posts = posts
        self.topPosts = topPosts
        self.point_load_calculator = point_load_calculator
        self.reaction_load_calculator = reaction_load_calculator
        self.calculate_loads()

    def calculate_loads(self):
        """
        The function calculates loads for each post based on their coordinates and the posts above them.
        """
        for i, Post in enumerate(self.posts):
            coordinate = Post["coordinate"]
            for Post_top in self.topPosts:
                if Post_top["coordinate"] == coordinate:
                    Post["load"]["point"] = self.point_load_calculator.calculate(Post, Post_top)
                    Post["load"]["reaction"] = self.reaction_load_calculator.calculate(Post, Post_top)
                    break


class ControlLoadType:
    def __init__(self, loadList):
        self.load_list = []
        if loadList:
            self.all_indexes2 = []
            self.all_indexes2.clear()
            type_list = [load_item['type'] for load_item in loadList]
            magnitude_list = [load_item['magnitude'] for load_item in loadList]
            checked_indexes = set()  # set for efficient searching

            num_type = len(type_list)  # calculating length once and reusing

            for i in range(num_type):
                if i not in checked_indexes:  # Control check
                    current_type = type_list[i]
                    index_list = [j for j in range(i, num_type) if type_list[j] == current_type]
                    checked_indexes.update(index_list)

                    self.all_indexes2.append(index_list)

            for Item in self.all_indexes2:
                load_mag = 0
                for i in Item:
                    load_mag += magnitude_list[i]
                self.load_list.append({
                    "type": type_list[i],
                    "magnitude": load_mag
                })
