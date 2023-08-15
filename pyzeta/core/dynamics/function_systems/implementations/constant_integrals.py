"""
Module containing a straightforward implementation of constant period
integrals.

Authors:\n
- Philipp Schuette\n
"""

from typing import Tuple

from pyzeta.core.dynamics.function_systems.integral_provider import (
    IntegralProvider,
)
from pyzeta.core.pyzeta_types.general import tIntegralVec, tWordVec


class ConstantIntegrals(IntegralProvider):
    """
    Class representation of constant orbit integrals.
    """

    def __init__(self) -> None:
        """
        Initialize a new class representation of constant orbit integrals.
        Instances refuse any attempt to calculate integrals because constant
        weights should not be calculated on two-dimensional arrays but instead
        via `calcA` on weighted zeta function instances.
        """

    # docstr-coverage: inherited
    def getOrbitIntegrals(self, words: tWordVec) -> tIntegralVec:
        raise ValueError(
            "cannot retrieve orbit integrals from constant provider!"
        )

    # docstr-coverage: inherited
    @property
    def integralShape(self) -> Tuple[int, int]:
        raise ValueError(
            "cannot retrieve orbit integral shape from constant provider!"
        )
