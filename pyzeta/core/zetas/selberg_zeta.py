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
from pyzeta.core.dynamics.symbolic_dynamics.symbolic_dynamics import (
    SymbolicDynamics,
)
from pyzeta.core.pyzeta_types.general import tMat, tVec, tWordVec
from pyzeta.core.zetas.abstract_zeta import AbstractZeta


class SelbergZeta(AbstractZeta):
    "TODO."

    __slots__ = (
        "_system",
        "_symbDyn",
        "_initStatus",
        "_wordArrs",
        "_stabilityArrs",
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
        self._symbDyn = SymbolicDynamics(self._system.adjacencyMatrix)

        self._initStatus: int = 0
        self._wordArrs: List[tWordVec] = []
        self._stabilityArrs: List[tVec] = []

    def __str__(self) -> str:
        "Simple string representation of a Selberg zeta function instance."
        return f"SelbergZeta({self._system})"

    def _initWordsAndStabilities(self, nMax: int) -> None:
        """
        Initialize symbolic words and associated stabilities for the underlying
        function system up to a requested maximal word length. The initialized
        data is stored internally for reuse in zeta function evaluations.

        :param nMax: maximal word length for initialization of dynamical data
        """
        if self._initStatus >= nMax:
            self.logger.warning("trying to re-initialize data in zeta!")
            return
        self.logger.debug("initializing data within zeta function!")

        for words, _ in self._symbDyn.wordGenerator(
            maxWordLength=nMax, cyclRed=True
        ):
            self._wordArrs.append(words)
            self._stabilityArrs.append(self._system.getStabilities(words))
        self._initStatus = nMax

    # docstr-coverage: inherited
    def calcA(self, s: tVec, nMax: int) -> tMat:
        self.logger.info(
            "starting Bell polýnomial construction on %d-vector", s.shape[0]
        )

        sSize = s.shape[0]
        aArr = np.empty((sSize, nMax), dtype=np.complex128)

        self._initWordsAndStabilities(nMax)
        s = s.reshape(-1, 1)
        for n in range(1, nMax + 1):
            stabilities = self._stabilityArrs[n - 1].reshape(1, -1)
            aArr[:, n - 1] = np.sum(
                np.power(stabilities, s, dtype=complex) / (1 - stabilities),
                axis=1,
            )
            aArr[:, n - 1] *= -1.0 / n
        return aArr
