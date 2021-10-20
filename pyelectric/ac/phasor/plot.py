from typing import List, Union

import numpy as np
from matplotlib import pyplot as plt

from . import Phasor


def plot_complex(zs: Union[complex, List[complex]], color: str = None):
    if isinstance(zs, complex):
        zs = [zs]
    vectors = np.array([[z.real, z.imag] for z in zs])
    origin = np.zeros(vectors.T.shape)
    plt.quiver(*origin, vectors[:, 0], vectors[:, 1],
               color=color, angles='xy', scale_units='xy', scale=1)

    limit = max([max([abs(z.real), abs(z.imag)]) for z in zs])
    plt.xlim((-limit, limit))
    plt.ylim((-limit, limit))
    plt.grid(True, which='both')
    plt.ylabel('Im')
    plt.xlabel('Re')


def plot_phasor(*phasor_list: Phasor, color: str = None, unitary: bool = False, **kwargs):
    if unitary:
        phasor_list = [p/p.abs for p in phasor_list]
    plot_complex([p.value for p in phasor_list], color=color, **kwargs)
