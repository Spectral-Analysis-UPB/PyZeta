"""
Module containing a class representation of geodesic on hyperbolic space. In
particular the class abstracts the translation procedure between the upper
halfplane and Poincare disc models and facilitates a homogeneous interface for
geometric operations and visualization.

Authors:\n
- Tobias Weich\n
- Philipp Schuette\n
- Sebastian Albrecht\n
"""

from __future__ import annotations

from cmath import isclose
from typing import Any, Optional, Tuple

import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from matplotlib import patches

from pyzeta.geometry.constants import tScal
from pyzeta.geometry.geometry_exceptions import (
    InvalidDiskPoint,
    InvalidGeodesicException,
    InvalidHalfplanePoint,
    InvalidModelException,
)
from pyzeta.geometry.helpers import DtoH, HtoD, stabilize


class Geodesic:
    r"""
    Utility class representing a geodesic in the Upper Halfplane
    :math:`\mathbb{H}` or in the Poincare Disk :math:`\mathbb{D}` through two
    given points of the respective model.
    """

    __slots__ = ("_model", "t", "u", "m", "r", "td", "ud", "md", "rd")

    def __init__(self, z1: tScal, z2: tScal, model: str = "H"):
        r"""
        Create a hyperbolic geodesic through two points `z1` and `z2`.

        The geodesic can be created in the Upper Halfplane :math:`\mathbb{H}`
        or in the Poincare Disk :math:`\mathbb{D}`. The model can be specified
        when a geodesic is newly created, and the behaviour of any class method
        adopts to this choice. Nevertheless, any class method supports
        the keyword argument `model` to allow for one-time changes of the
        model.

        :param z1: Point in the chosen `model`
        :param z2: Point in the chosen `model`
        :param model: Model for hyperbolic space ('H' or 'D'), defaults to 'H'
        :raises InvalidDiskPoint: Raised if outside Poincare disc
        :raises InvalidHalfplanePoint: Raised if outside upper halfplane
        :raises InvalidModelException: Raised if `model` is neither 'H' nor 'D'
        :raises InvalidGeodesicException: Raised if both points are identical
        """
        if z1 == z2:
            raise InvalidGeodesicException(z1, z2)
        if model == "D":
            z1 = stabilize(z1, model=model)  # improve numerical stability
            z2 = stabilize(z2, model=model)  # improve numerical stability
            if abs(z1) > 1:
                raise InvalidDiskPoint(z1)
            if abs(z2) > 1:
                raise InvalidDiskPoint(z2)
            z1 = DtoH(z1)
            z2 = DtoH(z2)
        elif model == "H":
            z1 = stabilize(z1, model=model)  # improve numerical stability
            z2 = stabilize(z2, model=model)  # improve numerical stability
            if z1.imag < 0:
                raise InvalidHalfplanePoint(z1)
            if z2.imag < 0:
                raise InvalidHalfplanePoint(z2)
        else:
            raise InvalidModelException(model)

        self._model = model

        if z1 == np.infty:
            self.m = self.r = self.u = np.infty
            self.t = z2.real
        elif z2 == np.infty:
            self.m = self.r = self.u = np.infty
            self.t = z1.real
        else:
            x1, y1 = z1.real, z1.imag
            x2, y2 = z2.real, z2.imag
            if x1 == x2:
                self.m = self.r = self.u = np.infty
                self.t = x1
            else:
                self.m = (
                    0.5 * (x1**2 - x2**2 + y1**2 - y2**2) / (x1 - x2)
                )
                self.r = np.sqrt((x1 - self.m) ** 2 + y1**2)
                self.t = self.m - self.r
                self.u = self.m + self.r
        self.td = HtoD(self.t)
        self.ud = HtoD(self.u)
        phiU = np.angle(self.ud)
        phiT = np.angle(self.td)
        phiInt = abs(phiT - phiU)
        if abs(phiInt - np.pi) < 1e-4:
            self.md = np.infty
            self.rd = np.infty
        else:
            phiMean = (phiT + phiU) / 2.0
            if abs(phiMean - phiT) > np.pi / 2.0:
                phiMean = phiMean + np.pi
            distCenter = 1.0 / abs(np.cos(phiInt / 2.0))
            self.md = distCenter * np.exp(1j * phiMean)
            self.rd = abs(np.sin(phiInt / 2.0)) * distCenter

    def __str__(self) -> str:
        r"""
        Return string representation of a hyperbolic geodesic.

        The string representation is model specific. For geodesics on the Upper
        Halfplane :math:`\mathbb{H}`, the string has the form
        'Geodesic_on_H(t, u)', where t and u are the endpoints of the geodesic
        on the real line (or at infinity). For geodesics on the Poincare Disk
        :math:`\mathbb{D}`, it has the form 'Geodesic_on_D(phi_t, phi_u)',
        where phi_t and phi_u are the anglular coordinates of the endpoints on
        the unit circle.

        :return: String representation of a geodesic
        """
        if self._model == "H":
            return f"Geodesic_on_H({self.t:.4g}, {self.u:.4g})"
        tAngle = np.angle(self.td) / np.pi
        uAngle = np.angle(self.ud) / np.pi
        return f"Geodesic_on_D({tAngle:.4g}pi, {uAngle:.4g}pi)"

    @property
    def model(self) -> str:
        "Getter method for the `model` attribute of a Geodesic instance."
        return self._model

    @model.setter
    def model(self, m: str) -> None:
        "Setter method for the `model` attribute of a Geodesic instance."
        m = m.upper()
        if m in {"H", "D"}:
            self._model = m
        else:
            raise InvalidModelException(m)

    def plot(
        self, *, inftyMax: float = 5.0, ax: Any = None, **kwargs: object
    ) -> Tuple[Any, Any]:
        r"""
        Plot a hyperbolic geodesic.

        :param inftyMax: Value at which the imaginary axis is cropped if
            the geodesic extends to :math:`\infty`, defaults to 5
        :param ax: Matplotlib axes object in which the plot should be drawn. If
            None is passed, a new figure and axes are created, defaults to None
        :param \*\*kwargs: Valid keyword arguments include 'color',
            'linestyle', 'linewidth', 'marker' and 'markersize'. Further
            matplotlib.lines.Line2D properties and matplotlib.patch
            properties work (but may not be reliable).
        :return: Matplotlib figure and matplotlib axes object in which the plot
            is drawn
        """
        model = self.model

        # place keyword arguments specifing markers into separate dictionary
        markerKwargs = {}
        for key, item in kwargs.items():
            if "marker" in key:
                markerKwargs[key] = item
        for key in markerKwargs:
            kwargs.pop(key)
        # TODO: Process kwargs that specify the text annotations in the plots
        # (textsize, textfont, ...)

        # set default values for certain kwargs if they have not been passed
        kwargs["color"] = kwargs.get("color", kwargs.get("c", "green"))
        kwargs.pop("c", None)
        markerKwargs["clip_on"] = kwargs.get("clip_on", False)

        # set maximal imag part on 'H' depending on default and circle size
        if self.r != np.infty:
            inftyMax = 1.2 * self.r
        # set center of real part on 'H' depending on circle position
        if self.r == np.infty:
            center = self.t
        else:
            center = self.m

        if ax is None:
            _, ax = plt.subplots(tight_layout=True)
        else:
            upper = max(ax.get_xlim()[1], center + inftyMax)
            lower = min(ax.get_xlim()[0], center - inftyMax)
            center = (upper + lower) / 2.0
            inftyMax = (upper - lower) / 2.0
        ax.set_aspect(aspect="equal")

        if model == "H":
            ax.set_xlim(center - inftyMax, center + inftyMax)
            ax.set_ylim(0, inftyMax)
            ax.text(
                1,
                1,
                r"$\mathbb{H}$",
                horizontalalignment="right",
                verticalalignment="top",
                transform=ax.transAxes,
                fontsize="xx-large",
            )
        else:
            ax.set_xlim(-1.01, 1.01)
            ax.set_ylim(-1.01, 1.01)
            ax.text(
                1,
                1,
                r"$\mathbb{D}$",
                horizontalalignment="right",
                verticalalignment="top",
                transform=ax.transAxes,
                fontsize="xx-large",
            )
        ax.set_xlabel(r"$\Re(z)$")
        ax.set_ylabel(r"$\Im(z)$")

        if model == "H":
            if self.r == np.infty:
                ax.plot(
                    [self.t.real, self.u.real],
                    [self.t.imag, self.u.imag],
                    ls="",
                    color=kwargs["color"],
                    **markerKwargs,
                )
                ax.axline((self.t, 0), (self.t, inftyMax), **kwargs)
                ax.text(
                    self.t,
                    0.99 * inftyMax,
                    r"$\!\! \uparrow \!\! \infty$",
                    horizontalalignment="left",
                    verticalalignment="top",
                    fontsize="x-large",
                )
            else:
                ax.plot(
                    [self.t.real, self.u.real],
                    [self.t.imag, self.u.imag],
                    ls="",
                    color=kwargs["color"],
                    **markerKwargs,
                )
                arc = patches.Arc(
                    (self.m, 0),
                    2 * self.r,
                    2 * self.r,
                    theta1=0,
                    theta2=180,
                    **kwargs,
                )
                ax.add_patch(arc)
        else:
            circle = patches.Arc((0, 0), 2, 2, lw=0.5)
            ax.add_patch(circle)

            phiU = np.angle(self.ud, deg=True)
            phiT = np.angle(self.td, deg=True)
            phiInt = abs(phiT - phiU)

            if isclose(phiInt, 180.0, abs_tol=1e-4):
                ax.plot(
                    [self.td.real, self.ud.real],
                    [self.td.imag, self.ud.imag],
                    ls="",
                    color=kwargs["color"],
                    **markerKwargs,
                )
                ax.plot(
                    [self.td.real, self.ud.real],
                    [self.td.imag, self.ud.imag],
                    **kwargs,
                )
            else:
                phiMean = np.angle(self.md, deg=True)
                theta2 = abs(180 - phiInt) / 2.0
                theta1 = -theta2
                offset = phiMean + 180

                ax.plot(
                    [self.td.real, self.ud.real],
                    [self.td.imag, self.ud.imag],
                    ls="",
                    color=kwargs["color"],
                    **markerKwargs,
                )
                arc = patches.Arc(
                    (self.md.real, self.md.imag),
                    2 * self.rd,
                    2 * self.rd,
                    theta1=theta1,
                    theta2=theta2,
                    angle=offset,
                    **kwargs,
                )
                ax.add_patch(arc)

        return ax.get_figure(), ax

    def intersect(self, other: Geodesic) -> Optional[Tuple[float, float]]:
        r"""
        Calculate the intersection point of a hyperbolic geodesics with another
        one.

        The model for hyperbolic space is inferred from the model of the
        geodesic `self`.

        :param other: Other geodesic intersecting given one in a single point.
        :raises ValueError: Raised if the two geodesics are identical.
        :return: Coordinates of the intersection point
        """
        if self.t == other.t and self.u == other.u:
            raise ValueError(
                "Tried to compute intersect of two identical geodesics"
            )

        model = self.model

        if self.r == np.infty:
            if other.r == np.infty:
                xx, yy = np.infty, np.infty
            elif self.t <= other.u:
                xx = self.t
                yy = np.sqrt(other.r**2 - (other.m - xx) ** 2)
            else:
                return None
        else:
            if other.r == np.infty:
                xx = other.t
                yy = np.sqrt(self.r**2 - (self.m - xx) ** 2)
            elif (
                (self.u - other.u)
                * (other.u - self.t)
                * (self.t - other.t)
                * (other.t - self.u)
            ) <= 0:
                xx = 0.5 * (
                    (self.r**2 - other.r**2 - self.m**2 + other.m**2)
                    / (other.m - self.m)
                )
                yy = np.sqrt(self.r**2 - (xx - self.m) ** 2)
            else:
                return None

        if model == "D":
            if xx == np.infty:
                xx = -1.0
                yy = 0.0
            else:
                point = complex(xx, yy)
                point = (1j - point) / (1j + point)
                xx, yy = point.real, point.imag

        return xx, yy

    def getReflecAxis(self, other: Geodesic) -> Geodesic:
        r"""
        Calculate the reflection axis between a hyperbolic geodesic on the
        Upper Halfplane :math:`\mathbb{H}` and another non-intersecting one.

        Reflection at the axis transforms the two geodesics into one another.
        The reflection axis is itself a geodesic.

        :param other: Geodesic which does not intersect the first one
        :raises NotImplementedError: Raised if any of the two geodesics extends
            to :math:`\infty`.
        :return: Reflection axis
        """
        a1, b1 = sorted((self.t, other.t))
        a2, b2 = sorted((self.u, other.u))

        if b2 == np.infty:
            raise NotImplementedError(
                "Computation of reflection axis of "
                + "geodesics going to infty not "
                + "implemented"
            )
        elif abs(a1 - a2 + b2 - b1) < 1e-9:
            c1 = np.infty
            c2 = 0.5 * (a1 + b2)
        else:
            c1 = (
                np.sqrt(b2 - b1)
                * np.sqrt(b2 - a2)
                * (b1 + a2)
                * np.sqrt(b1 - a1)
                * np.sqrt(a2 - a1)
                - a1 * a2 * b2
                - a2 * b1**2
                - ((a1 - 2 * a2) * b2 - 2 * a1 * a2 + a2**2) * b1
            ) / (
                2
                * np.sqrt(b2 - b1)
                * np.sqrt(b2 - a2)
                * np.sqrt(b1 - a1)
                * np.sqrt(a2 - a1)
                + (b2 + a1) * b1
                - (2 * a1 - a2) * b2
                + a1 * a2
                - a2**2
                - b1**2
            )
            c2 = -(
                np.sqrt(b2 - b1)
                * np.sqrt(b2 - a2)
                * np.sqrt(b1 - a1)
                * np.sqrt(a2 - a1)
                - a1 * b2
                + a2 * b1
            ) / (a1 - a2 + b2 - b1)
        geo = Geodesic(c1, c2)

        return geo
