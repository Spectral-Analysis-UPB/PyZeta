#!/usr/bin/python3
"""
Module hypgeo.py from the PyZeta project.
It provides utility methods and classes for hyperbolic geometry.

Authors:\n
- Tobias Weich\n
- Philipp Schuette\n
- Sebastian Albrecht\n
"""

from cmath import isclose
from logging import DEBUG
from typing import Any, Final, List, Optional, Tuple, Union, overload

import matplotlib.pyplot as plt
import numpy as np
import numpy.linalg as lin
from matplotlib import patches
from numpy.typing import NDArray
from scipy.optimize import root_scalar

from pyzeta.zeta_logger import initZetaLogger

# define some custom types here to avoid circular imports in zeta_types.py:
tScal = Union[float, complex]
tVec = NDArray[np.complex128]
tMat = NDArray[np.complex128]

#################
# Logging Setup #
#################

logger = initZetaLogger("hypgeo", __name__)


####################
# Global Constants #
####################

# in our convention we have the following correspondence 'H' -> 'D':
# 0 -> 1, 1 -> 1j, infty -> -1, -1 -> -1j
CAYLEY: Final[np.ndarray] = np.array([[-1., 1.j], [1., 1.j]])
INV_CAYLEY: Final[np.ndarray] = np.array([[1., -1.], [1.j, 1.j]])


#####################
# Custom Exceptions #
#####################

class InvalidModelException(Exception):
    r"""
    Raised when input model parameter is neither 'H' (Upper Halfplane) nor 'D'
    (Poincare Disk).
    """

    def __str__(self) -> str:
        return f"InvalidModelException({self.args[0]})"


class InvalidDiskPoint(Exception):
    r"""
    Raised when input points expected inside the Poincare Disk have
    absolute value larger than one.
    """

    def __str__(self) -> str:
        return f"InvalidDiskPoint({self.args[0]})"


class InvalidHalfplanePoint(Exception):
    r"""
    Raised when input points expected inside the Upper Half Plane have
    imaginary part less than zero.
    """

    def __str__(self) -> str:
        return f"InvalidHalfplanePoint({self.args[0]})"


class InvalidGeodesicException(Exception):
    r"""
    Raised when a unique geodesic curve cannot be created through a given
    pair of points.
    """

    def __init__(self, val1: tScal, val2: tScal) -> None:
        r"""
        Raise an exception that no valid geodesic exists through the points
        `val1` and `val2`.

        :param val1: Point on the complex plane
        :type val1: float or complex
        :param val2: Point on the complex plane
        :type val2: float or complex
        """
        super().__init__((val1, val2))

    def __str__(self) -> str:
        return f"Cannot create unique geodesic from {self.args[0]}"


class InvalidMatrixException(Exception):
    r"""
    Raised when input matrix expected in certain Matrix Group does not satisfy
    the defining group properties.
    """

    def __str__(self) -> str:
        return f"InvalidSymmetryException({self.args[0]})"


######################################
# Improvement of numerical stability #
######################################

@overload
def stabilize(z: tScal, model: str = "H", tol: float = 1e-9) -> tScal: ...


@overload
def stabilize(z: tVec, model: str = "H", tol: float = 1e-9) -> tVec: ...


def stabilize(z: Union[tScal, tVec], model: str = "H", tol: float = 1e-9
              ) -> Union[tScal, tVec]:
    r"""
    Stabilize copmutations in the module by taking care of small numerical
    errors that push boundary points out of the respective model.

    From the mathematical theory it is usualy clear that results of
    computations in this module are points that lie inside the Hyperbolic Plane
    :math:`\mathbb{H}` or the Poincare Disk :math:`\mathbb{D}` (or on their
    respective boundaries). In some cases, numerical computations produce very
    small errors (< 10^-9) that lie outside the respective boundary (i.e.
    points with very small negative imaginary part, in the case of
    :math:`\mathbb{H}`, or with absolute value very small above 1, in the case
    of :math:`\mathbb{D}`).

    :param z: Point or vector in the chosen `model`
    :type z: float or complex or numpy.ndarray
    :param model: Model for hyperbolic space ('H' or 'D'), defaults to 'H'
    :type model: str, optional
    :param tol: Absolute tolerance, defaults to 1e-9
    :type tol: float, optional
    :raises InvalidModelException: Raised if `model` is neither 'H' nor 'D'.
    :return: Point or vector with very small errors (within the specified
            `tolerance`) removed.
    :rtype: float or complex or numpy.ndarray
    """
    model = model.upper()
    if model == "H":
        if isinstance(z, np.ndarray):  # if z is a vector
            mask = np.logical_and(np.isclose(z.imag, 0., rtol=0., atol=tol),
                                  z.imag < 0.)
            if np.any(mask):
                logger.warning(f"stabilizing numerical values in {z}")
                z = np.where(mask, z.real, z)
        elif (isclose(z.imag, 0., rel_tol=0, abs_tol=tol)
              and z.imag < 0.):  # if z is a scalar
            logger.warning(f"stabilizing numerical value of {z}")
            z = z.real
    elif model == "D":
        if isinstance(z, np.ndarray):  # if z is a vector
            mask = np.logical_and(np.isclose(np.abs(z), 1., rtol=0., atol=tol),
                                  np.abs(z) > 1.)
            if np.any(mask):
                logger.warning(f"stabilizing numerical values in {z}")
                z = np.where(mask, z/abs(z), z)
        elif (isclose(abs(z), 1., rel_tol=0., abs_tol=tol)
              and abs(z) > 1.):  # if z is a scalar
            logger.warning(f"stabilizing numerical value of {z}")
            z = z/abs(z)
    else:
        raise InvalidModelException(model)
    return z


def HtoD(z: tScal) -> complex:
    r"""
    Map point from the Upper Halfplane to the Poincare Disk.

    The Cayley transformation
    :math:`C = \begin{pmatrix} -1 & i \\ 1 & i \end{pmatrix}` maps the Upper
    Halfplane :math:`\mathbb{H}` onto the Poincare Disk :math:`\mathbb{D}`.

    :param z: Point on the Upper Halfplane
    :type z: float or complex
    :return: Point on the Poincare Disk
    :rtype: float or complex
    """
    res: complex
    cT = CAYLEY
    if abs(z) == np.infty:
        res = cT[0, 0] / cT[1, 0]
    else:
        res = (cT[0, 0]*z + cT[0, 1]) / (cT[1, 0]*z + cT[1, 1])

    # convert to float to satisfy optional static type checking; could be
    # removed with proper type annotation for `tVec`:
    res = complex(res)

    res = stabilize(res, model="D")  # improve numerical stability
    return res


def DtoH(z: tScal) -> complex:
    r"""
    Map point from the Poincare Disk to the Upper Halfplane.

    The inverse Cayley transformation
    :math:`C = \begin{pmatrix} 1 & -1 \\ i & i \end{pmatrix}` maps the Poincare
    Disk :math:`\mathbb{D}` onto the Upper Halfplane :math:`\mathbb{H}`.

    :param z: Point on the Poincare Disk
    :type z: float or complex
    :return: Point on the Upper Halfplane
    :rtype: float or complex
    """
    res: complex
    icT = INV_CAYLEY
    if z == -(icT[1, 0] / icT[1, 1]):
        res = np.infty
    else:
        res = (icT[0, 0]*z + icT[0, 1]) / (icT[1, 0]*z + icT[1, 1])

    # convert to float to satisfy optional static type checking; could be
    # removed with proper type annotation for `tVec`:
    res = complex(res)

    res = stabilize(res, model="H")  # improve numerical stability
    return res


