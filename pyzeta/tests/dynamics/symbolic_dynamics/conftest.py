"""
Module containing some fixtures used in tests of (reduced) symbolic dynamics
implementations.

Authors:\n
- Philipp Schuette\
- Sebastian Albrecht\n
"""

import pytest as pt
from numpy import array, bool_

from pyzeta.core.pyzeta_types.general import tBoolMat


@pt.fixture(name="adjUnit")
def fixtureAdjUnit() -> tBoolMat:
    "Return the 4d unit matrix as an adjacency matrix."
    return array(
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        dtype=bool_,
    )


@pt.fixture(name="adjInverseUnit")
def fixtureAdjInverseUnit() -> tBoolMat:
    "Return the boolean inverse of the 4d unit matrix as an adjacency matrix."
    return array(
        [[0, 1, 1, 1], [1, 0, 1, 1], [1, 1, 0, 1], [1, 1, 1, 0]], dtype=bool_
    )


@pt.fixture(name="adjFull")
def fixtureAdjFull() -> tBoolMat:
    "Return a full 3d matrix as an adjacency matrix."
    return array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], dtype=bool_)


@pt.fixture(name="adjSparse")
def fixtureAdjSparse() -> tBoolMat:
    "Return some 5d matrix with many vanishing entries as an adjacency matrix."
    return array(
        [
            [1, 0, 1, 0, 1],
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 1],
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 1],
        ],
        dtype=bool_,
    )


@pt.fixture(name="adjBlock")
def fixtureAdjBlock() -> tBoolMat:
    "Return a special 3d matrix as an adjacency matrix."
    return array([[1, 1, 1], [1, 1, 1], [0, 0, 1]], dtype=bool_)


@pt.fixture(name="adjSchottky")
def fixtureAdjSchottky() -> tBoolMat:
    "Return the adjacency matrix of a rank 2 Schottky group/surface."
    return array(
        [[1, 1, 0, 1], [1, 1, 1, 0], [0, 1, 1, 1], [1, 0, 1, 1]], dtype=bool_
    )
