"""
TODO.

Authors:\n
- Philipp Schuette
"""

from abc import ABC, abstractmethod
from typing import Tuple

from pyzeta.core.pyzeta_types.general import tBoolMat, tVec, tWordVec
from pyzeta.framework.pyzeta_logging.loggable import Loggable


class HyperbolicMapSystem(ABC, Loggable):
    "Abstract representation of a hyperbolic (`n`-dimensional) map system."

    @property
    @abstractmethod
    def fundamentalRectangles(
        self,
    ) -> Tuple[Tuple[Tuple[float, float], ...], ...]:
        """
        Return the (real) domain of the maps making up the system. Domains
        are products of `n` intervals which in turn are represented as pairs of
        floats.

        :return: rectangles of definition of the map system
        """

    @property
    def dimension(self) -> int:
        """
        Return the dimension `n` of the map system.

        :return: the map system's dimension
        """
        if len(self.fundamentalRectangles) == 0:
            raise ValueError(
                "map system without fundamental rectangles is ill-defined!"
            )
        return len(self.fundamentalRectangles[0])

    @property
    @abstractmethod
    def adjacencyMatrix(self) -> tBoolMat:
        """
        Return the adjacency matrix of the given system of maps.

        :return: adjacency matrix
        """

    @abstractmethod
    def getStabilities(self, words: tWordVec) -> Tuple[tVec, ...]:
        """
        Return the stabilities (i.e. derivatives of map iterates at fixed
        points) associated with an array of symbolic words.

        :param words: array of symbolic words determining the map iterates
        :return: stabilities of the (symbolically given) periodic orbits
        """

    @abstractmethod
    def getPeriodicPoints(self, words: tWordVec) -> Tuple[tVec, ...]:
        """
        Return the periodic points (i.e. fixed points of map iterates)
        associated with an array of symbolic words.

        :param words: array of symbolic words determining the map iterates
        :return: fixed points of the (symbolically given) iterates
        """
