"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from abc import ABC, abstractmethod
from typing import Union

import numpy as np

from pyzeta.core.pyzeta_types.general import tMat, tVec
from pyzeta.core.zetas.helpers.bell_iteration import bellIteration
from pyzeta.framework.pyzeta_logging.loggable import Loggable


class AbstractZeta(ABC, Loggable):
    "TODO."

    @abstractmethod
    def calcA(self, s: tVec, nMax: int) -> tMat:
        """
        Compute the base step in the iterative process of Bell polynomial
        construction.

        :param s: array of complex points to evaluate the zeta function on
        :param nMax: the maximal order to use in the cycle expansion
        :return: array of shape `(number of s-values, nMax)`
        """

    def calcD(self, s: tVec, nMax: int) -> tMat:
        """
        Compute the actual steps in the iterative process of Bell polynomial
        construction.

        :param s: array of complex points to evaluate the zeta function on
        :param nMax: the maximal order to use in the cycle expansion
        :return: array of shape `(number of s-values, nMax)`
        """
        self.logger.info(
            "computing dArr at %s using wordLen < %d", str(s), nMax
        )
        aArr = self.calcA(s, nMax)
        return bellIteration(s, aArr, nMax)  # type: ignore

    def __call__(self, s: Union[complex, tVec], nMax: int) -> tVec:
        """
        Compute the values of the abstract zeta function on an input vector.

        :param s: vector of inputs in the complex plane
        :param nMax: cutoff in the cycle expansion
        :return: function values of the zeta function
        """
        if not isinstance(s, np.ndarray):
            s = np.array([s], dtype=np.complex128)

        self.logger.info(
            "evaluating %s on input vector of len=%d with nMax=%d",
            self.__class__.__name__,
            s.shape[0],
            nMax,
        )

        dArr = self.calcD(s.astype(dtype=np.complex128), nMax)
        return np.sum(dArr, axis=1)  # type: ignore
