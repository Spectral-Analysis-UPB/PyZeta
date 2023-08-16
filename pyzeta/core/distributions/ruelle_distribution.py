"""
Core module containing a concrete implementation of the abstract base class
`AbstractRuelleDistribution` based on Moebius hyperbolic map systems.

Authors:\n
- Philipp Schuette\n
"""

from typing import Tuple

import numpy as np
from numpy.typing import NDArray

from pyzeta.core.distributions.abstract_ruelle import (
    AbstractRuelleDistribution,
)
from pyzeta.core.dynamics.function_systems.map_system import (
    HyperbolicMapSystem,
)
from pyzeta.core.pyzeta_types.general import tMatVec, tVec
from pyzeta.core.pyzeta_types.integral_arguments import tOrbitIntegralInitArgs
from pyzeta.core.pyzeta_types.integrals import OrbitIntegralType
from pyzeta.core.pyzeta_types.map_systems import MapSystemType
from pyzeta.core.pyzeta_types.system_arguments import tMapSystemInitArgs
from pyzeta.core.pyzeta_types.zetas import WeightedZetaType
from pyzeta.core.zetas.abstract_wzeta import AbstractWeightedZeta
from pyzeta.framework.ioc.container_provider import ContainerProvider


class RuelleDistribution(AbstractRuelleDistribution):
    "Class representation of Ruelle distributions on hyperbolic map systems."

    __slots__ = ("_weightedZeta", "_system")

    def __init__(
        self,
        mapSystem: MapSystemType,
        systemInitArgs: tMapSystemInitArgs,
        integralType: OrbitIntegralType,
        sigma: float,
    ) -> None:
        """
        Initialize a new invariant Ruelle distribution for a given hyperbolic
        map system and integral provider.

        TODO.
        """
        self.logger.info(
            "creating %s for %s with %s",
            self.__class__.__name__,
            str(mapSystem),
            str(integralType),
        )

        container = ContainerProvider.getContainer()
        self._system = container.tryResolve(
            HyperbolicMapSystem, systemType=mapSystem, initArgs=systemInitArgs
        )

        integralInitArgs = self._createIntegralInitArgs(integralType, sigma)

        self._weightedZeta = container.tryResolve(
            AbstractWeightedZeta,
            zetaType=WeightedZetaType.WEIGHTED,
            mapSystem=mapSystem,
            systemInitArgs=systemInitArgs,
            integralType=integralType,
            integralInitArgs=integralInitArgs,
        )

    def _createIntegralInitArgs(
        self, integralType: OrbitIntegralType, sigma: float
    ) -> tOrbitIntegralInitArgs:
        """
        TODO.
        """
        integralInitArgs: tOrbitIntegralInitArgs
        if integralType == OrbitIntegralType.POINCARE:
            supportMinus, supportPlus = self._refineFundamentalIntervals()
            integralInitArgs = {
                "supportMinus": supportMinus,
                "supportPlus": supportPlus,
                "sigMinus": sigma,
                "sigPlus": sigma,
            }
        if integralType == OrbitIntegralType.FUNDAMENTAL_DOMAIN:
            supportReal, supportImag = self._refineFundamentalDomain()
            integralInitArgs = {
                "supportReal": supportReal,
                "supportImag": supportImag,
                "sigma": sigma,
            }
        if integralType == OrbitIntegralType.CONSTANT:
            integralInitArgs = {}

        return integralInitArgs

    def _refineFundamentalIntervals(
        self,
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        TODO.
        """
        return np.array([], dtype=np.float64), np.array([], dtype=np.float64)

    def _refineFundamentalDomain(
        self,
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        TODO.
        """
        return np.array([], dtype=np.float64), np.array([], dtype=np.float64)

    # docstr-coverage: inherited
    def __call__(self, s: tVec, nMax: int) -> tMatVec:
        dynDetf = self._weightedZeta.calcDynamicalDeterminant(
            s, nMax=nMax, dMax=1
        )
        return dynDetf[:, 0, 1, :, :] / dynDetf[:, 1, 0, :, :]
