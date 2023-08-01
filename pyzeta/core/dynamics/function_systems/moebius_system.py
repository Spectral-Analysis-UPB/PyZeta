"""
Module containing specializations of the abstract base classes `FunctionSystem`
and `HyperbolicMapSystem` to the case of the underlying functions/mappings
being given by Moebius transformations (i.e. real 2x2 matrices with unit
determinant acting on the upper half plane).

Authors:\n
- Philipp Schuette\n
"""

from abc import abstractmethod

from pyzeta.core.dynamics.function_systems.function_system import (
    FunctionSystem,
)
from pyzeta.core.dynamics.function_systems.map_system import (
    HyperbolicMapSystem,
)
from pyzeta.core.pyzeta_types.general import tBoolMat, tIndexVec, tMatVec


class MoebiusFunctionSystem(FunctionSystem):
    """
    Abstract representation of an (iterated) function system the functions of
    which are given by Moebius transformations.
    """

    __slots__ = ("_gens", "_adj", "_fundInter")

    def __init__(self, generators: tMatVec, adjacencyMatrix: tBoolMat) -> None:
        """
        Initialize an iterated function system which is more concretely given
        by iteration of Moebius transformations on the upper half plane.

        :param generators: array of real 2x2 matrices of unit determinant
        :param adjacency matrix: boolean matrix determining legal transitions
        """
        # TODO: conduct some sanity checks that the given data is consistent
        self._gens = generators
        self._adj = adjacencyMatrix

    # docstr-coverage:inherited
    @property
    def adjacencyMatrix(self) -> tBoolMat:
        return self._adj


class MoebiusMapSystem(HyperbolicMapSystem):
    """
    Abstract representation of a hyperbolic map system which is basically given
    by the inclusion of an additional dimension in a Moebius transformation
    based iterated function system.
    """

    @abstractmethod
    def getGenerators(self, indices: tIndexVec) -> tMatVec:
        """
        Convenience method used to retrieve an array of generators of the
        Moebius transformation based map system. Used in orbit integral
        calculation.
        """
