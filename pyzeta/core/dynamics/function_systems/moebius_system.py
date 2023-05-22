"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from pyzeta.core.dynamics.function_systems.function_system import (
    FunctionSystem,
)
from pyzeta.core.pyzeta_types.general import tBoolMat, tMatVec


class MoebiusSystem(FunctionSystem):
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