#############################
# Hyperbolic Geodesic Class #
#############################

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
        :type z1: float or complex
        :param z2: Point in the chosen `model`
        :type z2: float or complex
        :param model: Model for hyperbolic space ('H' or 'D'), defaults to 'H'
        :type model: str, optional
        :raises InvalidDiskPoint: Raised for points outside Poincare Disk.
        :raises InvalidHalfplanePoint: Raised for points outside Upper
            Halfplane.
        :raises InvalidModelException: Raised if `model` is neither 'H' nor
            'D'.
        :raises InvalidGeodesicException: Raised if both points are identical.
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
            logger.info(f"creating disk geodesic through ({z1:.4g}, " +
                        f"{z2:.4g})")
            z1 = DtoH(z1)
            z2 = DtoH(z2)
        elif model == "H":
            z1 = stabilize(z1, model=model)  # improve numerical stability
            z2 = stabilize(z2, model=model)  # improve numerical stability
            if z1.imag < 0:
                raise InvalidHalfplanePoint(z1)
            if z2.imag < 0:
                raise InvalidHalfplanePoint(z2)
            logger.info(f"creating halfplane geodesic through ({z1:.4g}, " +
                        f"{z2:.4g})")
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
                self.m = 0.5 * (x1**2 - x2**2 + y1**2 - y2**2) / (x1 - x2)
                self.r = np.sqrt((x1 - self.m)**2 + y1**2)
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
            phiMean = (phiT + phiU) / 2.
            if abs(phiMean - phiT) > np.pi / 2.:
                phiMean = phiMean + np.pi
            distCenter = 1. / abs(np.cos(phiInt / 2.))
            self.md = distCenter * np.exp(1j * phiMean)
            self.rd = abs(np.sin(phiInt / 2.)) * distCenter

        if self._model == "H":
            logger.debug("created halfplane geodesic has parameters " +
                         f"t={self.t:.4g}, u={self.u:.4g}, m={self.m:.4g}, " +
                         f"r={self.r:.4g}")
        else:
            logger.debug("created disk geodesic has parameters " +
                         f"td={self.td:.4g}, ud={self.ud:.4g}, " +
                         f"md={self.md:.4g}, rd={self.rd:.4g}")

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
        :rtype: str
        """
        if self._model == "H":
            return f"Geodesic_on_H({self.t:.4g}, {self.u:.4g})"
        tAngle = np.angle(self.td) / np.pi
        uAngle = np.angle(self.ud) / np.pi
        return f"Geodesic_on_D({tAngle:.4g}pi, {uAngle:.4g}pi)"

    @property
    def model(self) -> str:
        r"""Getter method for the `model` attribute of a Geodesic instance."""
        return self._model

    @model.setter
    def model(self, m: str) -> None:
        r"""Setter method for the `model` attribute of a Geodesic instance."""
        m = m.upper()
        if m in {"H", "D"}:
            self._model = m
        else:
            raise InvalidModelException(m)

    def plot(self, *, inftyMax: float = 5., ax: Any = None, **kwargs
             ) -> Tuple[Any, Any]:
        r"""
        Plot a hyperbolic geodesic.

        :param inftyMax: Value at which the imaginary axis is cropped if
            the geodesic extends to :math:`\infty`, defaults to 5
        :type inftyMax: float, optional
        :param ax: Matplotlib axes object in which the plot should be drawn. If
            None is passed, a new figure and axes are created, defaults to None
        :type ax: matplotlib.axes.Axes, optional
        :param \*\*kwargs: Valid keyword arguments include 'color',
            'linestyle', 'linewidth', 'marker' and 'markersize'. Further
            matplotlib.lines.Line2D properties and matplotlib.patch
            properties work (but may not be reliable).
        :return: Matplotlib figure and matplotlib axes object in which the plot
            is drawn
        :rtype: matplotlib.figure.Figure, matplotlib.axes.Axes
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
            inftyMax = 1.2*self.r
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
            center = (upper + lower) / 2.
            inftyMax = (upper - lower) / 2.
        ax.set_aspect(aspect="equal")

        if model == "H":
            ax.set_xlim(center - inftyMax, center + inftyMax)
            ax.set_ylim(0, inftyMax)
            ax.text(1, 1, r"$\mathbb{H}$", horizontalalignment="right",
                    verticalalignment="top", transform=ax.transAxes,
                    fontsize="xx-large")
        else:
            ax.set_xlim(-1.01, 1.01)
            ax.set_ylim(-1.01, 1.01)
            ax.text(1, 1, r"$\mathbb{D}$", horizontalalignment="right",
                    verticalalignment="top", transform=ax.transAxes,
                    fontsize="xx-large")
        ax.set_xlabel(r"$\Re(z)$")
        ax.set_ylabel(r"$\Im(z)$")

        if model == "H":
            if self.r == np.infty:
                ax.plot([self.t.real, self.u.real],
                        [self.t.imag, self.u.imag], ls="",
                        color=kwargs["color"], **markerKwargs)
                ax.axline((self.t, 0), (self.t, inftyMax), **kwargs)
                ax.text(self.t, 0.99*inftyMax, r"$\!\! \uparrow \!\! \infty$",
                        horizontalalignment="left", verticalalignment="top",
                        fontsize="x-large")
            else:
                ax.plot([self.t.real, self.u.real],
                        [self.t.imag, self.u.imag], ls="",
                        color=kwargs["color"], **markerKwargs)
                arc = patches.Arc((self.m, 0), 2*self.r, 2*self.r, theta1=0,
                                  theta2=180, **kwargs)
                ax.add_patch(arc)
        else:
            circle = patches.Arc((0, 0), 2, 2, lw=0.5)
            ax.add_patch(circle)

            phiU = np.angle(self.ud, deg=True)
            phiT = np.angle(self.td, deg=True)
            phiInt = abs(phiT - phiU)

            if isclose(phiInt, 180., abs_tol=1e-4):
                ax.plot([self.td.real, self.ud.real],
                        [self.td.imag, self.ud.imag], ls="",
                        color=kwargs["color"], **markerKwargs)
                ax.plot([self.td.real, self.ud.real],
                        [self.td.imag, self.ud.imag], **kwargs)
            else:
                phiMean = np.angle(self.md, deg=True)
                theta2 = abs(180 - phiInt) / 2.
                theta1 = - theta2
                offset = phiMean + 180

                ax.plot([self.td.real, self.ud.real],
                        [self.td.imag, self.ud.imag], ls="",
                        color=kwargs["color"], **markerKwargs)
                arc = patches.Arc((self.md.real, self.md.imag), 2*self.rd,
                                  2*self.rd, theta1=theta1, theta2=theta2,
                                  angle=offset, **kwargs)
                ax.add_patch(arc)

        logger.debug("plotted %s in model %s", str(self), model)
        return ax.get_figure(), ax

    def intersect(self, other) -> Optional[Tuple[float, float]]:
        r"""
        Calculate the intersection point of a hyperbolic geodesics with another
        one.

        The model for hyperbolic space is inferred from the model of the
        geodesic `self`.

        :param other: Another geodesic which intersects the geodesic in a
            single point.
        :type other: Geodesic
        :raises ValueError: Raised if the two geodesics are identical.
        :return: Coordinates of the intersection point
        :rtype: Tuple[float, float]
        """
        if self.t == other.t and self.u == other.u:
            raise ValueError(
                "Tried to compute intersect of two identical geodesics"
            )

        model = self.model
        logger.info("computing %s-intersect of %s and %s",
                    model, str(self), str(other))
        if model != other.model:
            logger.warning("computing intersect of geodesics on different %s",
                           "models")

        if self.r == np.infty:
            if other.r == np.infty:
                xx, yy = np.infty, np.infty
            elif self.t <= other.u:
                xx = self.t
                yy = np.sqrt(other.r**2 - (other.m - xx)**2)
            else:
                logger.warning("found that %s and %s do not intersect",
                               str(self), str(other))
                return None
        else:
            if other.r == np.infty:
                xx = other.t
                yy = np.sqrt(self.r**2 - (self.m - xx)**2)
            elif ((self.u - other.u) * (other.u - self.t) *
                  (self.t - other.t) * (other.t - self.u)) <= 0:
                xx = 0.5 * ((self.r**2 - other.r**2 - self.m**2 + other.m**2)
                            / (other.m - self.m))
                yy = np.sqrt(self.r**2 - (xx - self.m)**2)
            else:
                logger.warning("found that %s and %s do not intersect",
                               str(self), str(other))
                return None

        if model == "D":
            if xx == np.infty:
                xx = -1.
                yy = 0.
            else:
                point = complex(xx, yy)
                point = (1j - point) / (1j + point)
                xx, yy = point.real, point.imag

        logger.debug("computed %s-intersect (%.3f, %.3f)", model, xx, yy)
        return xx, yy

    def getReflecAxis(self, other):
        r"""
        Calculate the reflection axis between a hyperbolic geodesic on the
        Upper Halfplane :math:`\mathbb{H}` and another non-intersecting one.

        Reflection at the axis transforms the two geodesics into one another.
        The reflection axis is itself a geodesic.

        :param other: Geodesic which does not intersect the first one
        :type other: Geodesic
        :raises NotImplementedError: Raised if any of the two geodesics extends
            to :math:`\infty`.
        :return: Reflection axis
        :rtype: Geodesic
        """
        logger.info(f"computing reflection axis for {self} and {other}")
        a1, b1 = sorted((self.t, other.t))
        a2, b2 = sorted((self.u, other.u))

        if b2 == np.infty:
            raise NotImplementedError("Computation of reflection axis of " +
                                      "geodesics going to infty not " +
                                      "implemented")
        elif abs(a1 - a2 + b2 - b1) < 1e-9:
            c1 = np.infty
            c2 = 0.5 * (a1 + b2)
        else:
            c1 = (
                (np.sqrt(b2 - b1) * np.sqrt(b2 - a2) * (b1 + a2)
                 * np.sqrt(b1 - a1) * np.sqrt(a2 - a1) - a1 * a2 * b2
                 - a2 * b1**2 - ((a1 - 2*a2)*b2 - 2*a1*a2 + a2**2) * b1)
                / (2 * np.sqrt(b2 - b1) * np.sqrt(b2 - a2)
                   * np.sqrt(b1 - a1) * np.sqrt(a2 - a1) + (b2 + a1)*b1
                   - (2*a1 - a2)*b2 + a1*a2 - a2**2 - b1**2)
            )
            c2 = (
                -(np.sqrt(b2 - b1) * np.sqrt(b2 - a2) * np.sqrt(b1 - a1)
                  * np.sqrt(a2 - a1) - a1 * b2 + a2 * b1) / (a1 - a2 + b2 - b1)
                  )
        geo = Geodesic(c1, c2)
        logger.debug(f"computed reflection axis {geo}")
        return geo


