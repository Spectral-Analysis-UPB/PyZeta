"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from typing import Tuple

from pyzeta.core.dynamics.function_systems.function_system import (
    FunctionSystem,
)
from pyzeta.core.pyzeta_types.general import tBoolMat, tMatVec


class MoebiusSystem(FunctionSystem):
    """
    Abstract representation of an (iterated) function system the functions of
    which are given by Moebius transformations.
    """

    __slots__ = ("_gens", "_adj", "_fundRect")

    def __init__(
        self,
        generators: tMatVec,
        adjacencyMatrix: tBoolMat,
        fundamentalIntervals: Tuple[Tuple[float, float], ...],
    ) -> None:
        """
        TODO.
        """
        # TODO: conduct some sanity checks that the given data is consistent
        self._gens = generators
        # TODO: adjust adjacency matrix to the product setting!
        self._adj = adjacencyMatrix

        # construct the rectangles where the system is defined as products of
        # intervals where the generators are defined
        fundamentalRectangles = []
        for interval1 in fundamentalIntervals:
            for interval2 in fundamentalIntervals:
                fundamentalRectangles.append((interval1, interval2))
        self._fundRect = tuple(fundamentalRectangles)

    # docstr-coverage:inherited
    @property
    def adjacencyMatrix(self) -> tBoolMat:
        return self._adj

    # docstr-coverage:inherited
    @property
    def fundamentalRectangles(
        self,
    ) -> Tuple[Tuple[Tuple[float, float], ...], ...]:
        return self._fundRect
