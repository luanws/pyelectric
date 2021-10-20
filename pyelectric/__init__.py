import math
from typing import Tuple


def cutoff_frequencies(R: float, L: float, C: float) -> Tuple[float, float]:
    f1 = (1/(2*math.pi))*(-(R/(2*L)) + (1/2)*math.sqrt((R/L)**2 + (4/L*C)))
    f2 = (1/(2*math.pi))*((R/(2*L)) + (1/2)*math.sqrt((R/L)**2 + (4/L*C)))
    return f1, f2


def print_result(*args, **kwargs):
    args = [f'\33[32m{a}' for a in args]
    print(*args, **kwargs)
