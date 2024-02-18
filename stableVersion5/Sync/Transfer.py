import math
import sqlite3
from UI_Wood.stableVersion5.path import PathHandler, shearWallInputPath1, shearWallOutputPath1
from UI_Wood.stableVersion5.back.load_control import range_intersection


class Transfer:
    def __init__(self):
        self.transferListShearWall = []
        self.transferListStudWall = []

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
                                    itemBottom["pe_abv"] += shearWall["pe_initial"] * item["percent"] / 100
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
            label = itemBottom["label"]
            dataBasePath = PathHandler(shearWallInputPath1)
            conn = sqlite3.connect(dataBasePath)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE WallTable SET v_abv = ?, pe_abv = ? WHERE Wall_Label = ? AND Story = ?", (
                    itemBottom["v_abv"], itemBottom["pe_abv"], label[2:], story)
            )
            conn.commit()
            conn.close()

    def TransferOtherLoads(self, top, beams):
        if top:
            for shearWall in top:
                if shearWall in self.transferListShearWall:
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

                    for beam in beams:
                        coordinateBeam = beam["coordinate"]
                        beamDirection = beam["direction"]
                        if beamDirection == "N-S":
                            constantCoordBeam = coordinateBeam[0][constantIndex]
                            beamRange = (coordinateTop[0][1], coordinateTop[1][1])

                        else:
                            constantCoordBeam = coordinateBeam[0][constantIndex]
                            beamRange = (coordinateTop[0][0], coordinateTop[1][0])

                        if direction == beamDirection and constantCoordBeam == constantCoord:
                            intersection = range_intersection(swRange, beamRange)
                            if intersection:
                                print("SW set on this beam: ", beam)
                            break

    @staticmethod
    def get_data_after_run(shearWalls, story):
        dataBasePath = PathHandler(shearWallOutputPath1)
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
