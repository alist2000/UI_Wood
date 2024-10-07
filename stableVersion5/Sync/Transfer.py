import copy
import math
import sqlite3
from UI_Wood.stableVersion5.path import PathHandler, shearWallInputPath, shearWallOutputPath
from UI_Wood.stableVersion5.back.load_control import range_intersection
from UI_Wood.stableVersion5.post_new import magnification_factor


class Transfer:
    def __init__(self):
        self.transferListShearWall = []
        self.transferListStudWall = []
        self.transferListPost = []

    def StackControl(self, top, bottom, story, name="studWall"):
        if top:
            for item in top:
                coordinateTop = item["coordinate"]
                stack = False
                for itemBottom in bottom:
                    coordinateBottom = itemBottom["coordinate"]
                    if coordinateBottom == coordinateTop:
                        stack = True
                        break
                if not stack:
                    item["transfer_to_story"] = story
                    if name == "studWall":
                        self.transferListStudWall.append(item)
                    elif name == "post":
                        self.transferListPost.append(item)
                    else:
                        self.transferListShearWall.append(item)

    def TransferShear(self, top, bottom, story):
        for itemBottom in bottom:
            itemBottom["pe_abv"] = 0
            itemBottom["v_abv"] = 0
        transferToList = []
        if top:
            for shearWall in top:
                coordinateTop = shearWall["coordinate"]
                midPointX = (coordinateTop[0][0] + coordinateTop[1][0]) / 2
                midPointY = (coordinateTop[0][1] + coordinateTop[1][1]) / 2
                lineTop = shearWall["line_label"]
                shearTo = 0
                sameLine = []
                if shearWall in self.transferListShearWall:
                    # manual
                    if shearWall.get("transfer_to"):
                        for item in shearWall["transfer_to"]:
                            label = item["label"]
                            for itemBottom in bottom:
                                labelBottom = itemBottom["label"]
                                if labelBottom == label:
                                    if item.get("pe"):
                                        itemBottom["pe_abv"] += shearWall["pe_initial"]

                                    # itemBottom["pe_abv"] += shearWall["pe_initial"] * item["percent"] / 100
                                    itemBottom["v_abv"] += shearWall["v_design"] * item["percent"] / 100
                                    break
                            print("Done")
                    else:  # Auto (Developing)

                        for itemBottom in bottom:
                            coordinateBottom = itemBottom["coordinate"]
                            midPointXBottom = (coordinateBottom[0][0] + coordinateBottom[1][0]) / 2
                            midPointYBottom = (coordinateBottom[0][1] + coordinateBottom[1][1]) / 2
                            lineBottom = itemBottom["line_label"]
                            if lineBottom == lineTop:
                                sameLine.append(itemBottom)
                                pass  # DEVELOPING
                else:  # STACK
                    for itemBottom in bottom:
                        label = itemBottom["label"]
                        coordinateBottom = itemBottom["coordinate"]
                        if coordinateBottom == coordinateTop:
                            if itemBottom.get("pe_abv"):
                                itemBottom["pe_abv"] += shearWall["pe_initial"]
                                itemBottom["v_abv"] += shearWall["v_design"]
                            else:
                                itemBottom["pe_abv"] = shearWall["pe_initial"]
                                itemBottom["v_abv"] = shearWall["v_design"]

                            break

        for itemBottom in bottom:
            itemBottom["v_abv"] += itemBottom["extra_shear"]
            label = itemBottom["label"]
            dataBasePath = PathHandler(shearWallInputPath)
            conn = sqlite3.connect(dataBasePath)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE WallTable SET v_abv = ?, pe_abv = ? WHERE Wall_Label = ? AND Story = ?", (
                    itemBottom["v_abv"], itemBottom["pe_abv"], label[2:], story)
            )
            conn.commit()
            conn.close()

    def TransferOtherLoads(self, top, beams, aboveHeight, itemName="shearWall", story=None):
        if top:
            if itemName == "shearWall":
                transferList = self.transferListShearWall
            else:
                transferList = self.transferListStudWall
            for shearWall in top:
                if shearWall in transferList:
                    coordinateTop = shearWall["coordinate"]
                    direction = shearWall["direction"]
                    if direction == "N-S":
                        constantIndex = 0
                        constantCoord = coordinateTop[0][constantIndex]
                        swRange = (coordinateTop[0][1], coordinateTop[1][1])
                    else:
                        constantIndex = 1
                        constantCoord = coordinateTop[0][constantIndex]
                        swRange = (coordinateTop[0][0], coordinateTop[1][0])
                    swStart = min(swRange)
                    swEnd = max(swRange)
                    for beam in beams:
                        coordinateBeam = beam["coordinate"]
                        beamDirection = beam["direction"]
                        if beamDirection == "N-S":
                            constantIndexBeam = 0
                            constantCoordBeam = coordinateBeam[0][constantIndexBeam]
                            beamRange = (coordinateBeam[0][1], coordinateBeam[1][1])
                            beamStartMain = coordinateBeam[0][1]

                        else:
                            constantIndexBeam = 1
                            constantCoordBeam = coordinateBeam[0][constantIndexBeam]
                            beamRange = (coordinateBeam[0][0], coordinateBeam[1][0])
                            beamStartMain = coordinateBeam[0][0]

                        beamStart = min(beamRange)
                        beamEnd = max(beamRange)
                        if beamStart == coordinateBeam[0][constantIndexBeam - 1]:
                            distanceValue = abs(beamStart - swStart)
                        else:
                            distanceValue = abs(beamEnd - swEnd)
                        if direction == beamDirection and constantCoordBeam == constantCoord:
                            intersection = range_intersection(swRange, beamRange)
                            print("beam Range", beamRange)
                            print("shearWall Range", swRange)
                            if intersection and beamStart <= swStart and beamEnd >= swEnd:
                                if beam.get("transfer_item"):
                                    beam["transfer_item"].append({"item": itemName, "label": shearWall["label"]})
                                else:
                                    beam["transfer_item"] = [{"item": itemName, "label": shearWall["label"]}]
                                # Load Map
                                loadMapBottom = beam["load"]["joist_load"]["load_map"]
                                loadMapTop = copy.deepcopy(shearWall["load"]["joist_load"]["load_map"])
                                editedLoadMapTop = []
                                for load in loadMapTop:
                                    load["Transferred"] = True
                                    editedLoadMapTop.append(load)

                                loadMapBottom.extend(loadMapTop)
                                beam["load"]["joist_load"]["load_map"] = loadMapBottom

                                # Line Load
                                lineLoadBottom = beam["load"]["line"]
                                lineLoadTop = copy.deepcopy(shearWall["load"]["line"])
                                editedLineLoadTop = []
                                for load in lineLoadTop:
                                    load["distance"] = load["distance"] + distanceValue
                                    load["Transferred"] = True
                                    editedLineLoadTop.append(load)

                                lineLoadBottom.extend(editedLineLoadTop)
                                beam["load"]["line"] = lineLoadBottom

                                # SELF WEIGHT
                                if shearWall["interior_exterior"] == "exterior":
                                    deadLoad = 0.02  # ksf
                                else:
                                    deadLoad = 0.01  # ksf

                                beam["load"]["joist_load"]["load_map"].append(
                                    {'from': shearWall["label"], 'label': 'Self Weight',
                                     'load': [{'type': 'Dead', 'magnitude': deadLoad * aboveHeight}], 'start': swStart,
                                     'end': swEnd, "Transferred": True})

                                if itemName == "shearWall" and story:
                                    dataBasePath = PathHandler(shearWallOutputPath)
                                    conn = sqlite3.connect(dataBasePath)
                                    cursor = conn.cursor()
                                    r = cursor.execute(
                                        "SELECT tesion_demand_left, comp_demand_left, tesion_demand_right, comp_demand_right FROM shearwalldesign WHERE Wall_Label = ? AND Story = ?",
                                        (
                                            shearWall["label"][2:], story)
                                    )
                                    pointLoads = r.fetchall()

                                    distance1 = abs(beamStartMain - swStart)
                                    distance2 = abs(beamStartMain - swEnd)

                                    # omega factor = 2.5
                                    pointset = [
                                        {"distance": distance1, "magnitude": -pointLoads[0][0] * 2.5, "type": "Seismic",
                                         "Transferred": True, "set": 1},
                                        {"distance": distance2, "magnitude": pointLoads[0][3] * 2.5, "type": "Seismic",
                                         "Transferred": True, "set": 1},
                                        {"distance": distance1, "magnitude": -pointLoads[0][1] * 2.5, "type": "Seismic",
                                         "Transferred": True, "set": 2},
                                        {"distance": distance2, "magnitude": pointLoads[0][2] * 2.5, "type": "Seismic",
                                         "Transferred": True, "set": 2}
                                    ]
                                    print(pointset)
                                    beam["Transferred"] = True
                                    beam["load"]["point"].extend(pointset)

                                    print("Point loads from top shear wall printed")

                                # beam["load"]["joist_load"]["load_map"].append(
                                #     {"distance": distanceValue, "length": shearWall["length"],
                                #      "magnitude": deadLoad * aboveHeight,
                                #      "type": "Dead", "Transferred": True})

                                print("SW set on this beam: ", beam)
                            break

    def TransferPointLoads(self, top, beams):
        if top:
            transferList = self.transferListPost
            for post in top:
                if post in transferList and post["load_transfer"]:
                    coordinateTop = post["coordinate"]
                    for beam in beams:
                        coordinateBeam = beam["coordinate"]
                        beamDirection = beam["direction"]
                        if beamDirection == "N-S":
                            constantIndexBeam = 0
                            constantCoordBeam = coordinateBeam[0][constantIndexBeam]
                            beamRange = (coordinateBeam[0][1], coordinateBeam[1][1])
                            beamStartMain = coordinateBeam[0][1]

                        else:
                            constantIndexBeam = 1
                            constantCoordBeam = coordinateBeam[0][constantIndexBeam]
                            beamRange = (coordinateBeam[0][0], coordinateBeam[1][0])
                            beamStartMain = coordinateBeam[0][0]

                        beamStart = min(beamRange)
                        beamEnd = max(beamRange)
                        dist = abs(coordinateTop[constantIndexBeam] - constantCoordBeam)
                        if dist <= magnification_factor / 12 and beamStart <= coordinateTop[
                            constantIndexBeam - 1] <= beamEnd:  # distance till 1 inch is acceptable
                            if beam.get("transfer_item"):
                                beam["transfer_item"].append({"item": "post", "label": post["label"]})
                            else:
                                beam["transfer_item"] = [{"item": "post", "label": post["label"]}]

                            print("this post is transferred", post["label"], "on this beam", beam["label"])
                            pointLoads = post["load"]["point"]
                            reactionLoads = post["load"]["reaction"]
                            for loadType in [pointLoads, reactionLoads]:
                                for load in loadType:
                                    beam['load']['point'].append(
                                        {"distance": abs(beamStartMain - coordinateTop[constantIndexBeam - 1]),
                                         "magnitude": load["magnitude"],
                                         "type": load["type"],
                                         "Transferred": True}
                                    )
                            # beam["load"]["point"].extend(
                            #
                            # )

    def DeleteTransferredItems(self, beams):
        for beam in beams:
            if beam.get("transfer_item"):
                beam["transfer_item"] = []

    @staticmethod
    def get_data_after_run(shearWalls, story):
        dataBasePath = PathHandler(shearWallOutputPath)
        conn = sqlite3.connect(dataBasePath)
        cursor = conn.cursor()
        for shearWall in shearWalls:
            label = shearWall["label"]
            r = cursor.execute("SELECT Vdesign, Initial_PE FROM shearwalldesign WHERE Wall_Label = ? AND Story = ?", (
                label[2:], story)
                               )
            data = r.fetchone()
            shearWall["v_design"] = data[0]
            shearWall["pe_initial"] = data[1]
        conn.commit()
        conn.close()


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


class DeleteTransferred:
    def __init__(self, item):
        self.item = item
        self.delete()

    def delete(self):
        for story in self.item:
            for item in story:
                pointLoad = item["load"]["point"]
                lineLoad = item["load"]["line"]
                loadMap = item["load"]["joist_load"]["load_map"]
                newPointLoad = []
                newLineLoad = []
                newLoadMap = []
                for point in pointLoad:
                    if not point.get("Transferred"):
                        newPointLoad.append(point)
                for line in lineLoad:
                    if not line.get("Transferred"):
                        newLineLoad.append(line)
                for load in loadMap:
                    if not load.get("Transferred"):
                        newLoadMap.append(load)
                item["load"]["point"] = newPointLoad
                item["load"]["line"] = newLineLoad
                item["load"]["joist_load"]["load_map"] = newLoadMap
