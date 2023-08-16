"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from abc import abstractmethod

import numpy as np
from scipy.special import binom  # type: ignore

from pyzeta.core.pyzeta_types.general import (
    tDynDetIntermediate,
    tDynDetReturn,
    tVec,
)
from pyzeta.core.zetas.abstract_zeta import AbstractZeta


class AbstractWeightedZeta(AbstractZeta):
    "Abstract base for dynamical determinants and weighted zeta functions."

    @abstractmethod
    def calcWeightedA(
        self, s: tVec, nMax: int, dMax: int
    ) -> tDynDetIntermediate:
        """
        Compute the base step in the iterative process of Bell polynomial
        construction with weight functions.

        :param s: array of complex points to evaluate the zeta function on
        :param nMax: maximal summation order to use in the cycle expansion
        :param dMax: maximal number of `s`-derivatives to calculate
        :return: array of shape `(len(s), nMax, dMax+1, 2, shape(weights))`
        """

    def calcWeightedD(
        self, s: tVec, nMax: int, dMax: int
    ) -> tDynDetIntermediate:
        """
        Compute the actual steps in the iterative process of Bell polynomial
        construction with weight functions.

        :param s: array of complex points to evaluate the zeta function on
        :param nMax: maximal summation order to use in the cycle expansion
        :param dMax: maximal number of `s`-derivatives to calculate
        :return: array of shape `(len(s), nMax, dMax+1, 2, shape(weights))`
        """
        self.logger.info(
            "computing dArr at %s using wordLen < %d", str(s), nMax
        )
        afArr = self.calcWeightedA(s, nMax, dMax)
        dfArr = np.zeros_like(afArr, dtype=np.complex128)

        # initialize induction basis
        dfArr[:, 0, :, :, ...] = 0
        dfArr[:, 0, 0, 0, ...] = 1
        # calculate the induction step
        for n in range(1, nMax + 1):
            for k in range(1, n + 1):
                for d in range(0, dMax + 1):
                    for m in range(0, d + 1):
                        dfArr[:, n, d, 0, ...] += (
                            (1.0 * k / n)
                            * binom(d, m)
                            * (
                                dfArr[:, n - k, m, 0, ...]
                                * afArr[:, k - 1, d - m, 0, ...]
                            )
                        )
                        dfArr[:, n, d, 1, :, :] += (
                            (1.0 * k / n)
                            * binom(d, m)
                            * (
                                dfArr[:, n - k, m, 1, ...]
                                * afArr[:, k - 1, d - m, 0, ...]
                                + dfArr[:, n - k, m, 0, ...]
                                * afArr[:, k - 1, d - m, 1, ...]
                            )
                        )

        return dfArr

    def calcDynamicalDeterminant(
        self, s: tVec, nMax: int, dMax: int
    ) -> tDynDetReturn:
        """
        TODO.

        :param s: array of complex points to evaluate the zeta function on
        :param nMax: maximal summation order to use in the cycle expansion
        :param dMax: maximal number of `s`-derivatives to calculate
        :return: array of shape `(len(s), dMax+1, 2, shape(weights))`
        """
        dfArr = self.calcWeightedD(s, nMax, dMax)
        dynDet = np.sum(dfArr, axis=1)
        return dynDet  # type: ignore

    def calcWeightedZeta(self, s: tVec, nMax: int) -> tDynDetReturn:
        """
        TODO.

        :param s: array of complex points to evaluate the zeta function on
        :param nMax: maximal summation order to use in the cycle expansion
        :param dMax: maximal number of `s`-derivatives to calculate
        :return: array of shape `(len(s), dMax+1, 2, shape(weights))`
        """
        dynDet = self.calcDynamicalDeterminant(s, nMax, 0)
        numerator = dynDet[:, 0, 1, ...]
        denominator = dynDet[:, 0, 0, ...]
        return numerator / denominator
