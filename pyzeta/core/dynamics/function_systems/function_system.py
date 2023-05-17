"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from abc import ABC, abstractmethod
from typing import Tuple

from pyzeta.core.pyzeta_types.general import tBoolMat, tVec, tWordVec


class FunctionSystem(ABC):
    "Abstract representation of an (iterated) function system."

    @abstractmethod
    @property
    def adjacencyMatrix(self) -> tBoolMat:
        """
        Return the adjacency matrix of the given function system.

        :return: adjacency matrix
        """

    @abstractmethod
    @property
    def fundamentalRectangles(
        self,
    ) -> Tuple[Tuple[Tuple[float, float], ...], ...]:
        """
        Return the real domains of the functions making up the system. Domains
        are products of intervals which are represented as tuples of pairs of
        floats.

        :return: rectangles of definition of the function system
        """

    @property
    def intervalCount(self) -> int:
        """
        Return the number of fundamental intervals on which the iterated
        function system is defined. This should also equal the size of the
        (square) adjacency matrix.

        :return: number of functions
        """
        return len(self.fundamentalRectangles)

    @property
    def dimension(self) -> int:
        """
        Return the dimension of the analytic maps making up the system.

        :return: dimension of the function system
        """
        if len(self.fundamentalRectangles) == 0:
            raise ValueError(
                "can't determine system dimension with zero intervals!"
            )
        return len(self.fundamentalRectangles[0])

    @abstractmethod
    def getStabilities(self, words: tWordVec) -> Tuple[tVec, ...]:
        """
        Return the stabilities (i.e. derivatives of function iterates at fixed
        points) associated with an array of symbolic words.

        :param words: array of symbolic words determining the function iterates
        :return: stabilities of the (symbolically given) periodic orbits
        """

    @abstractmethod
    def getPeriodicPoints(self, words: tWordVec) -> Tuple[tVec, ...]:
        """
        Return the periodic points (i.e. fixed points of function iterates)
        associated with an array of symbolic words.

        :param words: array of symbolic words determining the function iterates
        :return: fixed points of the (symbolically given) function iterates
        """