##################
# SL(2, R) Class #
##################


class SL2R:
    r"""
    Utility class representing symmetries of the Upper Halfplane
    :math:`\mathbb{H}`, i.e. elements of :math:`\mathrm{SL}(2, \mathbb{R})`.
    """

    __slots__ = "fixPt", "_A"

    def __init__(self, A: tMat):
        r"""
        Create an element of :math:`\mathrm{SL}(2, \mathbb{R})`.

        The class can represent both orientation-preserving and orientation-
        reversing transformations. True elements of
        :math:`\mathrm{SL}(2, \mathbb{R})` are orientation-preserving. However,
        it is useful for other parts of the hypgeo module that this class can
        represent matrices both with determinant +1 and -1.

        :param A: Matrix representation of an element of
            :math:`\mathrm{SL}(2, \mathbb{R})`. Be aware that an input matrix
            with non-unit determinant will be normalised to unit determinant up
            to sign.
        :type A: numpy.ndarray
        :raises InvalidMatrixException: Raised if `A` has zero determinant.
        """
        self.fixPt: Optional[Tuple[tScal, ...]] = None
        det = A[0, 0]*A[1, 1] - A[0, 1]*A[1, 0]
        if isclose(abs(det), 0., abs_tol=1e-6):
            logger.warning(f"trying to create SL2R symmetry with det {det}")
            raise InvalidMatrixException(A)

        logger.info(f"creating SL2R with {A.round(3)}")
        self._A = 1. / np.sqrt(abs(det)) * A
        logger.debug(f"created SL2R({self._A.round(3)})")

    def __str__(self) -> str:
        r"""
        Return string representation of an element of
        :math:`\mathrm{SL}(2, \mathbb{R})`.

        :return: String representation of an element of
            :math:`\mathrm{SL}(2, \mathbb{R})`
        :rtype: str
        """
        return f"SL2R({self._A.round(3)})"

    def __repr__(self) -> str:
        r"""
        Return string representation of an element of
        :math:`\mathrm{SL}(2, \mathbb{R})`.

        This method works identically as the __str__ method. It is necessary
        for a human readable string representation of lists of SL2R elements.

        :return: String representation of an element of
            :math:`\mathrm{SL}(2, \mathbb{R})`
        :rtype: str
        """
        return f"SL2R({self._A.round(3)})"

    @overload
    def __call__(self, z: Geodesic) -> Geodesic: ...

    @overload
    def __call__(self, z: tScal) -> tScal: ...

    @overload
    def __call__(self, z: tVec) -> tVec: ...

    def __call__(self, z: Union[Geodesic, tScal, tVec]
                 ) -> Union[Geodesic, tScal, tVec]:
        r"""
        Calculate action of an element of :math:`\mathrm{SL}(2, \mathbb{R})` on
        a point, vector or geodesic in the Upper Halfplane :math:`\mathbb{H}`.

        Elements
        :math:`g = \begin{pmatrix} a & b \\ c & d \end{pmatrix}
        \in\mathrm{SL}(2, \mathbb{R})` act on the Upper Halfplane
        :math:`\mathbb{H}` via Moebius trafos:

        .. math::

            \mathbb{H}\ni z\mapsto g\cdot z = \frac{az + b}{cz + d}\in
            \mathbb{H}.

        :param z: Point or vector or hyperbolic geodesic in the Upper Halfplane
            :math:`\mathbb{H}`
        :type z: float or complex or numpy.ndarray or Geodesic
        :raises InvalidHalfplanePoint: Raised for points outside Upper
            Halfplane.
        :return: Transformed input
        :rtype: float or complex or numpy.ndarray or Geodesic, same type as
            input `z`
        """
        a: float
        b: float
        c: float
        d: float
        [[a, b], [c, d]] = self._A
        logger.info("calling %s on %s", str(self), str(z))

        if isinstance(z, Geodesic):
            return Geodesic(self(z.t), self(z.u))

        if isinstance(z, np.ndarray):
            z = stabilize(z, model="H")  # improve numerical stability
            if np.any(np.imag(z) < 0.):
                invalidIdx = tuple(np.argwhere(np.imag(z) < 0.)[0])
                raise InvalidHalfplanePoint(z[invalidIdx])
            res = np.zeros_like(z)
            mask = (z != np.infty)

            res[mask] = (a*z[mask] + b) / (c*z[mask] + d)
            if c != 0:
                res[~mask] = a / c
            else:
                res[~mask] = np.infty
            return res

        z = stabilize(z, model="H")  # improve numerical stability
        if np.imag(z) < 0.:
            raise InvalidHalfplanePoint(z)
        if z != np.infty:
            return (a*z + b) / (c*z + d)
        if c != 0:
            return a / c
        return np.infty

    def __len__(self) -> float:
        r"""
        Calculate displacement length of a hyperbolic element of
        :math:`\mathrm{SL}(2, \mathbb{R})`.

        :raises ValueError: Raised if the element is not hyperbolic.
        :return: Displacement length
        :rtype: float
        """
        trace = np.abs(self._A[0, 0] + self._A[1, 1])
        if trace <= 2:
            raise ValueError(
                "Trying to calculate displacement length for element that is"
                + " not hyperbolic"
            )
        else:
            logger.info(f"computing displacement length of {self}")
            res: float = 2. * np.arccosh(trace / 2.)
            logger.debug(f"computed displacement length {res}")
            return res

    def __mul__(self, other):
        r"""
        Calculate matrix product of two elements of
        :math:`\mathrm{SL}(2, \mathbb{R})`.

        :param other: Element of :math:`\mathrm{SL}(2, \mathbb{R})`
        :type other: SL2R
        :return: Matrix product of the two elements
        :rtype: SL2R
        """
        return SL2R(np.matmul(self._A, other._A))

    def __pow__(self, power: int):
        r"""
        Calculate matrix power of an element of
        :math:`\mathrm{SL}(2, \mathbb{R})`.

        :param power: Power to which the element is raised
        :type power: int
        :return: Matrix power of the element
        :rtype: SL2R
        """
        return SL2R(lin.matrix_power(self._A, power))

    def inverse(self):
        r"""
        Calculate inverse of an element of :math:`\mathrm{SL}(2, \mathbb{R})`.

        The same as SL2R.__pow__(-1).

        :return: Inverse of the element
        :rtype: SL2R
        """
        return SL2R(lin.inv(self._A))

    def getFixPt(self) -> Optional[Tuple[tScal, ...]]:
        r"""
        Calculate fixed point(s) of an element of
        :math:`\mathrm{SL}(2, \mathbb{R})`.

        Uses Dal'Bo p.16. Only fixed point(s) inside :math:`\mathbb{H}` are
        returned. Fixed points outside :math:`\mathbb{H}` are discarded.

        :raises ValueError: Raised if the element is the unit element.
        :raises NotImplementedError: Raised if the element has negative
            determinant.
        :return: Fixed point(s)
        :rtype: None or tuple of float or tuple of complex
        """
        if self.fixPt is None:
            [[a, b], [c, d]] = self._A
            if a*d - b*c < 0:
                raise NotImplementedError("Fixed point comptutation for " +
                                          "orientation-reversing trafo " +
                                          "not implemented")
            elif [[a, b], [c, d]] == [[1, 0], [0, 1]]:
                raise ValueError("Trying to calculate fixed points of the " +
                                 "identity transformation")
            elif c == 0:
                logger.info(f"computing fixed point(s) of {self}")
                if not isclose(d, a):
                    self.fixPt = (b / (d - a), np.infty)
                else:
                    self.fixPt = (np.infty, )
            else:
                logger.info(f"computing fixed point(s) of {self}")
                # distinguish parabolic, elliptic, hyperbolic using trace
                trace = abs(a + d)
                # parabolic case:
                if isclose(trace, 2.):
                    x12 = (a - d) / (2. * c)
                    self.fixPt = (x12, )
                # hyperbolic case:
                elif trace > 2:
                    x1 = (a - d - np.sqrt(trace**2 - 4)) / (2.*c)
                    x2 = (a - d + np.sqrt(trace**2 - 4)) / (2.*c)
                    self.fixPt = (x1, x2)
                # elliptic case:
                else:
                    x12 = (
                        (a - d) / (2.*c) +
                        np.sqrt(4 - trace**2)*1j / (2.*abs(c))
                    )
                    self.fixPt = (x12, )
            logger.debug(f"computed fixed point(s) {self.fixPt}")

        return self.fixPt

    def plotFixPt(self, *, ax: Any = None, **kwargs) -> Tuple[Any, Any]:
        r"""
        Calculate and plot fixed point(s) of an element of
        :math:`\mathrm{SL}(2, \mathbb{R})`.

        :param ax: Matplotlib axes object in which the plot should be drawn. If
            None is passed, a new figure and axes are created, defaults to None
        :type ax: matplotlib.axes.Axes, optional
        :param \*\*kwargs: Keyword arguments are passed to
            matplotlib.pyplot.scatter().
        :raises ValueError: Raised if the element has no fixed points in
            :math:`\mathbb{H}`.
        :return: Matplotlib figure and matplotlib axes object in which the plot
            is drawn
        :rtype: matplotlib.figure.Figure, matplotlib.axes.Axes
        """
        fixPts = self.getFixPt()
        if fixPts is None:
            raise ValueError(f"{self} has no fixed point(s) in H")

        fixPts_ = [complex(fixPt) for fixPt in fixPts]
        x = [fixPt.real for fixPt in fixPts_]
        y = [fixPt.imag for fixPt in fixPts_]

        # set default values for certain kwargs if they have not been passed
        kwargs["color"] = kwargs.get("color", kwargs.get("c", "green"))
        kwargs.pop("c", None)
        kwargs["clip_on"] = kwargs.get("clip_on", False)

        if ax is None:
            _, ax = plt.subplots(tight_layout=True)

        ax.set_ylim(bottom=0)
        ax.set_xlabel(r"$\Re(z)$")
        ax.set_ylabel(r"$\Im(z)$")
        ax.text(1, 1, r"$\mathbb{H}$", horizontalalignment="right",
                verticalalignment="top", transform=ax.transAxes,
                fontsize="xx-large")

        ax.scatter(x, y, **kwargs)
        if np.infty in x:
            ax.scatter(0.5, 1, **kwargs, transform=ax.transAxes)
            ax.text(0.5, 1, r"$\infty$", horizontalalignment="right",
                    verticalalignment="bottom", fontsize="x-large",
                    transform=ax.transAxes)

        logger.debug("plotted fixed points {fixPts} of {self}")
        return ax.get_figure(), ax

    def getIsoCirc(self) -> Geodesic:  # rename once we are sure, what it does
        # ??? what does this method ???
        x1 = -self._A[1, 1] / self._A[1, 0] + np.abs(1. / self._A[1, 0])
        x2 = -self._A[1, 1] / self._A[1, 0] - np.abs(1. / self._A[1, 0])
        return Geodesic(x1, x2)

    def getTransAx(self) -> Geodesic:
        r"""
        Calculate translation axis of a hyperbolic element of
        :math:`\mathrm{SL}(2, \mathbb{R})`.

        The axis of translation of a hyperbolic element of
        :math:`\mathrm{SL}(2, \mathbb{R})` is the unique geodesic between the
        two fixed points. It is preserved under the action of the hyperbolic
        element.

        :raises ValueError: Raised if the element is not hyperbolic.
        :return: Translation axis
        :rtype: Geodesic
        """
        try:
            x1, x2 = self.getFixPt()  # type: ignore
        except (TypeError, ValueError, NotImplementedError) as error:
            raise ValueError(
                "Can only generate unique geodesic for hyperbolic elements"
            ) from error
        logger.info(f"computing translation axis of {self}")
        res = Geodesic(x1, x2, model="H")
        logger.debug(f"computed translation axis {res}")
        return res


