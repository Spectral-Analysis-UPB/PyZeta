"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from abc import ABC, abstractmethod

from pyzeta.core.pyzeta_types.general import tBoolMat, tVec, tWordVec
from pyzeta.framework.pyzeta_logging.loggable import Loggable


class FunctionSystem(ABC, Loggable):
    "Abstract representation of an (iterated 1d) function system."

    @property
    @abstractmethod
    def adjacencyMatrix(self) -> tBoolMat:
        """
        Return the adjacency matrix of the given function system.

        :return: adjacency matrix
        """

    @abstractmethod
    def getStabilities(self, words: tWordVec) -> tVec:
        """
        Return the stabilities (i.e. derivatives of function iterates at fixed
        points) associated with an array of symbolic words.

        :param words: array of symbolic words determining the function iterates
        :return: stabilities of the (symbolically given) periodic orbits
        """
