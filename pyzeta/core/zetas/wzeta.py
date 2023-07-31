"""
Non-symmetry reduced implementation of the abstract weighted zeta interface.

Authors:\n
- Philipp Schuette\n
"""

import numpy as np

from pyzeta.core.pyzeta_types.general import tVec
from pyzeta.core.zetas.abstract_wzeta import AbstractWeightedZeta


class WeightedZeta(AbstractWeightedZeta):
    "Class representing non-reduced weighted zetas and dynamical determinants."

    __slots__ = (
        "_system",
        "_symbDyn",
        "_integralProvider",
        "_initStatus",
        "_wordArrs",
        "_stabilityArrs",
        "_integralArrs",
    )

    def __init__(self) -> None:
        """
        TODO.
        """
        # TODO: much of the same stuff as for Selberg zetas but with
        # TODO: additional integral provider!
        return

    def _initMapSystemData(self, nMax: int) -> None:
        """
        TODO.
        """
        # TODO: initialize words, stabilities, integrals from provider

    # docstr-coverage: inherited
    def calcA(self, s: tVec, nMax: int) -> tVec:
        self.logger.info(
            "computing aArr for %s up to word length %d", str(s), nMax
        )
        sSize = s.shape[0]
        aArr = np.empty((sSize, nMax), dtype=np.complex128)

        # we do not need to initialize period integrals here:
        # TODO: cannot inherit here because stabilities come from map system!
        self._initMapSystemData(nMax)
        s = s.reshape(-1, 1)
        for n in range(1, nMax + 1):
            stabilities = self._stabilityArrs[n - 1].reshape(1, -1)
            aArr[:, n - 1] = np.sum(
                np.power(stabilities, s + 1, dtype=complex)
                / np.power(1 - stabilities, 2),
                axis=1,
            )
            aArr[:, n - 1] *= -1.0 / n
        return aArr

    def calcAf(self, s: tVec, nMax: int, dMax: int) -> tMatVec:
        r"""
        Compute the basis step in the iterative process of computing Bell
        Polynomials with weights (c.f. documentation of pyzeta.zeta.calcZeta).

        :param s: Values entered in the zeta function
        :type s: numpy.ndarray of shape `(number of values,)`
        :param nMax: Maximal word length to be included in the iterative
            approximation
        :type nMax: int
        :param dMax: Maximal order of `s`-derivates included in the iterative
            approximation
        :type dMax: int
        :return: first steps in the iterative process of computing Bell
            Polynomials
        :rtype: numpy.ndarray of shape `(number of values, nMax, dMax+1, 2,
            len(xMinusArr), len(xPlusArr))`
        """
        logger.info(
            f"computing afArr for values {s} using words up to length"
            + f" {nMax}"
        )
        sSize = s.shape[0]
        minusLen, plusLen = self.xMinusDom.shape
        afArr = np.zeros(
            (sSize, nMax, dMax + 1, 2, minusLen, plusLen), dtype=np.complex128
        )

        self.initWords(nMax)
        s = s.reshape(-1, 1, 1, 1)
        for n in range(1, nMax + 1):
            lengths = self.lengthArr[n - 1].reshape(1, -1, 1, 1)
            integrals = self.integralArr[n - 1].reshape(
                1, -1, minusLen, plusLen
            )
            for d in range(dMax + 1):
                tmp = (
                    np.power(-1.0 * lengths, d)
                    * np.exp(-(s + 1.0) * lengths)
                    / np.power(1 - np.exp(-lengths), 2)
                )
                afArr[:, n - 1, d, 0, :, :] = np.sum(tmp, axis=1)
                afArr[:, n - 1, d, 1, :, :] = np.sum(
                    -1.0 * integrals * tmp, axis=1
                )
            afArr[:, n - 1, :, :, :, :] *= -1.0 / n

        return afArr