##################
# SU(1, 1) Class #
##################

class SU11:
    r"""
    Utility class representing symmetries of the Poincare Disk, i.e.
    elements of :math:`\mathrm{SU}(1, 1)`.
    """

    __slots__ = "fixPt", "_A"

    def __init__(self, A: tMat):
        r"""
        Create an element of :math:`\mathrm{SU}(1,1)`.

        The class can represent both orientation-preserving and orientation-
        reversing transformations. True elements of
        :math:`\mathrm{SU}(1,1)` are orientation-preserving. However,
        it is useful for other parts of the hypgeo module that this class can
        represent matrices both with determinant +1 and -1.

        :param A: Matrix representation of an element of
            :math:`\mathrm{SU}(1,1)`. Be aware that an input matrix
            with non-unit determinant will be normalised to unit determinant up
            to sign.
        :type A: numpy.ndarray
        :raises InvalidMatrixException: Raised if `A` has zero
            determinant or if it does not satisfy other defining properties of
            :math:`\mathrm{SU}(1,1)`.
        """
        self.fixPt: Optional[Tuple[float, ...]] = None
        det = abs(A[0, 0])**2 - abs(A[0, 1])**2
        if (isclose(abs(det), 0., abs_tol=1e-6)
                or not isclose(A[0, 0].conjugate(), A[1, 1])
                or not isclose(A[0, 1].conjugate(), A[1, 0])):
            logger.warning(
                "trying to create SU11 symmetry from invalid mat %s %s %.3f",
                str(A.round(3)), "with det", det
            )
            raise InvalidMatrixException(A)

        logger.info("creating SU11 from matrix %s", str(A.round(3)))
        self._A = 1. / np.sqrt(abs(det)) * A
        logger.debug("created SU11(%s)", str(self._A.round(3)))

    def __str__(self) -> str:
        r"""
        Return string representation of an element of :math:`\mathrm{SU}(1,1)`.

        :return: String representation of an element of
            :math:`\mathrm{SU}(1,1)`
        :rtype: str
        """
        return f"SU11({self._A.round(3)})"

    def __repr__(self) -> str:
        r"""
        Return string representation of an element of :math:`\mathrm{SU}(1,1)`.

        This method works identically as the __str__ method. It is necessary
        for a human readable string representation of lists of SU11 elements.

        :return: String representation of an element of
            :math:`\mathrm{SU}(1,1)`
        :rtype: str
        """
        return f"SU11({self._A.round(3)})"

    @overload
    def __call__(self, z: Geodesic) -> Geodesic: ...

    @overload
    def __call__(self, z: tScal) -> tScal: ...

    @overload
    def __call__(self, z: tVec) -> tVec: ...

    def __call__(self, z: Union[Geodesic, tScal, tVec]
                 ) -> Union[Geodesic, tScal, tVec]:
        r"""
        Calculate action of an element of :math:`\mathrm{SU}(1,1)` on
        a point, vector or geodesic in the Poincare Disk :math:`\mathbb{D}`.

        Elements
        :math:`g = \begin{pmatrix} a & b \\ b^* & a^* \end{pmatrix}
        \in\mathrm{SU}(1,1)` act on the Poincare Disk
        :math:`\mathbb{D}` via Moebius trafos:

        .. math::

            \mathbb{D}\ni z\mapsto g\cdot z = \frac{az + b}{b^*z + a^*}\in
            \mathbb{D}.

        :param z: Point or vector or hyperbolic geodesic in the Poincare Disk
            :math:`\mathbb{D}`
        :type z: float or complex or numpy.ndarray or Geodesic
        :raises InvalidDiskPoint: Raised for points outside Poincare Disk.
        :return: Transformed input
        :rtype: float or complex or numpy.ndarray or Geodesic, same type as
            input `z`
        """
        a: complex
        b: complex
        c: complex
        d: complex
        [[a, b], [c, d]] = self._A
        logger.info(f"calling {self} on {z}")

        if isinstance(z, Geodesic):
            return Geodesic(self(z.td), self(z.ud), model="D")
        if isinstance(z, np.ndarray):
            z = stabilize(z, model="D")  # improve numerical stability
            if np.any(np.abs(z) > 1.):
                invalidIdx = tuple(np.argwhere(np.abs(z) > 1.)[0])
                raise InvalidDiskPoint(z[invalidIdx])
            return np.ndarray((a*z + b) / (c*z + d))

        z = stabilize(z, model="D")  # improve numerical stability
        if np.abs(z) > 1.:
            raise InvalidDiskPoint(z)
        return (a*z + b) / (c*z + d)

    def __len__(self) -> float:
        r"""
        Calculate displacement length of a hyperbolic element of
        :math:`\mathrm{SU}(1,1)`.

        :raises ValueError: Raised if the element is not hyperbolic.
        :return: Displacement length
        :rtype: float
        """
        trace = np.abs(self._A[0, 0] + self._A[1, 1])
        if trace <= 2:
            raise ValueError(
                "Trying to calculate displacement length for element that is"
                + " not hyperbolic"
            )
        logger.info("computing displacement length of %s", str(self))
        res: float = 2. * np.arccosh(trace / 2.)
        logger.debug("computed displacement length %.3f", res)
        return res

    def __mul__(self, other):
        r"""
        Calculate matrix product of two elements of :math:`\mathrm{SU}(1,1)`.

        :param other: Element of :math:`\mathrm{SU}(1,1)`.
        :type other: SU11
        :return: Matrix product of the two elements
        :rtype: SU11
        """
        return SU11(np.matmul(self._A, other._A))

    def __pow__(self, power: int):
        r"""
        Calculate matrix power of an element of :math:`\mathrm{SU}(1,1)`.

        :param power: Power to which the element is raised
        :type power: int
        :return: Matrix power of the element
        :rtype: SU11
        """
        return SU11(lin.matrix_power(self._A, power))

    def inverse(self):
        r"""
        Calculate inverse of an element of :math:`\mathrm{SU}(1,1)`.

        The same as SU11.__pow__(-1).

        :return: Inverse of the element
        :rtype: SU11
        """
        return SU11(lin.inv(self._A))

    def getFixPt(self) -> Optional[Tuple[tScal, ...]]:
        r"""
        Calculate fixed point(s) of an element of :math:`\mathrm{SU}(1,1)`.

        Only fixed point(s) inside :math:`\mathbb{D}` are returned. Fixed
        points outside :math:`\mathbb{D}` are discarded.

        :raises ValueError: Raised if the element is the unit element.
        :raises NotImplementedError: Raised if the element has negative
            determinant.
        :return: Fixed point(s) inside :math:`\mathbb{D}`
        :rtype: None or tuple of float or tuple of complex
        """
        if self.fixPt is None:
            [[a, b], [c, d]] = self._A
            if a*d - b*c < 0:
                raise NotImplementedError("Fixed point comptutation for " +
                                          "orientation-reversing trafo " +
                                          "not implemented")
            elif [[a, b], [c, d]] == [[1, 0], [0, 1]]:
                raise ValueError("Trying to calculate fixed points of the " +
                                 "identity transformation")
            elif c == 0:
                logger.info(f"computing fixed point(s) of {self}")
                self.fixPt = (0., )
            else:
                logger.info(f"computing fixed point(s) of {self}")
                # distinguish parabolic, elliptic, hyperbolic using trace
                trace = abs(a + d)
                # parabolic case:
                if isclose(trace, 2.):
                    x12 = (a - d) / (2. * c)
                    self.fixPt = (x12, )
                # hyperbolic case:
                elif trace > 2.:
                    x1 = (a - d - np.sqrt(trace**2 - 4)) / (2.*c)
                    x2 = (a - d + np.sqrt(trace**2 - 4)) / (2.*c)
                    self.fixPt = (x1, x2)
                # elliptic case:
                else:
                    x12 = (abs(a - d)*1j - np.sqrt(4 - trace**2)*1j) / (2.*c)
                    self.fixPt = (x1, x2)
            logger.info(f"computed fixed point(s) {self.fixPt} of {self}")

        return self.fixPt

    def plotFixPt(self, *, ax: Any = None, **kwargs) -> Tuple[Any, Any]:
        r"""
        Calculate and plot fixed point(s) of an element of
        :math:`\mathrm{SU}(1, 1)`.

        :param ax: Matplotlib axes object in which the plot should be drawn. If
            None is passed, a new figure and axes are created, defaults to None
        :type ax: matplotlib.axes.Axes, optional
        :param \*\*kwargs: Keyword arguments are passed to
            matplotlib.pyplot.scatter().
        :raises ValueError: Raised if the element has no fixed points in
            :math:`\mathbb{D}`.
        :return: Matplotlib figure and matplotlib axes object in which the plot
            is drawn
        :rtype: matplotlib.figure.Figure, matplotlib.axes.Axes
        """
        fixPts = self.getFixPt()
        if fixPts is None or fixPts == ():
            raise ValueError(f"{self} has no fixed point(s) in D")

        logger.info(f"Plot fixed points {fixPts} of {self}")
        fixPts_ = [complex(fixPt) for fixPt in fixPts]
        x = [fixPt.real for fixPt in fixPts_]
        y = [fixPt.imag for fixPt in fixPts_]

        # set default values for certain kwargs if they have not been passed
        kwargs["color"] = kwargs.get("color", kwargs.get("c", "green"))
        kwargs.pop("c", None)
        kwargs["clip_on"] = kwargs.get("clip_on", False)

        if ax is None:
            _, ax = plt.subplots(tight_layout=True)
        ax.set_xlim(-1.01, 1.01)
        ax.set_ylim(-1.01, 1.01)
        ax.set_aspect(aspect="equal")
        ax.text(1, 1, r"$\mathbb{D}$", horizontalalignment="right",
                verticalalignment="top", transform=ax.transAxes,
                fontsize="xx-large")
        ax.set_xlabel(r"$\Re(z)$")
        ax.set_ylabel(r"$\Im(z)$")

        circle = patches.Arc((0, 0), 2, 2)
        ax.add_patch(circle)

        ax.scatter(x, y, **kwargs)

        logger.debug("plotted fixed points {fixPts} of {self}")
        return ax.get_figure(), ax

    def getIsoCirc(self) -> Geodesic:  # rename once we are sure what it does
        # ??? what does this method ???
        g = INV_CAYLEY @ self._A @ CAYLEY
        det = g[0, 0] * g[1, 1] - g[0, 1] * g[1, 0]
        g = 1. / np.sqrt(abs(det)) * g

        x1 = -g[1, 1] / g[1, 0] + np.abs(1. / g[1, 0])
        x2 = -g[1, 1] / g[1, 0] - np.abs(1. / g[1, 0])

        geo = Geodesic(x1, x2, model="H")
        geo.model = "D"
        return geo

    def getTransAx(self) -> Geodesic:
        r"""
        Calculate translation axis of a hyperbolic element of
        :math:`\mathrm{SU}(1,1)`.

        The axis of translation of a hyperbolic element of
        :math:`\mathrm{SU}(1,1)` is the unique geodesic between the
        two fixed points. It is preserved under the action of the hyperbolic
        element.

        :raises ValueError: Raised if the element is not hyperbolic.
        :return: Translation axis
        :rtype: Geodesic
        """
        try:
            x1, x2 = self.getFixPt()  # type: ignore
        except (TypeError, ValueError) as error:
            raise ValueError(
                "Can only generate unique geodesic for hyperbolic elements"
            ) from error
        logger.info(f"computing translation axis of {self}")
        res = Geodesic(x1, x2, model="D")
        logger.debug(f"computed translation axis {res}")
        return res


