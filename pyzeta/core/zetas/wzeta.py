"""
Non-symmetry reduced implementation of the abstract weighted zeta interface.

Authors:\n
- Philipp Schuette\n
"""

from typing import List, Tuple

import numpy as np

from pyzeta.core.dynamics.function_systems.integral_provider import (
    IntegralProvider,
)
from pyzeta.core.dynamics.function_systems.map_system import (
    HyperbolicMapSystem,
)
from pyzeta.core.dynamics.symbolic_dynamics.abstract_dynamics import (
    AbstractSymbolicDynamics,
)
from pyzeta.core.pyzeta_types.general import (
    tDynDetIntermediate,
    tIntegralVec,
    tVec,
    tWordVec,
)
from pyzeta.core.pyzeta_types.integral_arguments import tOrbitIntegralInitArgs
from pyzeta.core.pyzeta_types.integrals import OrbitIntegralType
from pyzeta.core.pyzeta_types.map_systems import MapSystemType
from pyzeta.core.pyzeta_types.symbolics import SymbolicDynamicsType
from pyzeta.core.pyzeta_types.system_arguments import tMapSystemInitArgs
from pyzeta.core.zetas.abstract_wzeta import AbstractWeightedZeta
from pyzeta.framework.ioc.container_provider import ContainerProvider


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

    def __init__(
        self,
        *,
        mapSystem: MapSystemType,
        systemInitArgs: tMapSystemInitArgs,
        integralType: OrbitIntegralType,
        integralInitArgs: tOrbitIntegralInitArgs,
    ) -> None:
        """
        TODO.
        """
        self.logger.info(
            "creating %s for %s", self.__class__.__name__, str(mapSystem)
        )

        container = ContainerProvider.getContainer()
        self._system = container.tryResolve(
            HyperbolicMapSystem, systemType=mapSystem, initArgs=systemInitArgs
        )
        self._symbDyn = container.tryResolve(
            AbstractSymbolicDynamics,
            symbolicsType=SymbolicDynamicsType.NON_REDUCED,
            adjacencyMatrix=self._system.adjacencyMatrix,
        )
        self._integralProvider = container.tryResolve(
            IntegralProvider,
            integralType=integralType,
            mapSystem=self._system,
            initArgs=integralInitArgs,
        )

        self._initStatus: int = 0
        self._wordArrs: List[tWordVec] = []
        self._stabilityArrs: List[Tuple[tVec, tVec]] = []
        self._integralArrs: List[tIntegralVec] = []

        return

    def _initMapSystemData(self, nMax: int, initIntegrals: bool) -> None:
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
        self._initMapSystemData(nMax, initIntegrals=False)
        s = s.reshape(-1, 1)
        for n in range(1, nMax + 1):
            stab1, stab2 = self._stabilityArrs[n - 1]
            stab1, stab2 = stab1.reshape(1, -1), stab2.reshape(1, -1)
            aArr[:, n - 1] = np.sum(
                np.power(stab1, s + 1, dtype=complex)
                / ((1 - stab1) * (stab2 - 1)),
                axis=1,
            )
            aArr[:, n - 1] *= -1.0 / n
        return aArr

    def calcWeightedA(
        self, s: tVec, nMax: int, dMax: int
    ) -> tDynDetIntermediate:
        """
        Compute the basis step in the iterative process of computing Bell
        Polynomials with weights.

        :param s: Values entered in the zeta function
        :param nMax: Maximal word length in the iterative approximation
        :param dMax: Maximal order of `s`-derivates included
        :return: first step in iterative Bell polynomial calculation
        """
        self.logger.info(
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
