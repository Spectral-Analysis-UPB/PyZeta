"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

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
        TODO.
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

    def getGenerators(self, indices: tIndexVec) -> tMatVec:
        """
        Convenience method used to retrieve an array of generators of the
        Moebius transformation based map system. Used in orbit integral
        calculation.
        """
        raise NotImplementedError()