#####################
# More Custom Types #
#####################

tSym = Union[SL2R, SU11]


#############################
# General utility functions #
#############################


def SLtoSU(g: SL2R) -> SU11:
    r"""
    Transform element `g` of :math:`\mathrm{SL}(2, \mathbb{R})` into element of
    :math:`\mathrm{SU}(1, 1)`.

    The Cayley transformation
    :math:`C = \begin{pmatrix} -1 & i \\ 1 & i \end{pmatrix}` maps the Upper
    Halfplane :math:`\mathbb{H}` onto the Poincare Disk :math:`\mathbb{D}`.
    Given an isometry `g` of the Upper Halfplane, the related isometry of the
    Poincare Disk is given by :math:`g^{\prime} = C g C^{-1}`.

    :param g: Element in :math:`\mathrm{SL}(2, \mathbb{R})`
    :type g: SL2R
    :return: Conjugated element in :math:`\mathrm{SU}(1,1)`
    :rtype: SU11
    """
    h = CAYLEY @ g._A @ INV_CAYLEY
    return SU11(h)


def SUtoSL(g: SU11) -> SL2R:
    r"""
    Transform element of :math:`\mathrm{SU}(1, 1)` into element of
    :math:`\mathrm{SL}(2, \mathbb{R})`.

    The Cayley transformation
    :math:`C = \begin{pmatrix} -1 & i \\ 1 & i \end{pmatrix}` maps the Upper
    Halfplane :math:`\mathbb{H}` onto the Poincare Disk :math:`\mathbb{D}`.
    Given an isometry `g` of the Poincare Disk, the related isometry of the
    Upper Halfplane is given by :math:`g^{\prime} = C^{-1} g C`.

    :param g: Element in :math:`\mathrm{SU}(1,1)`
    :type g: SU11
    :return: Conjugated element in :math:`\mathrm{SL}(2, \mathbb{R})`
    :rtype: SL2R
    """
    gSL = INV_CAYLEY @ g._A @ CAYLEY
    return SL2R(gSL)


