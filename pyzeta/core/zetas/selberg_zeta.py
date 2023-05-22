"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from typing import List

import numpy as np

from pyzeta.core.dynamics.function_systems.function_system import (
    FunctionSystem,
)
from pyzeta.core.pyzeta_types.general import tMat, tVec, tWordVec
from pyzeta.core.zetas.abstract_zeta import AbstractZeta


class SelbergZeta(AbstractZeta):
    "TODO."

    __slots__ = (
        "_system",
        "_symbDyn",
        "_initStatus",
        "_wordArr",
        "_stabilityArr",
    )

    def __init__(self, functionSystem: FunctionSystem) -> None:
        """
        TODO.
        """
        self.logger.info(
            "creating %s for %s", self.__class__.__name__, str(functionSystem)
        )

        # TODO: resolve function system from container!
        self._system = functionSystem
        # TODO: resolve symbolic dynamic from container!

        self._initStatus: int = 0
        self._wordArr: List[tWordVec] = []
        self._stabilityArr: List[tVec] = []

    def __str__(self) -> str:
        "Simple string representation of a Selberg zeta function instance."
        return f"SelbergZeta({self._system})"

    def initWords(self, nMax: int) -> None:
        """
        TODO.
        """
        if self._initStatus >= nMax:
            self.logger.warning("re-initializing data in zeta function!")
            return
        self.logger.debug("initializing data within zeta function")
        self._initStatus = nMax

        # TODO: calculate stabilities from symbolic and function dynamics!

    # docstr-coverage: inherited
    def calcA(self, s: tVec, nMax: int) -> tMat:
        self.logger.info(
            "starting Bell polýnomial construction on %d-vector", s.shape[0]
        )

        sSize = s.shape[0]
        aArr = np.empty((sSize, nMax), dtype=np.complex128)

        self.initWords(nMax)
        s.reshape(-1, 1)
        for n in range(1, nMax + 1):
            stabilities = self._stabilityArr[n - 1].reshape(1, -1)
            aArr[:, n - 1] = np.sum(
                np.power(stabilities, s, dtype=complex) / (1 - stabilities),
                axis=1,
            )
            aArr[:, n - 1] *= -1.0 / n
        return aArr
