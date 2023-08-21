"""
Core module containing a concrete implementation of the abstract base class
`AbstractRuelleDistribution` based on Moebius hyperbolic map systems.

Authors:\n
- Philipp Schuette\n
"""

from math import ceil
from typing import List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from pyzeta.core.distributions.abstract_ruelle import (
    AbstractRuelleDistribution,
)
from pyzeta.core.dynamics.function_systems.map_system import (
    HyperbolicMapSystem,
)
from pyzeta.core.dynamics.function_systems.moebius_system import (
    MoebiusMapSystem,
)
from pyzeta.core.dynamics.symbolic_dynamics.abstract_dynamics import (
    AbstractSymbolicDynamics,
)
from pyzeta.core.pyzeta_types.general import tMatVec, tVec
from pyzeta.core.pyzeta_types.integral_arguments import tOrbitIntegralInitArgs
from pyzeta.core.pyzeta_types.integrals import OrbitIntegralType
from pyzeta.core.pyzeta_types.map_systems import MapSystemType
from pyzeta.core.pyzeta_types.symbolics import SymbolicDynamicsType
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
        numSupportPts: int,
        refinementLevel: int = 0,
        *,
        minusIndices: Optional[Tuple[int, ...]] = None,
        plusIndices: Optional[Tuple[int, ...]] = None,
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

        integralInitArgs = self._createIntegralInitArgs(
            integralType,
            sigma,
            numSupportPts,
            refinementLevel,
            minusIndices,
            plusIndices,
        )

        self._weightedZeta = container.tryResolve(
            AbstractWeightedZeta,
            zetaType=WeightedZetaType.WEIGHTED,
            mapSystem=mapSystem,
            systemInitArgs=systemInitArgs,
            integralType=integralType,
            integralInitArgs=integralInitArgs,
        )

    def _createIntegralInitArgs(
        self,
        integralType: OrbitIntegralType,
        sigma: float,
        numSupportPts: int,
        refinementLevel: int = 0,
        minusIndices: Optional[Tuple[int, ...]] = None,
        plusIndices: Optional[Tuple[int, ...]] = None,
    ) -> tOrbitIntegralInitArgs:
        """
        TODO.
        """
        integralInitArgs: tOrbitIntegralInitArgs
        if integralType == OrbitIntegralType.POINCARE:
            supportMinus, supportPlus = self._refineFundamentalIntervals(
                numSupportPts, refinementLevel, minusIndices, plusIndices
            )
            integralInitArgs = {
                "supportMinus": supportMinus,
                "supportPlus": supportPlus,
                "sigMinus": sigma,
                "sigPlus": sigma,
            }
        if integralType == OrbitIntegralType.FUNDAMENTAL_DOMAIN:
            supportReal, supportImag = self._refineFundamentalDomain(
                numSupportPts, refinementLevel
            )
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
        suppPts: int,
        refinementLevel: int,
        minusIdx: Optional[Tuple[int, ...]] = None,
        plusIdx: Optional[Tuple[int, ...]] = None,
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        TODO.
        """
        # use symbolic dynamics to refine the original fundamental intervals by
        # application of iterates of generators
        endpts: List[Tuple[float, float]] = []
        if refinementLevel <= 0:
            endpts = list(self._system.fundamentalIntervals)
        else:
            if not isinstance(self._system, MoebiusMapSystem):
                raise NotImplementedError(
                    "Ruelle distribution domain refinement not available for "
                    + str(self._system)
                )

            container = ContainerProvider.getContainer()
            symbDyn = container.tryResolve(
                AbstractSymbolicDynamics,
                symbolicsType=SymbolicDynamicsType.NON_REDUCED,
                adjacencyMatrix=self._system.adjacencyMatrix,
            )
            words = list(
                symbDyn.wordGenerator(refinementLevel, cyclRed=True),
            )[-1][0]

            for word in words:
                for i, interval in enumerate(
                    self._system.fundamentalIntervals
                ):
                    if self._system.adjacencyMatrix[word[0]][i]:  # TODO!
                        for letter in word:
                            (a, b), (c, d) = self._system.getGenerators(
                                np.array([[letter]], dtype=np.uint8)
                            )[0]
                            x, y = interval
                            xx = (a * x + b) / (c * x + d)
                            yy = (a * y + b) / (c * y + d)
                            endpts.append((xx, yy))

            endpts.sort(key=lambda x: x[0])

        # choose the correct intervals from `endpts` according to the (valid)
        # entries in `minusIdx`, `plusIdx` if given
        if minusIdx and plusIdx:
            maxIdx = len(endpts)
            minusIdx = tuple(
                xMinus for xMinus in minusIdx if 0 <= xMinus < maxIdx
            )
            plusIdx = tuple(xPlus for xPlus in plusIdx if 0 <= xPlus < maxIdx)

            endptsMinus = [endpts[idx] for idx in minusIdx]
            endptsPlus = [endpts[idx] for idx in plusIdx]
        else:
            endptsMinus = endpts
            endptsPlus = endpts

        return (
            self._getDomainFromEndpts(endptsMinus, suppPts),
            self._getDomainFromEndpts(endptsPlus, suppPts),
        )

    def _getDomainFromEndpts(
        self, endpts: List[Tuple[float, float]], suppPts: int
    ) -> NDArray[np.float64]:
        """
        Convenience function that calculates suitably spaced support points
        from a given list of interval endpoints and a given number of (total)
        support points.

        TODO.
        """
        # the pixel resolution of the individual fundamental intervals gets
        # scaled according to their actual size
        totalSize: float = 0
        for xMin, xMax in endpts:
            totalSize += np.abs(xMax - xMin)

        domainList: List[float] = []
        for xMin, xMax in endpts:
            numPts = ceil(np.abs(xMax - xMin) / totalSize * suppPts)
            domainList.extend(np.linspace(xMin, xMax, numPts))
        return np.array(domainList, dtype=np.float64)

    def _refineFundamentalDomain(
        self, numSupportPts: int, refinementLevel: int = 0
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        TODO.
        """
        if refinementLevel <= 0:
            pad = 1e-2
            leftEnd = np.array(self._system.fundamentalIntervals).min() - pad
            rightEnd = np.array(self._system.fundamentalIntervals).max() + pad
            supportReal = np.linspace(leftEnd, rightEnd, numSupportPts)
            supportImag = np.linspace(
                pad, (rightEnd - leftEnd) / 2 + pad, numSupportPts
            )
        # TODO: do not silently ignore minusIndices, plusIndices!
        else:
            raise NotImplementedError(
                "domain refinement not yet implemented for fundamental domain!"
            )
        return supportReal, supportImag

    # docstr-coverage: inherited
    def __call__(self, s: tVec, nMax: int) -> tMatVec:
        dynDetf = self._weightedZeta.calcDynamicalDeterminant(
            s, nMax=nMax, dMax=1
        )
        return dynDetf[:, 0, 1, :, :] / dynDetf[:, 1, 0, :, :]
