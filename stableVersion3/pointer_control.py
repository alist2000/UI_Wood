import numpy as np


def pointer_control(range_x, range_y, x, y):
    if (range_x[0] <= x <= range_x[1]) and (range_y[0] <= y <= range_y[1]):
        return True

    else:
        return False


def set_point(range_x, range_y, x, y, support_type):
    point_range = pointer_control(range_x, range_y, x, y)
    if point_range:
        center_x = ((range_x[1] - range_x[0]) / 2) + range_x[0]
        center_y = ((range_y[1] - range_y[0]) / 2) + range_y[0]
        if support_type == "post":
            return True, center_x, center_y
        else:
            # support type = beam
            width = range_x[1] - range_x[0]
            height = range_y[1] - range_y[0]
            if abs(width) > abs(height):
                # horizontal beam
                return True, x, center_y
            else:
                # vertical beam
                return True, center_x, y

    else:
        return False, "", ""


# # TEST
# print(pointer_control((0, 50), (375, 425), 25, 300))
# print(pointer_control((0, 50), (375, 425), 65, 380))
# print(pointer_control((0, 50), (375, 425), 65, 300))
# print(set_point((0, 50), (375, 425), 28, 402, "post"))
# print(set_point((0, 100), (375, 425), 28, 402, "beam"))
# print(set_point((0, 50), (375, 450), 28, 402, "beam"))
# print(set_point((25, 50), (375, 450), 28, 402, "beam"))
# print(set_point((10.4, 50), (300, 450), 28, 402, "beam"))
# print(set_point((10.4, 50), (300, 450), 5, 402, "beam"))
# print(set_point((10.4, 50), (300, 450), 5, 402, "post"))


def range_post(post_position, post_dimension):
    post_range = []
    for postItem in post_position.values():
        post = postItem["coordinate"]
        range_x = (post[0] - post_dimension, post[0] + post_dimension)
        range_y = (post[1] - post_dimension, post[1] + post_dimension)
        post_range.append([range_x, range_y])
    return post_range


def selectable_beam_range(beam_position, beam_width):
    beam_selectable_range = []
    for beamItem in beam_position.values():
        beam = beamItem["coordinate"]
        start = beam[0]
        end = beam[1]
        x1 = start[0]
        y1 = start[1]
        x2 = end[0]
        y2 = end[1]
        x1_main = min(x1, x2)
        x2_main = max(x1, x2)
        y1_main = min(y1, y2)
        y2_main = max(y1, y2)
        width = x2 - x1
        height = y2 - y1
        # horizontally beam
        if abs(width) > abs(height):
            range_x = (x1_main, x2_main)
            range_y = (y1 - beam_width / 2, y1 + beam_width / 2)
        else:
            range_x = (x1 - beam_width / 2, x1 + beam_width / 2)
            range_y = (y1_main, y2_main)
        beam_selectable_range.append([range_x, range_y])
    return beam_selectable_range


def control_post_range(post_range, x, y):
    for item in post_range:
        status, x_final, y_final = set_point(item[0], item[1], x, y, "post")
        if status:
            return status, x_final, y_final

    return False, "", ""


def control_selectable_beam_range(beam_range, x, y):
    # print(beam_range)
    # print(x, y)
    for item in beam_range:
        status, x_final, y_final = set_point(item[0], item[1], x, y, "beam")
        if status:
            return status, x_final, y_final

    return False, "", ""


def beam_end_point(start, end):
    x1 = start[0]
    y1 = start[1]
    x2 = end[0]
    y2 = end[1]
    width = x2 - x1
    height = y2 - y1
    if abs(width) > abs(height):
        # horizontal beam --> y: constant
        x_end = x2
        y_end = y1
    else:
        # vertical beam --> x: constant
        x_end = x1
        y_end = y2
    return x_end, y_end


def pointer_control_shearWall(x, y, gridProp):
    vertical = gridProp["vertical"]
    print(vertical)
    horizontal = gridProp["horizontal"]
    print(horizontal)
    x_start = vertical[0]["position"]
    x_end = vertical[-1]["position"]
    y_start = horizontal[0]["position"]
    y_end = horizontal[-1]["position"]
    horizontal_dict = {item["position"]: item["label"] for item in horizontal}
    vertical_dict = {item["position"]: item["label"] for item in vertical}

    if (x_start <= x <= x_end and y in horizontal_dict.keys()) and (
            y_start <= y <= y_end and x in vertical_dict.keys()):
        line = [vertical_dict[x], horizontal_dict[y]]

        if (y == y_start or y == y_end) and (x == x_start or x == x_end):
            int_ext = "exterior"
        else:
            int_ext = "interior"
        return True, "both", int_ext, line
    elif x_start <= x <= x_end and y in horizontal_dict.keys():
        line = horizontal_dict[y]
        if y == y_start or y == y_end:
            int_ext = "exterior"
        else:
            int_ext = "interior"
        return True, "E-W", int_ext, line

    # point is on vertical grid
    elif y_start <= y <= y_end and x in vertical_dict.keys():
        line = vertical_dict[x]
        if x == x_start or x == x_end:
            int_ext = "exterior"
        else:
            int_ext = "interior"
        return True, "N-S", int_ext, line
    else:
        return False, "", "", ""


def pointer_control_studWall(start, end, gridProp):
    x1, y1 = start
    x2, y2 = end
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    vertical = gridProp["vertical"]
    horizontal = gridProp["horizontal"]
    x_start = vertical[0]["position"]
    x_end = vertical[-1]["position"]
    y_start = horizontal[0]["position"]
    y_end = horizontal[-1]["position"]
    if width > height:
        direction = "E-W"
        if (y1 == y_start or y1 == y_end) and (y2 == y_start or y2 == y_end):
            int_ext = "exterior"
        else:

            int_ext = "interior"

    else:
        direction = "N-S"
        if (x1 == x_start or x1 == x_end) and (x2 == x_start or x2 == x_end):
            int_ext = "exterior"
        else:
            int_ext = "interior"

    return direction, int_ext
