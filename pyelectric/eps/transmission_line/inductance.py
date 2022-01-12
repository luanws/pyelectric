import math
from typing import List, Tuple


class Cable:
    radius: float
    position: Tuple[float, float]

    def __init__(self, radius: float, position: Tuple[float, float]):
        self.radius = radius
        self.position = position


def distance_between_cables(cable1: Cable, cable2: Cable) -> float:
    x1, y1 = cable1.position
    x2, y2 = cable2.position
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def geometric_mean_of_cable_distances(cables_phase_x: List[Cable], cables_phase_y: List[Cable]) -> float:
    distance: float = 1
    for cable_x in cables_phase_x:
        for cable_y in cables_phase_y:
            d = distance_between_cables(cable_x, cable_y)
            distance *= d if d > 0 else cable_x.radius*math.exp(-1/4)
    n = len(cables_phase_x) * len(cables_phase_y)
    distance = distance**(1/n)
    return distance


def calc_inductance(cables_phase_x: List[Cable], cables_phase_y: List[Cable]) -> float:
    Dm = geometric_mean_of_cable_distances(cables_phase_x, cables_phase_y)
    Dsx = geometric_mean_of_cable_distances(cables_phase_x, cables_phase_x)
    Dsy = geometric_mean_of_cable_distances(cables_phase_y, cables_phase_y)

    Lx = 2e-7*math.log(Dm/Dsx)
    Ly = 2e-7*math.log(Dm/Dsy)
    L = Lx + Ly
    return L
