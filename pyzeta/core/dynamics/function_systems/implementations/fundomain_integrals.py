"""
Module containing an implementation of the orbit integral provider. This
method for integral calculation corresponds to Gaussian test functions constant
in the fiber coordinate of phase space which in terms of Ruelle distributions
is push-forward along the bundle projection.

Authors:\n
- Philipp Schuette\n
"""

from typing import Tuple

import numpy as np

from pyzeta.core.dynamics.function_systems.integral_provider import (
    IntegralProvider,
)
from pyzeta.core.dynamics.function_systems.moebius_system import (
    MoebiusMapSystem,
)
from pyzeta.core.pyzeta_types.general import tIntegralVec, tVec, tWordVec


class FundamentalDomainIntegrals(IntegralProvider):
    """
    Class representation of orbit integrals w.r.t. weights on the fundamental
    domain and constant in the fiber.
    """

    __slots__ = ("_mapSystem", "_domain", "sigma")

    def __init__(
        self,
        mapSystem: MoebiusMapSystem,
        supportReal: tVec,
        supportImag: tVec,
        sigma: float,
    ) -> None:
        """
        TODO.
        """
        self._mapSystem = mapSystem
        # create support points in the upper half plane
        gridReal, gridImag = np.meshgrid(supportReal, supportImag)
        self.domain = np.array(gridReal + 1j * gridImag)
        self.sigma = sigma

    # docstr-coverage: inherited
    def getOrbitIntegrals(self, words: tWordVec) -> tIntegralVec:
        integrals = np.zeros(
            (words.shape[0], *self.domain.shape), dtype=np.float64
        )
        if words.shape[0] == 0:
            return integrals

        xMinus, xPlus = self._mapSystem.getPeriodicPoints(words)

        # rotate and translate fixed points to standard config (0, infinity)
        angles = np.arctan(1.0 / xPlus)
        rotations = np.array(
            [
                [
                    [np.cos(angle), np.sin(angle)],
                    [-np.sin(angle), np.cos(angle)],
                ]
                for angle in angles
            ],
            dtype=np.float64,
        )
        offsets = (rotations[:, 0, 0] * xMinus + rotations[:, 0, 1]) / (
            rotations[:, 1, 0] * xMinus + rotations[:, 1, 1]
        )
        translations = np.array(
            [[[1, -offset], [0, 1]] for offset in offsets], dtype=np.float64
        )
        symmetries = np.array(
            [
                translation @ rotation
                for translation, rotation in zip(translations, rotations)
            ]
        )

        # use domain in the shape (words.shape[0], domain.shape)
        domain = self.domain.reshape(1, *self.domain.shape)
        for i in range(words.shape[1]):
            # iterate the domain (support points) along the orbit
            generators = self._mapSystem.getGenerators(words[:, i])
            domain = (generators[:, 0, 0] * domain + generators[:, 0, 1]) / (
                generators[:, 1, 0] * domain + generators[:, 1, 1]
            )
            # Rotate domain onto standard vertical geodesic:
            movedDomain = (
                symmetries[:, 0, 0] * domain + symmetries[:, 0, 1]
            ) / (symmetries[:, 1, 0] * domain + symmetries[:, 1, 1])
            assert np.all(
                movedDomain.imag != 0
            ), "moved domain outside upper halfplane"

            integrals += np.exp(
                -(movedDomain.real**2)
                / ((self.sigma * movedDomain.imag) ** 2)
            )

        return integrals / (np.sqrt(np.pi) * self.sigma)  # type: ignore

    # docstr-coverage: inherited
    @property
    def integralShape(self) -> Tuple[int, int]:
        shape = self.domain.shape
        if len(shape) != 2:
            raise ValueError(
                "incompatible shape of fundamental domain integrals!"
            )
        return shape  # type: ignore