def getReflecTrafo(geo: Geodesic) -> tSym:
    r"""
    Compute the transformation matrix corresponding to a reflection at the
    geodesic. This function cannot be implemented as a method on `Geodesic` due
    to typing dependencies.

    :param geo: Geodesic at which the reflection takes place
    :type geo: Geodesic
    :return: Matrix representing the reflection transformation
    :rtype: SL2R or SU11, depending on the model of `geo`
    """
    model = geo.model
    logger.info("computing reflection transformation for {geo} on {model}")

    if geo.u == np.infty:
        g = np.array([[-1, 2 * geo.t], [0, 1]])
    elif geo.t == np.infty:
        g = np.array([[-1, 2 * geo.u], [0, 1]])
    else:
        g = np.array([[(geo.t + geo.u) / (geo.t - geo.u),
                       -2 * geo.t * geo.u / (geo.t - geo.u)],
                      [2. / (geo.t - geo.u),
                       -(geo.t + geo.u) / (geo.t - geo.u)]]
                     )
    trafo: tSym
    trafo = SL2R(g)
    if model == "D":
        trafo = SLtoSU(trafo)

    logger.debug("calculated reflection trafo %s", str(trafo))
    return trafo


def hypDist(z1: complex, z2: complex, model: str = "H") -> float:
    r"""
    Compute the hyperbolic distance between two points `z1` and `z2`.

    :param z1: Point in the chosen `model`
    :type z1: complex
    :param z2: Point in the chosen `model`
    :type z2: complex
    :param model: Model for hyperbolic space ('H' or 'D'), defaults to 'H'
    :type model: str, optional
    :raises InvalidDiskPoint: Raised for points outside Poincare Disk.
    :raises InvalidHalfplanePoint: Raised for points outside Upper Halfplane.
    :raises InvalidModelException: Raised if `model` is neither 'H' nor 'D'.
    :return: Hyperbolic distance :math:`\mathrm{d}_{\mathbb{H}}(z1, z2)`
        or :math:`\mathrm{d}_{\mathbb{D}}(z1, z2)`
    :rtype: float
    """
    model = model.upper()
    if model == "D":
        if abs(z1) > 1:
            raise InvalidDiskPoint(z1)
        if abs(z2) > 1:
            raise InvalidDiskPoint(z2)
        logger.info("computing distance between %s and %s on %s",
                    str(z1), str(z2), model)
        z1 = DtoH(z1)
        z2 = DtoH(z2)
    elif model == "H":
        if z1.imag < 0:
            raise InvalidHalfplanePoint(z1)
        if z2.imag < 0:
            raise InvalidHalfplanePoint(z2)
        logger.info("computing distance between %s and %s on %s",
                    str(z1), str(z2), model)
    else:
        raise InvalidModelException(model)

    if z1.imag == 0 or z2.imag == 0:
        if z1 == z2:
            return 0.
        return np.infty
    if abs(z1) == np.infty or abs(z2) == np.infty:
        logger.info("computed distance between %s and %s on %s %s",
                    str(z1), str(z2), model, "is infinite")
        return np.infty

    distance = 2. * np.arcsinh(abs(z1 - z2) / (2*np.sqrt(z1.imag*z2.imag)))
    logger.debug("computed distance %.4f", distance)
    # convert to float to satisfy optional static type checking
    return float(distance)


def horoDist(z: tVec, xi: tScal, model: str = "H") -> tVec:
    r"""
    Compute the horocyclic distance between two points `z` and `xi`.

    :param z: Array of points in the chosen `model`
    :type z: np.ndarray
    :param xi: Point in the chosen `model`
    :type xi: complex
    :param model: Model for hyperbolic space ('H' or 'D'), defaults to 'H'
    :type model: str, optional
    :raises ValueError: Raised if `xi` is not a boundary point.
    :raises InvalidModelException: Raised if `model` is neither 'H' nor 'D'.
    :return: Horocyclic distance between a point `z` of hyperbolic space and
        a point `xi` on the boundary of hyperbolic space
    :rtype: float
    """
    model = model.upper()
    if model == "H":
        if xi.imag != 0:
            raise ValueError(f"{xi} is not a valid boundary pt of {model}!")
        logger.info("computing horocyclic distance between %s and %s on %s",
                    str(z), str(xi), model)
        # convert from 'H' to 'D' for actual calculation
        cT = CAYLEY
        idx = (z == np.infty)
        z[idx] = cT[0, 0] / cT[1, 0]
        z[~idx] = (cT[0, 0]*z[~idx] + cT[0, 1]) / (cT[1, 0]*z[~idx] + cT[1, 1])
        xi = HtoD(xi)
    elif model == "D":
        if abs(xi) != 1:
            raise ValueError(f"{xi} is not a valid boundary pt of {model}!")
        logger.info("computing horocyclic distance between %s and %s on %s",
                    str(z), str(xi), model)
    else:
        raise InvalidModelException(model)
    res = np.empty(z.shape, dtype=np.float64)
    mask = (np.abs(z) < 1)
    theta = np.angle(z[mask])
    phi = np.angle(xi)
    zAbs = np.abs(z[mask])
    zSquare = np.power(zAbs, 2)

    numer = 1. - zSquare
    denom = 1. + zSquare - 2.*zAbs*np.cos(theta - phi)
    res[mask] = np.log(numer / denom)
    res[~mask] = np.nan
    return res


def hypPlaneWave(realArr: tVec, imagArr: tVec, xi: List[tScal], k: List[float],
                 model: str = "H") -> tVec:
    r"""
    """
    x, y = np.meshgrid(realArr, imagArr)
    z = np.empty(x.shape, dtype=np.complex128)
    z.real = x
    z.imag = y
    res = np.cos(k[0] * horoDist(z, xi[0], model=model))
    for freq, start in zip(k[1:], xi[1:]):
        res += np.cos(freq * horoDist(z, start, model=model))
    return res


