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
    def fundamentalIntervals(
        self,
    ) -> Tuple[Tuple[float, float], ...]:
        """
        Return the (real) domains of the maps making up the system. Domains
        are bounded, connected subsets of the real line which in turn are
        represented as pairs of floats.

        :return: intervals of definition of the map system
        """

    @property
    @abstractmethod
    def adjacencyMatrix(self) -> tBoolMat:
        """
        Return the adjacency matrix of the given system of maps. The size of
        this matrix must fit the underlying alphabet of the map system.

        :return: adjacency matrix
        """

    @abstractmethod
    def getStabilities(self, words: tWordVec) -> Tuple[tVec, tVec]:
        """
        Return the stabilities (i.e. derivatives of map iterates at fixed
        points) associated with an array of symbolic words.

        :param words: array of symbolic words determining the map iterates
        :return: stabilities of the (symbolically given) periodic orbits
        """

    @abstractmethod
    def getPeriodicPoints(self, words: tWordVec) -> Tuple[tVec, tVec]:
        """
        Return the periodic points (i.e. fixed points of map iterates)
        associated with an array of symbolic words.

        :param words: array of symbolic words determining the map iterates
        :return: fixed points of the (symbolically given) iterates
        """
