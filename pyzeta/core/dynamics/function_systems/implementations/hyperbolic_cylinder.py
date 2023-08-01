"""
Module hyperbolic_cylinder.py from the core package of the `PyZeta` project.

Authors:\n
- Philipp Schuette\n
- Sebastian Albrecht\n
"""

from typing import Tuple

import numpy as np

from pyzeta.core.dynamics.function_systems.moebius_system import (
    MoebiusFunctionSystem,
    MoebiusMapSystem,
)
from pyzeta.core.dynamics.function_systems.schottky_exception import (
    InvalidSchottkyException,
)
from pyzeta.core.dynamics.function_systems.schottky_surface import (
    SchottkySurface,
)
from pyzeta.core.pyzeta_types.general import (
    tBoolMat,
    tIndexVec,
    tMatVec,
    tVec,
    tWordVec,
)


class HyperbolicCylinder(SchottkySurface):
    r"""
    Class representation a hyperbolic cylinder, i.e. the single topological
    possibility for a Schottky surface of rank one.
    """

    __slots__ = ("width",)

    def __init__(self, funnelWidth: float) -> None:
        """
        Initialize a hyperbolic cylinder.

        This Schottky surface is determined by a single parameter representing
        the diameter of the cylinder at its most narrow point (fundamental
        closed geodesic).

        :param funnelWidth: width of the cylinder at its most narrow point
        """
        self.width = funnelWidth
        self.logger.info("creating %s", str(self))
        gen = [[np.exp(self.width / 2), 0], [0, np.exp(-self.width / 2)]]

        try:
            super().__init__(np.array([gen], dtype=np.float64))
        except InvalidSchottkyException as error:
            raise ValueError(f"can't create {self}!") from error

    def __str__(self) -> str:
        "Simple string representation of a hyperbolic cylinder."
        return f"HyperbolicCylinder({self.width:.4g})"


class HyperbolicCylinderMap(MoebiusMapSystem):
    "Class representing hyperbolic cylinders as hyperbolic map systems."

    __slots__ = ("cylinderSystem",)

    def __init__(self, funnelWidth: float) -> None:
        """
        Initialize a hyperbolic map system representation of the hyperbolic
        cylinder. This map system delegates most work to an associated function
        system.

        :param funnelWidth: width of the cylinder at its most narrow point
        """
        self.cylinderSystem = HyperbolicCylinder(funnelWidth=funnelWidth)

    # docstr-coverage: inherited
    @property
    def fundamentalIntervals(self) -> Tuple[Tuple[float, float], ...]:
        raise NotImplementedError()

    # TODO: put this into abstract base class!
    # docstr-coverage: inherited
    @property
    def adjacencyMatrix(self) -> tBoolMat:
        return self.cylinderSystem.adjacencyMatrix

    # TODO: put this into abstract base class!
    # docstr-coverage: inherited
    def getStabilities(self, words: tWordVec) -> Tuple[tVec, tVec]:
        contractingStabs = self.cylinderSystem.getStabilities(words)
        return contractingStabs, 1 / contractingStabs

    # docstr-coverage: inherited
    def getPeriodicPoints(self, words: tWordVec) -> Tuple[tVec, tVec]:
        raise NotImplementedError()

    def getGenerators(self, indices: tIndexVec) -> tMatVec:
        raise NotImplementedError()


class FlowAdaptedCylinder(MoebiusFunctionSystem):
    "Class representation of flow adapted hyperbolic cylinders."


class FlowAdaptedCylinderMap(MoebiusMapSystem):
    "Class representation of flow adapted cylinders as hyperbolic map systems."
