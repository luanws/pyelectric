import math
from functools import reduce
from typing import Any, Dict, List, Tuple, Union


class Cable:
    radius: float
    position: Tuple[float, float]

    def __init__(self, radius: float, position: Tuple[float, float]):
        self.radius = radius
        self.position = position


def distance_between_cables(cable1: Cable, cable2: Cable) -> float:
    x1, y1 = cable1.position
    x2, y2 = cable2.position
    d = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return d if d > 0 else cable1.radius*math.exp(-1/4)


def multiply_all_elements_from_list(list: List[float]) -> float:
    return reduce(lambda x, y: x*y, list)


def list_of_lists_to_list(list_of_list: List[List[Any]]) -> List[Any]:
    return [item for sublist in list_of_list for item in sublist]


def geometric_mean_of_cable_distances(cables_bundles: List[List[Cable]]) -> float:
    distance: float = 1
    for i, cables_bundle in enumerate(cables_bundles):
        compare_cables_bundles = cables_bundles[i+1:]
        compare_cables = list_of_lists_to_list(compare_cables_bundles)
        for cable1 in cables_bundle:
            for cable2 in compare_cables:
                distance *= distance_between_cables(cable1, cable2)
    n = reduce(lambda x, y: x*y, [len(c) for c in cables_bundles])
    distance = distance**(1/n)
    return distance


def to_cables(cables: List[Union[Cable, Dict[str, Any]]]) -> List[Cable]:
    cables_list: List[Cable] = []
    for cable in cables:
        if isinstance(cable, Cable):
            cables_list.append(cable)
        else:
            cables_list.append(Cable(**cable))
    return cables_list


def calc_inductance(*conductors_bundle: List[Union[Cable, Dict[str, Any]]]) -> float:
    cables_bundles: List[List[Cable]] = [
        to_cables(c) for c in conductors_bundle]
    Dm = geometric_mean_of_cable_distances(cables_bundles)
    Ds_list = [geometric_mean_of_cable_distances(
        [c, c]) for c in cables_bundles]

    L_list = [2e-7*math.log(Dm/Ds) for Ds in Ds_list]
    L = sum(L_list)
    return L
