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
        "_initStatusStabilities",
        "_initStatusIntegrals",
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

        self._initStatusStabilities: int = 0
        self._initStatusIntegrals: int = 0
        self._wordArrs: List[tWordVec] = []
        self._stabilityArrs: List[Tuple[tVec, tVec]] = []
        self._integralArrs: List[tIntegralVec] = []

    def _initMapSystemData(self, nMax: int, initIntegrals: bool) -> None:
        """
        Initialize symbolic words and associated stabilities as well as orbit
        integrals for the underlying hyperbolic map system. Initialization
        happens up to a requested maximal word length and (costly) calculation
        of orbit integrals can be excluded. All data is stored internally for
        reuse in dynamical determinant/weighted zeta function evaluations.

        :param nMax: maximal word length for initialization of dynamical data
        :param initIntegrals: flag indicating whether to calculate integrals
        """
        if not initIntegrals and self._initStatusStabilities >= nMax:
            self.logger.info(
                "trying to re-initialize stability data in weighted zeta!"
            )
            return
        if initIntegrals and self._initStatusIntegrals >= nMax:
            self.logger.info(
                "trying to re-initialize integral data in weighted zeta!"
            )
            return
        self.logger.debug("initializing data within weighted zeta function!")

        # TODO: re-use previously calculated data by skipping words!
        self._wordArrs = []
        self._stabilityArrs = []
        self._integralArrs = []
        for words, _ in self._symbDyn.wordGenerator(
            maxWordLength=nMax, cyclRed=True
        ):
            self._wordArrs.append(words)
            self._stabilityArrs.append(self._system.getStabilities(words))
            if initIntegrals:
                self._integralArrs.append(
                    self._integralProvider.getOrbitIntegrals(words)
                )
                self._initStatusIntegrals = nMax
        self._initStatusStabilities = nMax

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
                np.power(stab1, s, dtype=complex)
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
            "computing afArr for %s with words up to length %d", str(s), nMax
        )

        sSize = s.shape[0]
        integralShape = self._integralProvider.integralShape
        afArr = np.zeros(
            (sSize, nMax, dMax + 1, 2, *integralShape), dtype=np.complex128
        )

        self._initMapSystemData(nMax, initIntegrals=True)

        s = s.reshape(-1, 1, 1, 1)
        for n in range(1, nMax + 1):
            stab1, stab2 = self._stabilityArrs[n - 1]
            stab1 = stab1.reshape(1, -1, 1, 1)
            stab2 = stab2.reshape(1, -1, 1, 1)

            integrals = self._integralArrs[n - 1].reshape(
                1, -1, *integralShape
            )

            for d in range(dMax + 1):
                tmp = (
                    np.power(np.log(stab1), d)
                    * np.power(stab1, s, dtype=complex)
                    / ((1 - stab1) * (stab2 - 1))
                )
                afArr[:, n - 1, d, 0, :, :] = np.sum(tmp, axis=1)
                afArr[:, n - 1, d, 1, :, :] = np.sum(
                    -1.0 * integrals * tmp, axis=1
                )
            afArr[:, n - 1, :, :, :, :] *= -1.0 / n

        return afArr
