import copy
from typing import List, Dict, Any


class ShearWall:
    def __init__(self, name, left_top=None, right_bottom=None, pd_left=0, pd_right=0, pl_left=0, pl_right=0, pe_left=0,
                 pe_right=0, ps_left=0, ps_right=0):
        self.name = name
        self.left_top = left_top
        self.right_bottom = right_bottom
        self.pd_left = pd_left
        self.pd_right = pd_right
        self.pl_left = pl_left
        self.pl_right = pl_right
        self.pe_left = pe_left
        self.pe_right = pe_right
        self.ps_left = ps_left
        self.ps_right = ps_right


def distribute_loads(shear_walls: List[ShearWall]) -> List[ShearWall]:
    sw_dict = {sw.name: sw for sw in shear_walls}
    processed_connections = set()

    for sw in shear_walls:
        # Check left (top) connection
        if sw.left_top and (sw.name, sw.left_top) not in processed_connections:
            connected_sw = sw_dict.get(sw.left_top)
            if connected_sw:
                if connected_sw.right_bottom == sw.name:
                    for attr in ['pd', 'pl', 'pe']:
                        total_load = getattr(sw, f"{attr}_left") + getattr(connected_sw, f"{attr}_right")
                        setattr(sw, f"{attr}_left", total_load)
                        setattr(connected_sw, f"{attr}_right", total_load)
                elif connected_sw.left_top == sw.name:
                    for attr in ['pd', 'pl', 'pe']:
                        total_load = getattr(sw, f"{attr}_left") + getattr(connected_sw, f"{attr}_left")
                        setattr(sw, f"{attr}_left", total_load)
                        setattr(connected_sw, f"{attr}_left", total_load)
                processed_connections.add((sw.name, sw.left_top))
                processed_connections.add((sw.left_top, sw.name))

        # Check right (bottom) connection
        if sw.right_bottom and (sw.name, sw.right_bottom) not in processed_connections:
            connected_sw = sw_dict.get(sw.right_bottom)
            if connected_sw:
                if connected_sw.left_top == sw.name:
                    for attr in ['pd', 'pl', 'pe']:
                        total_load = getattr(sw, f"{attr}_right") + getattr(connected_sw, f"{attr}_left")
                        setattr(sw, f"{attr}_right", total_load)
                        setattr(connected_sw, f"{attr}_left", total_load)
                elif connected_sw.right_bottom == sw.name:
                    for attr in ['pd', 'pl', 'pe']:
                        total_load = getattr(sw, f"{attr}_right") + getattr(connected_sw, f"{attr}_right")
                        setattr(sw, f"{attr}_right", total_load)
                        setattr(connected_sw, f"{attr}_right", total_load)
                processed_connections.add((sw.name, sw.right_bottom))
                processed_connections.add((sw.right_bottom, sw.name))

    return shear_walls
