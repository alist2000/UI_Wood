import numpy as np
from sympy import Point, Line
from UI_Wood.stableVersion5.post_new import magnification_factor


def pointer_control(start, end, x, y):
    # Inclined beams
    range_x = (min(start[0], end[0]), max(start[0], end[0]))
    range_y = (min(start[1], end[1]), max(start[1], end[1]))
    point = (x, y)
    # Define two points
    p1, p2 = Point(start[0], start[1]), Point(end[0], end[1])

    # Define a line through the two points
    line = Line(p1, p2)
    distance = float(line.distance(point))

    # Define a tolerance value
    tolerance = magnification_factor / 3
    xRangeCondition = range_x[0] <= x <= range_x[1]
    if range_x[1] - range_x[0] < tolerance:
        xRangeCondition = True

    yRangeCondition = range_y[0] <= y <= range_y[1]
    if range_y[1] - range_y[0] < tolerance:
        yRangeCondition = True

    if distance <= tolerance and xRangeCondition and yRangeCondition:
        projection = line.projection(point)
        x_1, y_1 = float(projection.args[0]), float(projection.args[1])
        return True, x_1, y_1
    else:
        return False, "", ""

    # if (range_x[0] <= x <= range_x[1]) and (range_y[0] <= y <= range_y[1]):
    #     return True
    #
    # else:
    #     return False


def pointer_control2(range_x, range_y, x, y):
    if (range_x[0] <= x <= range_x[1]) and (range_y[0] <= y <= range_y[1]):
        return True


def set_point(start, end, x, y, support_type):
    beam_width = magnification_factor / 2
    if support_type == "post":
        point_range = pointer_control2(start, end, x, y)
    else:
        # Vertical and horizontal beams
        x1_main = min(start[0], end[0])
        x2_main = max(start[0], end[0])
        y1_main = min(start[1], end[1])
        y2_main = max(start[1], end[1])
        width = end[0] - start[0]
        height = end[1] - start[1]
        # horizontally beam
        if width == 0 or height == 0:
            if abs(width) > abs(height):
                range_x = (x1_main, x2_main)
                range_y = (start[1] - beam_width / 2, start[1] + beam_width / 2)
            else:
                range_x = (start[0] - beam_width / 2, start[0] + beam_width / 2)
                range_y = (y1_main, y2_main)
                # support type = beam
            point_range = pointer_control2(range_x, range_y, x, y)
            if point_range:
                width = range_x[1] - range_x[0]
                height = range_y[1] - range_y[0]
                center_x = ((range_x[1] - range_x[0]) / 2) + range_x[0]
                center_y = ((range_y[1] - range_y[0]) / 2) + range_y[0]
                if abs(width) > abs(height):
                    # horizontal beam
                    return True, x, center_y
                else:
                    # vertical beam
                    return True, center_x, y
            else:
                return False, "", ""
        else:
            # Inclined beams
            point_range, x_output, y_output = pointer_control(start, end, x, y)
    if point_range:
        range_x = start
        range_y = end
        center_x = ((range_x[1] - range_x[0]) / 2) + range_x[0]
        center_y = ((range_y[1] - range_y[0]) / 2) + range_y[0]
        if support_type == "post":
            return True, center_x, center_y
        else:
            # support type = beam
            return True, x_output, y_output

            # width = range_x[1] - range_x[0]
            # height = range_y[1] - range_y[0]
            # if abs(width) > abs(height):
            #     # horizontal beam
            #     return True, x, center_y
            # else:
            #     # vertical beam
            #     return True, center_x, y

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
        range_x = (x1_main, x2_main)

        range_y = (y1_main, y2_main)

        # if abs(width) > abs(height):
        #     range_x = (x1_main, x2_main)
        #     range_y = (y1 - beam_width / 2, y1 + beam_width / 2)
        # else:
        #     range_x = (x1 - beam_width / 2, x1 + beam_width / 2)
        #     range_y = (y1_main, y2_main)
        # beam_selectable_range.append([range_x, range_y])
        beam_selectable_range.append([start, end])
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
    x_start = min(i["position"] for i in vertical)
    x_end = max(i["position"] for i in vertical)
    y_start = min(i["position"] for i in horizontal)
    y_end = max(i["position"] for i in horizontal)
    horizontal_dict = {item["position"]: item["label"] for item in horizontal}
    vertical_dict = {item["position"]: item["label"] for item in vertical}

    if (x_start <= x <= x_end and y in horizontal_dict.keys()) and (
            y_start <= y <= y_end and x in vertical_dict.keys()):
        return True, "both"
    elif x_start <= x <= x_end and y in horizontal_dict.keys():
        return True, "E-W"

    # point is on vertical grid
    elif y_start <= y <= y_end and x in vertical_dict.keys():
        return True, "N-S"
    else:
        return False, ""


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


def range_post_shearWall(post_position, post_dimension):
    post_range = []
    for postItem in post_position.values():
        post = postItem["post"]["start_center"]
        range_x = (post[0] - post_dimension, post[0] + post_dimension)
        range_y = (post[1] - post_dimension, post[1] + post_dimension)

        post2 = postItem["post"]["end_center"]
        range2_x = (post2[0] - post_dimension, post2[0] + post_dimension)
        range2_y = (post2[1] - post_dimension, post2[1] + post_dimension)

        post_range.append([range_x, range_y])
        post_range.append([range2_x, range2_y])
    return post_range
