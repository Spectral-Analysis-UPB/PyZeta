"""
Module containing specializations of the abstract base classes `FunctionSystem`
and `HyperbolicMapSystem` to the case of the underlying functions/mappings
being given by Moebius transformations (i.e. real 2x2 matrices with unit
determinant acting on the upper half plane).

Authors:\n
- Philipp Schuette\n
"""

from typing import Tuple

import numpy as np
from numpy import exp

from pyzeta.core.dynamics.function_systems.function_system import (
    FunctionSystem,
)
from pyzeta.core.dynamics.function_systems.helpers.schottky_helper import (
    getDisplacementLengths,
)
from pyzeta.core.dynamics.function_systems.map_system import (
    HyperbolicMapSystem,
)
from pyzeta.core.pyzeta_types.general import (
    tBoolMat,
    tIndexVec,
    tMatVec,
    tVec,
    tWordVec,
)


class MoebiusFunctionSystem(FunctionSystem):
    """
    Abstract representation of an (iterated) function system the functions of
    which are given by Moebius transformations.
    """

    __slots__ = ("phi", "_adj")

    def __init__(self, generators: tMatVec, adjacencyMatrix: tBoolMat) -> None:
        """
        Initialize an iterated function system which is more concretely given
        by iteration of Moebius transformations on the upper half plane.

        :param generators: array of real 2x2 matrices of non-null determinants
        :param adjacency matrix: boolean matrix determining legal transitions
        """
        # sanity check that given data is consistent
        if generators.shape[0] != adjacencyMatrix.shape[0]:
            raise ValueError(
                "shape miss-match between generators and adjacency matrix!"
            )
        if adjacencyMatrix.shape[0] != adjacencyMatrix.shape[1]:
            raise ValueError(
                "must provide square adjacency matrix for Moebius system!"
            )
        self.phi = generators
        self._adj = adjacencyMatrix

    def _iterateGenerators(self, words: tWordVec) -> tMatVec:
        """
        Iterate the functions defining the system along the individual members
        of a given array of symbolic words.

        :param words: array of words whose members are used for iteration
        :return: array of 2x2 matrices corresponding to the iterates
        """
        # TODO: implement caching to save from re-calculation!
        self.logger.debug("iterating generators along %s", str(words))
        wordNum = words.shape[0]
        iteratedGenerators = np.empty((wordNum, 2, 2), dtype=np.float64)
        for i in range(wordNum):
            temp = np.eye(2, dtype=np.float64)
            word = words[i]
            for letter in word:
                temp = self.phi[letter] @ temp
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

    # docstr-coverage: inherited
    @property
    def adjacencyMatrix(self) -> tBoolMat:
        return self._adj


class MoebiusMapSystem(HyperbolicMapSystem):
    """
    Abstract representation of a hyperbolic map system which is basically given
    by the inclusion of an additional dimension in a Moebius transformation
    based iterated function system.
    """

    __slots__ = ("_functionSystem",)

    def __init__(self, functionSystem: MoebiusFunctionSystem) -> None:
        """
        Initialize a hyperbolic map system which delegates most work to an
        associated Moebius function system. The only required property for
        subclasses to implement is `fundamentalIntervals`.

        :param functionSystem: the backing function system
        """
        self._functionSystem = functionSystem

    # docstr-coverage: inherited
    @property
    def adjacencyMatrix(self) -> tBoolMat:
        return self._functionSystem.adjacencyMatrix

    # docstr-coverage: inherited
    def getStabilities(self, words: tWordVec) -> Tuple[tVec, tVec]:
        contractingStabs = self._functionSystem.getStabilities(words)
        return contractingStabs, 1 / contractingStabs

    def getGenerators(self, indices: tIndexVec) -> tMatVec:
        """
        Convenience method used to retrieve an array of generators of the
        Moebius transformation based map system. Used in orbit integral
        calculation.

        :param indices: array of indices into the underlying Moebius trafos
        :return: array of 2x2 matrices representing Moebius trafos
        """
        returnGenerators = np.empty((indices.shape[0], 2, 2), dtype=np.float64)
        for j, index in enumerate(indices):
            returnGenerators[j, :, :] = self._functionSystem.phi[index]

        return returnGenerators

    # docstr-coverage: inherited
    def getPeriodicPoints(self, words: tWordVec) -> Tuple[tVec, tVec]:
        self.logger.info("computing periodic points")
        iteratedGenerators = self._functionSystem._iterateGenerators(words)

        # the matrix entry `b` is not required as we assume `c != 0`
        a = iteratedGenerators[:, 0, 0]
        c = iteratedGenerators[:, 1, 0]
        d = iteratedGenerators[:, 1, 1]

        discriminant = np.sqrt((a + d) ** 2 - 4.0) / (2.0 * c)
        intermediate = (a - d) / (2.0 * c)
        fixPts = intermediate + discriminant, intermediate - discriminant

        # order the fixed points as (repelling, attracting) by selecting...
        mask = np.array(
            [
                not self._inInterval(lastLetter, secondFixPt)
                for lastLetter, secondFixPt in zip(words[:, -1], fixPts[1])
            ],
            dtype=np.bool_,
        )
        # .. and then switching selected elements
        tmp = fixPts[1][mask]
        fixPts[1][mask] = fixPts[0][mask]
        fixPts[0][mask] = tmp

        return fixPts

    def _inInterval(self, letter: np.uint8, point: float) -> bool:
        """
        Determine if a given fixed point lies within a fundamental interval.

        :param letter: symbolic letter fixing the interval
        :param fixPoint: point whose interval membership is checked
        """
        # TODO: test this thorougly!
        intervals = self.fundamentalIntervals
        return intervals[letter][0] <= point <= intervals[letter][1]
