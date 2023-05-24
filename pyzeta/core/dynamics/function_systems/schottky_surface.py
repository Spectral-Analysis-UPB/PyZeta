"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

import numpy as np
from numpy import exp
from numpy.linalg import inv

from pyzeta.core.dynamics.function_systems.helpers.schottky_helper import (
    getDisplacementLengths,
)
from pyzeta.core.dynamics.function_systems.moebius_system import MoebiusSystem
from pyzeta.core.pyzeta_types.general import tBoolMat, tMatVec, tVec, tWordVec


class SchottkySurface(MoebiusSystem):
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

    def _iterateGenerators(self, words: tWordVec) -> tMatVec:
        """
        TODO.
        """
        self.logger.debug("iterating generators along %s", str(words))
        wordNum = words.shape[0]
        iteratedGenerators = np.empty((wordNum, 2, 2), dtype=np.float64)
        for i in range(wordNum):
            temp = np.eye(2, dtype=np.float64)
            word = words[i]
            for letter in word:
                temp = self._gens[letter] @ temp
            iteratedGenerators[i] = temp
        self.logger.debug(
            "iterated generators are %s", str(iteratedGenerators)
        )
        return iteratedGenerators

    # docstr-coverage: inherited
    def getStabilities(self, words: tWordVec) -> tVec:
        self.logger.info(
            "computing stabilities (exponentials of displacement lengths)"
        )
        iteratedGenerators = self._iterateGenerators(words)
        displacementLens = getDisplacementLengths(iteratedGenerators)
        self.logger.debug(
            "calculated displacement lengths %s", str(displacementLens)
        )
        return exp(-displacementLens)  # type: ignore
