"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from abc import ABC, abstractmethod
from typing import Tuple

from pyzeta.core.pyzeta_types.general import tIntegralVec, tWordVec


class IntegralProvider(ABC):
    "Abstract base realizing the potentials used in weighted zeta functions."

    @abstractmethod
    def getOrbitIntegrals(self, words: tWordVec) -> tIntegralVec:
        """
        Calculate an array of 2d grids containing orbit integrals parallel to
        a given array of symbolic words.

        :param words: array of symbolic words to calculate orbit integrals for
        :return: array of orbit integrals on a 2d grid
        """

    @property
    @abstractmethod
    def integralShape(self) -> Tuple[int, int]:
        """
        Return the shape of individual orbit integrals as calculated by the
        given provider instance. Usually this returns `(n, n)` for square
        and `(n, m)` for non-square arrays of integral values.

        :return: shape of individual arrays of calculated integrals
        """
