"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

import numpy as np
from numpy.linalg import inv

from pyzeta.core.dynamics.function_systems.moebius_system import (
    MoebiusFunctionSystem,
)
from pyzeta.core.pyzeta_types.general import tBoolMat, tMatVec


class SchottkySurface(MoebiusFunctionSystem):
    "Class representation of the geodesic flow dynamics on Schottky surfaces."

    def __init__(self, generators: tMatVec) -> None:
        r"""
        Generators are assumed to be in :math:`\mathrm{SL}(2, \mathbb{R})`.

        TODO.
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
        TODO.
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
        TODO.
        """
        rank = generators.shape[0]
        fullSystem = np.empty((2 * rank, 2, 2), dtype=np.float64)
        fullSystem[rank:] = generators

        for i in range(rank):
            fullSystem[i] = inv(generators[i])

        return fullSystem
