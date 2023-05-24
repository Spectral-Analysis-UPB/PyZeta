"""
Module hyperbolic_cylinder.py from the core package of the `PyZeta` project.

Authors:\n
- Philipp Schuette\n
- Sebastian Albrecht\n
"""

import numpy as np

from pyzeta.core.dynamics.function_systems.schottky_exception import (
    InvalidSchottkyException,
)
from pyzeta.core.dynamics.function_systems.schottky_surface import (
    SchottkySurface,
)


class HyperbolicCylinder(SchottkySurface):
    r"""
    Class representation a hyperbolic cylinder, i.e. the single topological
    possibility for a Schottky surface of rank one.
    """

    __slots__ = ("width",)

    def __init__(self, funnelWidth: float) -> None:
        r"""
        Initiliaze a hyperbolic cylinder.

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