def getMiddlePt(z1: tScal, z2: tScal, model: str = "H") -> tScal:
    r"""
    Compute the middle point of the hyperbolic segment [`z1`, `z2`].

    The middle point lies on the hyperbolic segment and is equidistant from the
    endpoints of the segment measured w.r.t. hyperbolic distance.

    :param z1: Point in the chosen `model`
    :type z1: float or complex
    :param z2: Point in the chosen `model`
    :type z2: float or complex
    :param model: Model for hyperbolic space ('H' or 'D'), defaults to 'H'
    :type model: str, optional
    :raises InvalidDiskPoint: Raised for points outside Poincare Disk.
    :raises InvalidHalfplanePoint: Raised for points outside Upper Halfplane.
    :raises InvalidModelException: Raised if `model` is neither 'H' nor 'D'.
    :return: Middle point
    :rtype: float or complex
    """
    model = model.upper()
    if model == "D":
        if abs(z1) > 1:
            raise InvalidDiskPoint(z1)
        if abs(z2) > 1:
            raise InvalidDiskPoint(z2)
        logger.info("computing mid pt of %s-seg [(%.3f+%.3fj), (%.3f+%.3fj)]",
                    model, z1.real, z1.imag, z2.real, z2.imag)
        z1 = DtoH(z1)
        z2 = DtoH(z2)
    elif model == "H":
        if z1.imag < 0:
            raise InvalidHalfplanePoint(z1)
        if z2.imag < 0:
            raise InvalidHalfplanePoint(z2)
        logger.info("computing mid pt of %s-seg [(%.3f+%.3fj), (%.3f+%.3fj)]",
                    model, z1.real, z1.imag, z2.real, z2.imag)
    else:
        raise InvalidModelException(model)

    if z1 == z2:
        logger.warning("computing the middle point of two identical points")
        res = z1
    elif z1.imag == 0:
        if z2.imag == 0:
            res = min(z1, z2) + 1/2 * abs(z1 - z2) * (1 + 1j)  # type: ignore
        else:
            res = z1
    elif z2.imag == 0:
        res = z2
    else:
        geo = Geodesic(z1, z2, model="H")
        if geo.r == np.infty:
            d0 = hypDist(z1, z2)
            # root_scalar returns RootResults object; need the attribute root
            xMid = root_scalar(
                lambda x: hypDist(z1, z1*(1 - x) + z2*x) - d0/2, bracket=[0, 1]
            ).root
            res = z1*(1 - xMid) + z2*xMid
        else:
            phi0 = np.angle(z1 - geo.m)
            phi1 = np.angle(z2 - geo.m)
            d0 = hypDist(z1, z2)
            phiMid = root_scalar(
                lambda phi: (
                    hypDist(z1, geo.m+geo.r*(np.cos(phi)+1j*np.sin(phi)))-d0/2
                    ), bracket=sorted((phi0, phi1))
            ).root
            res = geo.m + geo.r*(np.cos(phiMid) + 1j*np.sin(phiMid))

    if model == 'D':
        res = HtoD(res)
    logger.debug(f"computed middle point {res}")
    return res


def getPerpGeo(z1: tScal, z2: tScal, model: str = "H") -> Geodesic:
    r"""
    Compute the perpendicular bisector of the hyperbolic segment [`z1`, `z2`].

    The perpendicular bisector of a hyperbolic segment is the unique geodesic
    through the middle point of the segment and perpendicular to the segment.

    :param z1: Point in the chosen `model`
    :type z1: float or complex
    :param z2: Point in the chosen `model`
    :type z2: float or complex
    :param model: Model for hyperbolic space ('H' or 'D'), defaults to 'H'
    :type model: str, optional
    :raises InvalidDiskPoint: Raised for points outside Poincare Disk.
    :raises InvalidHalfplanePoint: Raised for points outside Upper Halfplane.
    :raises InvalidModelException: Raised if `model` is neither 'H' nor 'D'.
    :raises InvalidGeodesicsException: Raised if both points are identical.
    :raises ValueError: Raised it the middle point of the hyperbolic segment
        lies on the boundary of the model. This happens if exactly one endpoint
        of the segment lies on the boundary.
    :return: Perpendicular bisector
    :rtype: Geodesic
    """
    model = model.upper()
    if model == "D":
        if abs(z1) > 1:
            raise InvalidDiskPoint(z1)
        if abs(z2) > 1:
            raise InvalidDiskPoint(z2)
        logger.info("compute perpendicular bisector of %s-segment [%s, %s]",
                    model, str(z1), str(z2))
        z1 = DtoH(z1)
        z2 = DtoH(z2)
    elif model == "H":
        if z1.imag < 0:
            raise InvalidHalfplanePoint(z1)
        if z2.imag < 0:
            raise InvalidHalfplanePoint(z2)
        logger.info("compute perpendicular bisector of %s-segment [%s, %s]",
                    model, str(z1), str(z2))
    else:
        raise InvalidModelException(model)

    if z1 == z2:
        logger.warning("trying to compute perpendicular bisector of %s",
                       "degenerate segment consisting of a single point")
        raise InvalidGeodesicException(z1, z2)

    geo = Geodesic(z1, z2, model="H")
    zMid = getMiddlePt(z1, z2, model="H")

    if zMid.imag == 0.:
        if model == "D":
            geo.model = "D"
            zMid = HtoD(zMid)
        logger.warning("trying to compute perpendicular bisector for %s %s",
                       "segment with endpoint on boundary of", model)
        raise ValueError(f"No geodesic perpendicular to {geo} through "
                         + "{zMid:.4f} exists.")

    if z1.imag == z2.imag:
        res = Geodesic(zMid.real, zMid, model="H")
        res.model = model
    else:
        trans = SL2R(np.array([[1, (-1*zMid).real], [0, 1]]))
        dilat = SL2R(np.array([[zMid.imag**(-1), 0], [0, 1]]))
        turn = SL2R(np.array([[1, -1], [1, 1]]))
        prod = trans.inverse()*dilat.inverse()*turn*dilat*trans
        res = prod(geo)
        res.model = model
    logger.debug("computed perpendicular bisector %s", str(res))
    return res


def getFundDom(*generators: tSym, z0: tScal = 1j) -> List[Tuple[float, float]]:
    r"""
    Compute the fundamental domain of a Schottky group of arbitrary rank.

    A Schottky group of rank k is generated by k hyperbolic isometries. The
    generators are the only arguments passed to this function. Note that only
    the k generators (not in addition their inverses) should be passed.
    Generators may be of type SL2R or of type SU11. The model (Upper Halfplane
    or Poincare Disk) is inferred from the type of the generators.

    The fundamental domain computed here is a Dirichlet domain (cf. Dal'Bo
    p.21) centered at `z0`.

    :param \*generators: Generators of the Schottky group
    :type \*generators: SL2R or SU11, all generators must be of the same type
    :param z0: center of the Dirichlet domain, defaults to i (or 0)
        on the Upper Halfplane (or on the Poincare Disk, respectively)
    :type z0: float or complex, optional
    :raises InvalidMatrixException: Raised if the generators are neither of
        type SL2R nor of type SU11
    :raises TypeError: Raised if not all generators are of the same type
    :return: List of tuple of float, the tuples contain the endpoints of
        geodesics bounding the fundamental domain; there are two tuples per
        generator, on the Upper Halfplane the endpoints lie on the real axis
        and are thus determined by their real part, on the Poincare Disk the
        endpoints lie on the unit circle and are determined by their angle
    :rtype: List[Tuple[float, float]]
    """
    # determine model from type of first symmetry passed
    if isinstance(generators[0], SL2R):
        model = "H"
    elif isinstance(generators[0], SU11):
        model = "D"
    else:
        raise TypeError("Generators must be passed as SL2R objects or as " +
                        "SU11 objects")

    if model == "D" and z0 == 1j:
        z0 = 0.

    boundaryPts = []
    boundaryPtsInv = []
    for g in generators:
        if model == "H":
            if not isinstance(g, SL2R):
                raise TypeError("Cannot compute fundamental domain for " +
                                f"generators {generators[0]} and {g} of " +
                                "different type.")
        if model == "D":
            if not isinstance(g, SU11):
                raise TypeError("Cannot compute fundamental domain for " +
                                f"generators {generators[0]} and {g} of " +
                                "different type.")

        logger.info(
            "Compute Dirichlet domain of %s for z0=%.4f+%.4f*1j on model %s",
            str(g), z0.real, z0.imag, model
        )

        z1 = g(z0)
        perpGeo1 = getPerpGeo(z0, z1, model=model)
        gInv = g.inverse()
        z2 = gInv(z0)
        perpGeo2 = getPerpGeo(z0, z2, model=model)

        if model == "H":
            boundaryPts.append((perpGeo1.t, perpGeo1.u))
            boundaryPtsInv.append((perpGeo2.t, perpGeo2.u))
        if model == "D":
            boundaryPts.append((float(np.angle(perpGeo1.td)),
                                float(np.angle(perpGeo1.ud))))
            boundaryPtsInv.append((float(np.angle(perpGeo2.td)),
                                   float(np.angle(perpGeo2.ud))))

        logger.debug("computed fundamental domain is bounded by %s and %s",
                     str(perpGeo1), str(perpGeo2))

    # order fundamental intervals in the Schottky surface convention
    boundaryPts.extend(boundaryPtsInv)

    return boundaryPts


