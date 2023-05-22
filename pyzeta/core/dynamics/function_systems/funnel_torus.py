"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from numpy import array, cos, cosh, exp, float64, pi, sin, sinh, sqrt

from pyzeta.core.dynamics.function_systems.schottky_exception import (
    InvalidSchottkyException,
)
from pyzeta.core.dynamics.function_systems.schottky_surface import (
    SchottkySurface,
)


class FunnelTorus(SchottkySurface):
    "Class representation of a torus with one funnel attached."

    __slots__ = ("l1", "l2", "phi")

    def __init__(self, outerLen: float, innerLen: float, angle: float) -> None:
        """
        TODO.
        """
        self.len1, self.len2, self.phi = outerLen, innerLen, angle
        self.logger.info("initializing %s", str(self))

        gen1 = [[exp(self.len1 / 2.0), 0.0], [0.0, exp(-self.len1 / 2.0)]]
        gen2 = [
            [
                cosh(self.len2 / 2.0) - cos(self.phi) * sinh(self.len2 / 2.0),
                sinh(self.len2 / 2.0) * sin(self.phi) ** 2,
            ],
            [
                sinh(self.len2 / 2.0),
                cosh(self.len2 / 2.0) + cos(self.phi) * sinh(self.len2 / 2.0),
            ],
        ]

        try:
            super().__init__(array([gen1, gen2], dtype=float64))
        except InvalidSchottkyException as error:
            raise ValueError(f"can't create {self}!") from error

    def __str__(self) -> str:
        "Simple string representation of a funneled torus."
        phiFrac = pi / self.phi
        return (
            f"FunnelTorus({self.len1:.4g}, {self.len2:.4g}, pi/{phiFrac:.4g})"
        )


class GeometricFunnelTorus(SchottkySurface):
    "More geometric class representation of a torus with one funnel attached."

    __slots__ = ("len", "width", "twist")

    def __init__(
        self, outerLen: float, funnelWidth: float, twist: float
    ) -> None:
        """
        TODO.
        """
        self.len, self.width, self.twist = outerLen, funnelWidth, twist
        self.logger.info("creating %s", str(self))

        gen1 = [[exp(self.len / 2.0), 0.0], [0.0, exp(-self.len / 2.0)]]
        b = sqrt((1 + cosh(self.width / 2)) / 2) / (sinh(self.len / 2))
        a = sqrt(1 + b**2)
        gen2 = [
            [exp(self.twist / 2.0) * a, exp(self.twist / 2.0) * b],
            [exp(-self.twist / 2.0) * b, exp(-self.twist / 2.0) * a],
        ]

        try:
            super().__init__(array([gen1, gen2], dtype=float64))
        except InvalidSchottkyException as error:
            raise ValueError(f"can't create {self}!") from error

    def __str__(self) -> str:
        "Simple string representation of a geometric funneled torus."
        length, width, twist = self.len, self.width, self.twist
        return f"GeometricFunnelTorus({length:.4g}, {width:.4g}, {twist:.4g})"
