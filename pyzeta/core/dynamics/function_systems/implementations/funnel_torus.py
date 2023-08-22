"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from numpy import array, cos, cosh, exp, float64, pi, sin, sinh, sqrt

from pyzeta.core.dynamics.function_systems.schottky_exception import (
    InvalidSchottkyException,
)
from pyzeta.core.dynamics.function_systems.schottky_system import (
    SchottkyFunctionSystem,
    SchottkyMapSystem,
)


class FunnelTorus(SchottkyFunctionSystem):
    "Class representation of a torus with one funnel attached."

    __slots__ = ("l1", "l2", "varphi")

    def __init__(
        self,
        outerLen: float,
        innerLen: float,
        angle: float,
        rotate: bool = True,
    ) -> None:
        """
        TODO.
        """
        self.len1, self.len2, self.varphi = outerLen, innerLen, angle
        self.logger.info("initializing %s", str(self))

        gen1 = array(
            [[exp(self.len1 / 2.0), 0.0], [0.0, exp(-self.len1 / 2.0)]]
        )
        gen2 = array(
            [
                [
                    cosh(self.len2 / 2.0)
                    - cos(self.varphi) * sinh(self.len2 / 2.0),
                    sinh(self.len2 / 2.0) * sin(self.varphi) ** 2,
                ],
                [
                    sinh(self.len2 / 2.0),
                    cosh(self.len2 / 2.0)
                    + cos(self.varphi) * sinh(self.len2 / 2.0),
                ],
            ]
        )
        if rotate:
            rotation = array(
                [[cos(pi / 8), sin(pi / 8)], [-sin(pi / 8), cos(pi / 8)]],
                dtype=float64,
            )
            rotationInv = array(
                [[cos(pi / 8), -sin(pi / 8)], [sin(pi / 8), cos(pi / 8)]],
                dtype=float64,
            )
            gen1 = rotationInv @ gen1 @ rotation
            gen2 = rotationInv @ gen2 @ rotation

        try:
            super().__init__(array([gen1, gen2], dtype=float64))
        except InvalidSchottkyException as error:
            raise ValueError(f"can't create {self}!") from error

    def __str__(self) -> str:
        "Simple string representation of a funneled torus."
        phiFrac = pi / self.varphi
        return (
            f"FunnelTorus({self.len1:.4g}, {self.len2:.4g}, pi/{phiFrac:.4g})"
        )


class FunnelTorusMap(SchottkyMapSystem):
    "Class representing funneled tori as hyperbolic map systems."

    def __init__(self, outerLen: float, innerLen: float, angle: float) -> None:
        """
        TODO.
        """
        super().__init__(
            FunnelTorus(outerLen=outerLen, innerLen=innerLen, angle=angle)
        )


class GeometricFunnelTorus(SchottkyFunctionSystem):
    "More geometric class representation of a torus with one funnel attached."

    __slots__ = ("len", "width", "twist")

    def __init__(
        self,
        outerLen: float,
        funnelWidth: float,
        twist: float,
        rotate: bool = True,
    ) -> None:
        """
        TODO.
        """
        self.len, self.width, self.twist = outerLen, funnelWidth, twist
        self.logger.info("creating %s", str(self))

        b = sqrt((1 + cosh(self.width / 2)) / 2) / (sinh(self.len / 2))
        a = sqrt(1 + b**2)
        if not rotate:
            gen1 = [[exp(self.len / 2.0), 0.0], [0.0, exp(-self.len / 2.0)]]
            gen2 = [
                [exp(self.twist / 2.0) * a, exp(self.twist / 2.0) * b],
                [exp(-self.twist / 2.0) * b, exp(-self.twist / 2.0) * a],
            ]
        else:
            gen1 = [
                [cosh(self.len / 2), sinh(self.len / 2)],
                [sinh(self.len / 2), cosh(self.len / 2)],
            ]
            gen2 = [
                [
                    (a - b) * cosh(self.twist / 2),
                    (a + b) * sinh(self.twist / 2),
                ],
                [
                    (a - b) * sinh(self.twist / 2),
                    (a + b) * cosh(self.twist / 2),
                ],
            ]

        try:
            super().__init__(array([gen1, gen2], dtype=float64))
        except InvalidSchottkyException as error:
            raise ValueError(f"can't create {self}!") from error

    def __str__(self) -> str:
        "Simple string representation of a geometric funneled torus."
        length, width, twist = self.len, self.width, self.twist
        return f"GeometricFunnelTorus({length:.4g}, {width:.4g}, {twist:.4g})"


class GeometricFunnelTorusMap(SchottkyMapSystem):
    "Class representing geometric funneled tori as hyperbolic map systems."

    def __init__(
        self, outerLen: float, funnelWidth: float, twist: float
    ) -> None:
        """
        TODO.
        """
        super().__init__(
            GeometricFunnelTorus(
                outerLen=outerLen, funnelWidth=funnelWidth, twist=twist
            )
        )
