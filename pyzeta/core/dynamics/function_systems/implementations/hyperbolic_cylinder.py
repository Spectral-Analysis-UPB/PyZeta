"""
Module hyperbolic_cylinder.py from the core package of the `PyZeta` project.

Authors:\n
- Philipp Schuette\n
- Sebastian Albrecht\n
"""

from typing import List, Tuple

import numpy as np

from pyzeta.core.dynamics.function_systems.moebius_system import (
    MoebiusFunctionSystem,
    MoebiusMapSystem,
)
from pyzeta.core.dynamics.function_systems.schottky_exception import (
    InvalidSchottkyException,
)
from pyzeta.core.dynamics.function_systems.schottky_system import (
    SchottkyFunctionSystem,
    SchottkyMapSystem,
)
from pyzeta.core.pyzeta_types.general import tMatVec


class HyperbolicCylinder(SchottkyFunctionSystem):
    """
    Class representation a hyperbolic cylinder, i.e. the single topological
    possibility for a Schottky surface of rank one.
    """

    __slots__ = ("width",)

    def __init__(self, funnelWidth: float, rotate: bool) -> None:
        """
        Initialize a hyperbolic cylinder.

        This Schottky surface is determined by a single parameter representing
        the diameter of the cylinder at its most narrow point (fundamental
        closed geodesic).

        :param funnelWidth: width of the cylinder at its most narrow point
        :param rotate: flag indicating whether to rotate cylinder
        """
        self.width = funnelWidth
        self.logger.info("creating %s", str(self))
        if not rotate:
            gen = [[np.exp(self.width / 2), 0], [0, np.exp(-self.width / 2)]]
        else:
            gen = [
                [np.cosh(self.width / 2), np.sinh(self.width / 2)],
                [np.sinh(self.width / 2), np.cosh(self.width / 2)],
            ]

        try:
            super().__init__(np.array([gen], dtype=np.float64))
        except InvalidSchottkyException as error:
            raise ValueError(f"can't create {self}!") from error

    def __str__(self) -> str:
        "Simple string representation of a hyperbolic cylinder."
        return f"HyperbolicCylinder({self.width:.4g})"


class HyperbolicCylinderMap(SchottkyMapSystem):
    "Class representing hyperbolic cylinders as hyperbolic map systems."

    def __init__(self, funnelWidth: float) -> None:
        """
        Initialize a Moebius hyperbolic map system representation of the
        hyperbolic cylinder. The underlying flow adapted cylinder is always
        rotated to obtain sensible fundamental intervals.

        :param funnelWidth: width of the cylinder at its most narrow point
        """
        super().__init__(
            HyperbolicCylinder(funnelWidth=funnelWidth, rotate=True)
        )


class FlowAdaptedCylinder(MoebiusFunctionSystem):
    "Class representation of flow adapted hyperbolic cylinders."

    __slots__ = ("width",)

    def __init__(self, funnelWidth: float, rotate: bool) -> None:
        """
        Initialize a flow adapted (hyperbolic) cylinder.

        :param funnelWidth: width of the cylinder at its most narrow point
        """
        self.width = funnelWidth
        self.logger.info("creating %s", str(self))
        generators = self._createGenerators(rotate=rotate)
        adjacencyMatrix = np.array(
            [[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0]],
            dtype=np.bool_,
        )

        try:
            super().__init__(
                generators=generators, adjacencyMatrix=adjacencyMatrix
            )
        except InvalidSchottkyException as error:
            raise ValueError(f"can't create {self}!") from error

    def __str__(self) -> str:
        "Simple string representation of a hyperbolic cylinder."
        return f"HyperbolicCylinder({self.width:.4g})"

    def _createGenerators(self, rotate: bool) -> tMatVec:
        """
        Create the pair of generators and their inverses for a flow adapted
        cylinder. Generators may be create either rotated or not.

        :param rotate: flag indicating whether generators should be rotated
        :return: array of generators
        """
        if not rotate:
            gen1 = [[0, np.exp(self.width / 4)], [np.exp(-self.width / 4), 0]]
            gen2 = [[0, np.exp(-self.width / 4)], [np.exp(self.width / 4), 0]]
        else:
            gen1 = [
                [np.cosh(self.width / 4), np.sinh(self.width / 4)],
                [-np.sinh(self.width / 4), -np.cosh(self.width / 4)],
            ]
            gen2 = [
                [np.cosh(self.width / 4), -np.sinh(self.width / 4)],
                [np.sinh(self.width / 4), -np.cosh(self.width / 4)],
            ]
        generators = [gen1, gen2, gen1, gen2]
        return np.array(generators, dtype=np.float64)


class FlowAdaptedCylinderMap(MoebiusMapSystem):
    "Class representation of flow adapted cylinders as hyperbolic map systems."

    __slots__ = ("_fundInter",)

    def __init__(self, funnelWidth: float) -> None:
        """
        Initialize a Moebius hyperbolic map system representation of the flow
        adapted (hyperbolic) cylinder. The underlying flow adapted cylinder is
        always rotated to obtain sensible fundamental intervals.

        :param funnelWidth: width of the cylinder at its most narrow point
        """
        super().__init__(FlowAdaptedCylinder(funnelWidth, rotate=True))

        self._fundInter, deltaOffset = self._getFundamentalIntervals()
        self._addTranslationToReflections(deltaOffset)

    def _getFundamentalIntervals(
        self,
    ) -> Tuple[Tuple[Tuple[float, float], ...], float]:
        """
        TODO.
        """
        firstHalf: List[Tuple[float, float]] = []
        for reflection in self._functionSystem.phi[:2]:
            radius = 1.0 / reflection[1, 0]
            midPoint = reflection[0, 0] * radius
            firstHalf.append((midPoint - abs(radius), midPoint + abs(radius)))
        deltaOffset = firstHalf[1][1] - firstHalf[0][0] + 1
        secondHalf: List[Tuple[float, float]] = []
        for interval in firstHalf:
            secondHalf.append(
                (interval[0] + deltaOffset, interval[1] + deltaOffset)
            )

        return tuple(firstHalf + secondHalf), deltaOffset

    def _addTranslationToReflections(self, deltaOffset: float) -> None:
        """
        TODO.
        """
        translation = np.array([[1, deltaOffset], [0, 1]], dtype=np.float64)
        translationInv = np.array(
            [[1, -deltaOffset], [0, 1]], dtype=np.float64
        )
        for i, reflection in enumerate(self._functionSystem.phi[:2]):
            self._functionSystem.phi[i] = translation @ reflection
        for i, reflection in enumerate(self._functionSystem.phi[2:]):
            self._functionSystem.phi[i + 2] = reflection @ translationInv

    # docstr-coverage: inherited
    @property
    def fundamentalIntervals(self) -> Tuple[Tuple[float, float], ...]:
        return self._fundInter
