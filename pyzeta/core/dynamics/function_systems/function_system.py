"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from abc import ABC, abstractmethod
from typing import Tuple

from pyzeta.core.pyzeta_types.general import tBoolMat, tVec, tWordVec
from pyzeta.framework.pyzeta_logging.loggable import Loggable


class FunctionSystem(ABC, Loggable):
    "Abstract representation of an (iterated) function system."

    @property
    @abstractmethod
    def adjacencyMatrix(self) -> tBoolMat:
        """
        Return the adjacency matrix of the given function system.

        :return: adjacency matrix
        """

    @property
    @abstractmethod
    def fundamentalIntervals(self) -> Tuple[Tuple[float, float], ...]:
        """
        Return the (real) domain of the functions making up the system. Domains
        are intervals which are represented as pairs of floats.

        :return: intervals of definition of the function system
        """

    @property
    def intervalCount(self) -> int:
        """
        Return the number of fundamental intervals on which the iterated
        function system is defined. This should also equal the size of the
        (square) adjacency matrix.

        :return: number of functions
        """
        return len(self.fundamentalIntervals)

    @abstractmethod
    def getStabilities(self, words: tWordVec) -> tVec:
        """
        Return the stabilities (i.e. derivatives of function iterates at fixed
        points) associated with an array of symbolic words.

        :param words: array of symbolic words determining the function iterates
        :return: stabilities of the (symbolically given) periodic orbits
        """

    @abstractmethod
    def getPeriodicPoints(self, words: tWordVec) -> tVec:
        """
        Return the periodic points (i.e. fixed points of function iterates)
        associated with an array of symbolic words.

        :param words: array of symbolic words determining the function iterates
        :return: fixed points of the (symbolically given) function iterates
        """