def plotFundDom(*generators: tSym, z0: tScal = 1j, transAx: bool = True,
                center: bool = True, ax: Any = None, **kwargs
                ) -> Tuple[Any, Any]:
    r"""
    Plot the fundamental domain of a Schottky group of arbitrary rank.

    The generators must be passed as arguments to this function. Note that only
    the generators (not in addition their inverses) should be passed.
    Generators may be of type SL2R or of type SU11. The model (Upper Halfplane
    or Poincare Disk) is infered from the type of the generators.

    The fundamental domain plotted here is a Dirichlet domain (cf. Dal'Bo
    p.21) centered at `z0`.

    :param \*generators: Generators of the Schottky group
    :type \*generators: SL2R or SU11, all generators must be of the same type
    :param z0: center of the Dirichlet domain, defaults to i (or 0)
        on the Upper Halfplane (or on the Poincare Disk, respectively)
    :type z0: float or complex, optional
    :param transAx: specifies whether the translation axis is plotted for each
        generator, defaults to true
    :type transAx: bool, optional
    :param center: specifies whether the center of the domain is plotted,
        defaults to True
    :type center: bool, optional
    :param ax: Matplotlib axes object in which the plot should be drawn. If
        None is passed, a new figure and axes are created, defaults to None
    :type ax: matplotlib.axes.Axes, optional
    :param \*\*kwargs: Further keyword arguments are passed to
        hypgeo.Geodesic.plot
    :raises InvalidMatrixException: Raised if the generators are neither of
        type SL2R nor of type SU11
    :return: Matplotlib figure and matplotlib axes object in which the plot
        is drawn
    :rtype: matplotlib.figure.Figure, matplotlib.axes.Axes
    """
    # determine model from type of first symmetry passed
    if isinstance(generators[0], SL2R):
        model = "H"
    elif isinstance(generators[0], SU11):
        model = "D"
    else:
        raise TypeError("Generators must be passed as SL2R objects or as " +
                        "SU11 objects")

    if model == "D" and z0 == 1j:
        z0 = 0

    if ax is None:
        _, ax = plt.subplots(tight_layout=True)

    kwargs["color"] = kwargs.get("color", kwargs.get("c", "green"))
    kwargs.pop("c", None)
    kwargs["linewidth"] = kwargs.get("linewidth", kwargs.get("lw", 2.))
    kwargs.pop("lw", None)
    kwargs["clip_on"] = kwargs.get("clip_on", False)

    boundaryPts = sorted(getFundDom(*generators, z0=z0))
    if model == "D" and boundaryPts[0][1] > boundaryPts[-1][1]:
        # if one boundary geodesic encloses angle=+/-pi on the disk, switch its
        # tAngle and uAngle such that uAngle comes anti-clockwise after tAngle
        boundaryPts[0] = boundaryPts[0][::-1]
    for endPts in boundaryPts:
        if model == "D":
            endPts = (np.exp(1j*endPts[0]), np.exp(1j*endPts[1]))
        geo = Geodesic(endPts[0], endPts[1], model=model)
        geo.plot(ax=ax, **kwargs)

    if center and model == "H":
        if ax.get_ylim()[1] < 1.1*z0.imag:
            addLim = 1.1*z0.imag - ax.get_ylim()[1]
            ax.set_xlim(ax.get_xlim()[0] - addLim,
                        ax.get_xlim()[1] + addLim)
            ax.set_ylim(0, ax.get_ylim()[1] + addLim)
            ax.set_aspect("equal")

    # place keyword arguments specifing markers into separate dictionary
    markerKwargs = {}
    for key, item in kwargs.items():
        if "marker" in key:
            markerKwargs[key] = item
    for key in markerKwargs:
        kwargs.pop(key)

    kwargs["linestyle"] = kwargs.get("linestyle", kwargs.get("ls", "--"))
    kwargs.pop("ls", None)

    if model == "H":
        if boundaryPts[0][1] < boundaryPts[-1][1]:
            # if fundamental domain extends to inf
            boundaryPts.insert(0, (ax.get_xlim()[0], ax.get_xlim()[1]))
            ax.text(boundaryPts[0][0], 0, r"$\overleftarrow{\infty}$",
                    horizontalalignment="left",
                    verticalalignment="bottom", fontsize="x-large")
            ax.text(boundaryPts[0][1], 0, r"$\overrightarrow{\infty}$",
                    horizontalalignment="right",
                    verticalalignment="bottom", fontsize="x-large")

        ax.plot([boundaryPts[0][0], boundaryPts[1][0]], [0, 0], **kwargs)
        ax.plot([boundaryPts[-1][1], boundaryPts[0][1]], [0, 0], **kwargs)
        for i in range(1, len(boundaryPts)-1):
            ax.plot([boundaryPts[i][1], boundaryPts[i+1][0]], [0, 0],
                    **kwargs)

    if model == "D":
        theta1 = np.rad2deg(boundaryPts[-1][1])
        theta2 = np.rad2deg(boundaryPts[0][0])
        arc = patches.Arc((0, 0), 2, 2, theta1=theta1, theta2=theta2,
                          **kwargs)
        ax.add_patch(arc)

        for i in range(0, len(boundaryPts)-1):
            theta1 = np.rad2deg(boundaryPts[i][1])
            theta2 = np.rad2deg(boundaryPts[i+1][0])
            arc = patches.Arc((0, 0), 2, 2, theta1=theta1, theta2=theta2,
                              **kwargs)
            ax.add_patch(arc)

    if transAx:
        inftyMax = ax.get_ylim()[1]
        for g in generators:
            kwargs["color"] = "tab:gray"
            kwargs["linestyle"] = ":"
            transAxis = g.getTransAx()
            transAxis.plot(ax=ax, inftyMax=inftyMax, **kwargs, **markerKwargs)

    if center:
        markerKwargs["marker"] = markerKwargs.get("marker", "o")
        ax.plot(z0.real, z0.imag, color="0.5", **markerKwargs)
        ax.text(z0.real, z0.imag, r"$z_0$")
        for g in generators:
            z1 = g(z0)
            gInv = g.inverse()
            z2 = gInv(z0)
            ax.plot(z1.real, z1.imag, color="0.35", **markerKwargs)
            ax.plot(z2.real, z2.imag, color="0.65", **markerKwargs)

    logger.debug("plotted fundamental domain of %s", str(generators))
    return ax.get_figure(), ax


def main(model: str = "H") -> None:
    r"""Some examples illustrating the features of this module."""
    logger.setLevel(DEBUG)
    # funnel torus example
    l1 = 2.0
    l2 = 2.0
    phi = 0.5*np.pi
    z0 = 1j

    mat1 = [[np.exp(l1/2.0), 0.0], [0.0, np.exp(-l1/2.0)]]
    mat2 = [[np.cosh(l2/2.0) - np.cos(phi)*np.sinh(l2/2.0),
             np.sinh(l2/2.0)*np.sin(phi)**2],
            [np.sinh(l2/2.0), np.cosh(l2/2.0) + np.cos(phi)*np.sinh(l2/2.0)]]

    mats = [np.array(mat1), np.array(mat2)]

    generators = [SL2R(mat) for mat in mats]
    if model == "D":
        for i, gen in enumerate(generators):
            generators[i] = SLtoSU(gen)  # type: ignore
        z0 = HtoD(z0)
    plotFundDom(*generators, z0=z0)
    plt.show()

    # hyperbolic plane waves example1
    realArr = np.linspace(-2., 2., 1000)
    imagArr = np.linspace(0., 4., 1000)
    xi = [0. + 0.j, ]
    k = [5.0, ]

    wave = hypPlaneWave(realArr, imagArr, xi, k, model="H")
    wave[wave == np.infty] = -1.
    plt.imshow(wave, cmap="Reds", interpolation="nearest", origin="lower",
               extent=[-2, 2, 0, 4.])
    plt.show()

    # hyperbolic plane waves example2
    realArr = np.linspace(-1., 1., 8000)
    imagArr = np.linspace(-1., 1., 8000)
    xi = [1., -1.]
    k = [2., 3.]

    wave = hypPlaneWave(realArr, imagArr, xi, k, model="D")
    wave[wave == np.nan] = 0.
    plt.imshow(wave, cmap="Reds", interpolation="nearest", origin="lower",
               extent=[-1, 1, -1, 1])
    plt.show()

##############################################################################
# TODO: Once NumPy gets decent type annotations like `np.ndarray[np.complex64]
#       we should adjust the custom types `tVec`, `tMat`
##############################################################################


if __name__ == "__main__":
    main()
