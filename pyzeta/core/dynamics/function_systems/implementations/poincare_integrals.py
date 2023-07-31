"""
Module containing an implementation of the orbit integral provider. This
method for integral calculation corresponds to Gaussians supported on the
canonical Poincare section of the underlying hyperbolic map system which in
terms of Ruelle distributions is restriction to this Poincare section.

Authors:\n
- Philipp Schuette\n
"""

import numpy as np

from pyzeta.core.dynamics.function_systems.integral_provider import (
    IntegralProvider,
)
from pyzeta.core.pyzeta_types.general import tIntegralVec, tWordVec


class PoincareSectionIntegrals(IntegralProvider):
    "Class representing orbit integrals w.r.t. weights on a Poincare section."

    __slots__ = ("domainMinus", "domainPlus", "sigMinus", "sigPlus")

    def __init__(self, sigMinus: float, sigPlus: float) -> None:
        """
        TODO.
        """
        # TODO: construct domains from args; verify consistency of dimensions
        self.domainMinus = ...
        self.domainPlus = ...
        # TODO: resolve and save map system
        self.sigMinus = sigMinus
        self.sigPlus = sigPlus

    # docstr-coverage: inherited
    def getOrbitIntegrals(self, words: tWordVec) -> tIntegralVec:
        # TODO: ported from FunnelIFS
        integrals = np.zeros(
            (words.shape[0], *self.domainMinus.shape[0]),
            dtype=np.float64,
        )
        if words.shape[0] == 0:
            return integrals
        # define constants for later re-use
        denomMinus = self.sigMinus**2
        denomPlus = self.sigPlus**2
        # calculate orbit integrals on Poincare section by shuffeling letters
        for _ in range(words.shape[1]):
            # calculate current intersection with Poincare section
            xMinus, xPlus = self._mapSystem.getPeriodicPoints(words)
            # xMinus, xPlus = self.getPeriodicPoints(words, model)
            xMinus = xMinus.reshape(-1, 1, 1)
            xPlus = xPlus.reshape(-1, 1, 1)

            # calculate (main contribution to) period integrals
            integrals += np.exp(
                -np.power(self.domainMinus - xMinus, 2) / denomMinus
                - np.power(self.domainPlus - xPlus, 2) / denomPlus
            )

            # prepare for next intersection with Poincare section
            words = np.roll(words, -1, axis=1)

        return integrals / (np.pi * self.sigMinus * self.sigPlus)
