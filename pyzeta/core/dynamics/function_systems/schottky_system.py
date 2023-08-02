"""
Module containing a subclass of `MoebiusFunctionSystem` representing Schottky
surface function dynamics. The subclass provides the concrete adjacency matrix
of Schottky groups and complements an array of generators with their inverses
to complete the requirements for symbolic dynamics.

Authors:\n
- Philipp Schuette\n
"""

from typing import Tuple

import numpy as np
from numpy.linalg import inv

from pyzeta.core.dynamics.function_systems.moebius_system import (
    MoebiusFunctionSystem,
    MoebiusMapSystem,
)
from pyzeta.core.pyzeta_types.general import tBoolMat, tMatVec
from pyzeta.geometry.sl2r import SL2R
from pyzeta.geometry.visuals import getFundDom


class SchottkyFunctionSystem(MoebiusFunctionSystem):
    "Class representation of the geodesic flow dynamics on Schottky surfaces."

    def __init__(self, generators: tMatVec) -> None:
        r"""
        Generators are assumed to be in :math:`\mathrm{SL}(2, \mathbb{R})`.

        :param generators: array of 2x2 generators without their inverses
        """
        rank = generators.shape[0]
        adjacencyMatrix = self._initSchottkyAdjacency(rank)
        fullSystem = self._getFullSystem(generators)

        super().__init__(
            generators=fullSystem,
            adjacencyMatrix=adjacencyMatrix,
        )

    def _initSchottkyAdjacency(self, rank: int) -> tBoolMat:
        """
        Return the adjacency matrix of a Schottky surface with given rank.

        :param rank: rank of the Schottky surface
        :return: square adjacency matrix of size `2*rank x 2*rank`
        """
        adjacency = [
            [
                1 if j != ((i + rank) % (2 * rank)) else 0
                for j in range(2 * rank)
            ]
            for i in range(2 * rank)
        ]
        return np.array(adjacency, dtype=np.bool_)

    def _getFullSystem(self, generators: tMatVec) -> tMatVec:
        """
        Complete a list of generators by calculating and appending their
        inverses in the correct positions.

        :param generators: array of 2x2 generators without inverses
        :return: completed list of generators with inverses
        """
        rank = generators.shape[0]
        fullSystem = np.empty((2 * rank, 2, 2), dtype=np.float64)
        fullSystem[rank:] = generators

        for i in range(rank):
            fullSystem[i] = inv(generators[i])

        return fullSystem


class SchottkyMapSystem(MoebiusMapSystem):
    "Class representing Schottky surface dynamics as hyperbolic map systems."

    __slots__ = ("_fundInter",)

    def __init__(self, functionSystem: SchottkyFunctionSystem) -> None:
        """
        Initialize a hyperbolic map system which delegates most work to an
        associated Schottky function system. Subclasses should only override
        the constructor.

        :param functionSystem: the backing function system
        """
        super().__init__(functionSystem)

        # determine fundamental intervals
        fullSystem = self._functionSystem.phi
        generators = fullSystem[: len(fullSystem) // 2]
        self._fundInter = tuple(getFundDom(*(SL2R(gen) for gen in generators)))

    # docstr-coverage: inherited
    @property
    def fundamentalIntervals(self) -> Tuple[Tuple[float, float], ...]:
        return self._fundInter
