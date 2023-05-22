"""
Module containing (numba compiled) helper functions that are used within
methods of Schottky surface-related classes.

Authors:\n
- Philipp Schuette\n
"""

import numba as nb  # type: ignore
import numpy as np

from pyzeta.core.pyzeta_types.general import tMatVec, tVec


@nb.njit(
    nb.float64[:](nb.float64[:, :, :]), fastmath=True, cache=True
)  # type: ignore
def getDisplacementLengths(symVec: tMatVec) -> tVec:
    r"""
    Numba compiled helper that calculates a vector of displacement lengths
    parallel to an input vector of elements of
    :math:`\mathrm{SL}(2, \mathbb{R})`.

    :param symVec: vector of 2x2 real matrices of unit determinent
    :return: vector of displacement lengths
    """
    trace = np.abs(symVec[:, 0, 0] + symVec[:, 1, 1])
    return 2.0 * np.arccosh(trace / 2.0)  # type: ignore
