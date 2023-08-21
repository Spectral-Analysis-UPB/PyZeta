"""
Abstract base class for invariant Ruelle distributions.

Authors:\n
- Philipp Schuette\n
"""

from abc import ABC, abstractmethod

from pyzeta.core.pyzeta_types.general import tMatVec, tVec
from pyzeta.framework.pyzeta_logging.loggable import Loggable


class AbstractRuelleDistribution(ABC, Loggable):
    "Abstract class representation of Ruelle distributions."

    @abstractmethod
    def __call__(self, s: tVec, nMax: int) -> tMatVec:
        """
        Calculate an approximation of the distribution with `nMax` summands on
        a two-dimensional grid.

        :param s: array of complex values to evaluate the distribution on
        :param nMax: number of summands used to approximate the distribution
        :return: array of two-dimensional arrays of distribution evaluations
            parallel to the input array `s`
        """
