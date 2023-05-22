"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from abc import ABC, abstractmethod

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
