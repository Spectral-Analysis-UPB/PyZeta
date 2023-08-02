"""
TODO.

Authors:\n
- Philipp Schuette\n
- Tobias Weich\n
- Sebastian Albrecht\n
"""

from __future__ import annotations

from typing import Any, List, Tuple, Union

import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from matplotlib import patches
from numpy.typing import NDArray
from scipy.optimize import root_scalar  # type: ignore
from typing_extensions import TypeAlias

from pyzeta.core.pyzeta_types.general import tVec
from pyzeta.geometry.constants import CAYLEY, INV_CAYLEY, tScal
from pyzeta.geometry.geodesic import Geodesic
from pyzeta.geometry.geometry_exceptions import (
    InvalidDiskPoint,
    InvalidGeodesicException,
    InvalidHalfplanePoint,
    InvalidModelException,
)
from pyzeta.geometry.helpers import DtoH, HtoD
from pyzeta.geometry.sl2r import SL2R
from pyzeta.geometry.su11 import SU11

tSym: TypeAlias = Union[SL2R, SU11]


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
    :return: Conjugated element in :math:`\mathrm{SU}(1,1)`
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
    :return: Conjugated element in :math:`\mathrm{SL}(2, \mathbb{R})`
    """
    gSL = INV_CAYLEY @ g._A @ CAYLEY
    return SL2R(gSL)


def getReflecTrafo(geo: Geodesic) -> tSym:
    r"""
    Compute the transformation matrix corresponding to a reflection at the
    geodesic.

    :param geo: Geodesic at which the reflection takes place
    :return: Matrix representing the reflection transformation
    """
    model = geo.model

    if geo.u == np.infty:
        g = np.array([[-1, 2 * geo.t], [0, 1]])
    elif geo.t == np.infty:
        g = np.array([[-1, 2 * geo.u], [0, 1]])
    else:
        g = np.array(
            [
                [
                    (geo.t + geo.u) / (geo.t - geo.u),
                    -2 * geo.t * geo.u / (geo.t - geo.u),
                ],
                [2.0 / (geo.t - geo.u), -(geo.t + geo.u) / (geo.t - geo.u)],
            ]
        )
    trafo: tSym
    trafo = SL2R(g)
    if model == "D":
        trafo = SLtoSU(trafo)

    return trafo


def hypDist(z1: complex, z2: complex, model: str = "H") -> float:
    r"""
    Compute the hyperbolic distance between two points `z1` and `z2`.

    :param z1: Point in the chosen `model`
    :param z2: Point in the chosen `model`
    :param model: Model for hyperbolic space ('H' or 'D'), defaults to 'H'
    :raises InvalidDiskPoint: Raised for points outside Poincare Disk.
    :raises InvalidHalfplanePoint: Raised for points outside Upper Halfplane.
    :raises InvalidModelException: Raised if `model` is neither 'H' nor 'D'.
    :return: Hyperbolic distance :math:`\mathrm{d}_{\mathbb{H}}(z1, z2)`
        or :math:`\mathrm{d}_{\mathbb{D}}(z1, z2)`
    """
    model = model.upper()
    if model == "D":
        if abs(z1) > 1:
            raise InvalidDiskPoint(z1)
        if abs(z2) > 1:
            raise InvalidDiskPoint(z2)
        z1 = DtoH(z1)
        z2 = DtoH(z2)
    elif model == "H":
        if z1.imag < 0:
            raise InvalidHalfplanePoint(z1)
        if z2.imag < 0:
            raise InvalidHalfplanePoint(z2)
    else:
        raise InvalidModelException(model)

    if z1.imag == 0 or z2.imag == 0:
        if z1 == z2:
            return 0.0
        return np.infty
    if abs(z1) == np.infty or abs(z2) == np.infty:
        return np.infty

    distance = 2.0 * np.arcsinh(
        abs(z1 - z2) / (2 * np.sqrt(z1.imag * z2.imag))
    )
    # convert to float to satisfy optional static type checking
    return float(distance)


def horoDist(z: tVec, xi: tScal, model: str = "H") -> NDArray[np.float64]:
    r"""
    Compute the horocyclic distance between two points `z` and `xi`.

    :param z: Array of points in the chosen `model`
    :param xi: Point in the chosen `model`
    :param model: Model for hyperbolic space ('H' or 'D'), defaults to 'H'
    :raises ValueError: Raised if `xi` is not a boundary point.
    :raises InvalidModelException: Raised if `model` is neither 'H' nor 'D'.
    :return: Horocyclic distance between a point `z` of hyperbolic space and
        a point `xi` on the boundary of hyperbolic space
    """
    model = model.upper()
    if model == "H":
        if xi.imag != 0:
            raise ValueError(f"{xi} is not a valid boundary pt of {model}!")
        # convert from 'H' to 'D' for actual calculation
        cT = CAYLEY
        idx = z == np.infty
        z[idx] = cT[0, 0] / cT[1, 0]
        z[~idx] = (cT[0, 0] * z[~idx] + cT[0, 1]) / (
            cT[1, 0] * z[~idx] + cT[1, 1]
        )
        xi = HtoD(xi)
    elif model == "D":
        if abs(xi) != 1:
            raise ValueError(f"{xi} is not a valid boundary pt of {model}!")
    else:
        raise InvalidModelException(model)
    res = np.empty(z.shape, dtype=np.float64)
    mask = np.abs(z) < 1
    theta = np.angle(z[mask])
    phi = np.angle(xi)
    zAbs = np.abs(z[mask])
    zSquare = np.power(zAbs, 2)

    numer = 1.0 - zSquare
    denom = 1.0 + zSquare - 2.0 * zAbs * np.cos(theta - phi)
    res[mask] = np.log(numer / denom)
    res[~mask] = np.nan
    return res


def hypPlaneWave(
    realArr: NDArray[np.float64],
    imagArr: NDArray[np.float64],
    xi: List[tScal],
    k: List[float],
    model: str = "H",
) -> tVec:
    """
    TODO.
    """
    x, y = np.meshgrid(realArr, imagArr)
    z = np.empty(x.shape, dtype=np.complex128)
    z.real = x
    z.imag = y
    res = np.zeros_like(z)
    for freq, start in zip(k, xi):
        res += np.cos(freq * horoDist(z, start, model=model))
    return res


def getMiddlePt(z1: tScal, z2: tScal, model: str = "H") -> tScal:
    r"""
    Compute the middle point of the hyperbolic segment [`z1`, `z2`].

    The middle point lies on the hyperbolic segment and is equidistant from the
    endpoints of the segment measured w.r.t. hyperbolic distance.

    :param z1: Point in the chosen `model`
    :param z2: Point in the chosen `model`
    :param model: Model for hyperbolic space ('H' or 'D'), defaults to 'H'
    :raises InvalidDiskPoint: Raised for points outside Poincare Disk.
    :raises InvalidHalfplanePoint: Raised for points outside Upper Halfplane.
    :raises InvalidModelException: Raised if `model` is neither 'H' nor 'D'.
    :return: Middle point
    """
    model = model.upper()
    if model == "D":
        if abs(z1) > 1:
            raise InvalidDiskPoint(z1)
        if abs(z2) > 1:
            raise InvalidDiskPoint(z2)
        z1 = DtoH(z1)
        z2 = DtoH(z2)
    elif model == "H":
        if z1.imag < 0:
            raise InvalidHalfplanePoint(z1)
        if z2.imag < 0:
            raise InvalidHalfplanePoint(z2)
    else:
        raise InvalidModelException(model)

    if z1 == z2:
        res = z1
    elif z1.imag == 0:
        if z2.imag == 0:
            res = min(z1, z2) + 1 / 2 * abs(z1 - z2) * (1 + 1j)  # type: ignore
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
                lambda x: hypDist(z1, z1 * (1 - x) + z2 * x) - d0 / 2,
                bracket=[0, 1],
            ).root
            res = z1 * (1 - xMid) + z2 * xMid
        else:
            phi0 = float(np.angle(z1 - geo.m))
            phi1 = float(np.angle(z2 - geo.m))
            d0 = hypDist(z1, z2)
            phiMid = root_scalar(
                lambda phi: (
                    hypDist(
                        z1, geo.m + geo.r * (np.cos(phi) + 1j * np.sin(phi))
                    )
                    - d0 / 2
                ),
                bracket=sorted((phi0, phi1)),
            ).root
            res = geo.m + geo.r * (np.cos(phiMid) + 1j * np.sin(phiMid))

    if model == "D":
        res = HtoD(res)
    return res


def getPerpGeo(z1: tScal, z2: tScal, model: str = "H") -> Geodesic:
    r"""
    Compute the perpendicular bisector of the hyperbolic segment [`z1`, `z2`].

    The perpendicular bisector of a hyperbolic segment is the unique geodesic
    through the middle point of the segment and perpendicular to the segment.

    :param z1: Point in the chosen `model`
    :param z2: Point in the chosen `model`
    :param model: Model for hyperbolic space ('H' or 'D'), defaults to 'H'
    :raises InvalidDiskPoint: Raised for points outside Poincare Disk.
    :raises InvalidHalfplanePoint: Raised for points outside Upper Halfplane.
    :raises InvalidModelException: Raised if `model` is neither 'H' nor 'D'.
    :raises InvalidGeodesicsException: Raised if both points are identical.
    :raises ValueError: Raised it the middle point of the hyperbolic segment
        lies on the boundary of the model. This happens if exactly one endpoint
        of the segment lies on the boundary.
    :return: Perpendicular bisector
    """
    model = model.upper()
    if model == "D":
        if abs(z1) > 1:
            raise InvalidDiskPoint(z1)
        if abs(z2) > 1:
            raise InvalidDiskPoint(z2)
        z1 = DtoH(z1)
        z2 = DtoH(z2)
    elif model == "H":
        if z1.imag < 0:
            raise InvalidHalfplanePoint(z1)
        if z2.imag < 0:
            raise InvalidHalfplanePoint(z2)
    else:
        raise InvalidModelException(model)

    if z1 == z2:
        raise InvalidGeodesicException(z1, z2)

    geo = Geodesic(z1, z2, model="H")
    zMid = getMiddlePt(z1, z2, model="H")

    if zMid.imag == 0.0:
        if model == "D":
            geo.model = "D"
            zMid = HtoD(zMid)
        raise ValueError(
            "No geodesic perpendicular to {geo} through {zMid:.4f} exists."
        )

    if z1.imag == z2.imag:
        res = Geodesic(zMid.real, zMid, model="H")
        res.model = model
    else:
        trans = SL2R(np.array([[1, (-1 * zMid).real], [0, 1]]))
        dilat = SL2R(np.array([[zMid.imag ** (-1), 0], [0, 1]]))
        turn = SL2R(np.array([[1, -1], [1, 1]]))
        prod = trans.inverse() * dilat.inverse() * turn * dilat * trans
        res = prod(geo)
        res.model = model
    return res


def getFundDom(*generators: tSym, z0: tScal = 1j) -> List[Tuple[float, float]]:
    r"""
    Compute the fundamental domain of a Schottky group of arbitrary rank.

    A Schottky group of rank k is generated by k hyperbolic isometries. The
    generators are the only arguments passed to this function. Note that only
    the k generators (not in addition their inverses) should be passed.
    Generators may be of type SL2R or of type SU11. The model (upper halfplane
    or Poincare disc) is inferred from the type of the generators.

    The fundamental domain computed here is a Dirichlet domain (cf. Dal'Bo
    p.21) centered at `z0`.

    :param \*generators: Generators of the Schottky group
    :param z0: center of the Dirichlet domain, defaults to i (or 0)
        on the Upper Halfplane (or on the Poincare Disk, respectively)
    :raises InvalidMatrixException: Raised if the generators are neither of
        type SL2R nor of type SU11
    :raises TypeError: Raised if not all generators are of the same type
    :return: List of tuple of float, the tuples contain the endpoints of
        geodesics bounding the fundamental domain; there are two tuples per
        generator, on the Upper Halfplane the endpoints lie on the real axis
        and are thus determined by their real part, on the Poincare Disk the
        endpoints lie on the unit circle and are determined by their angle
    """
    # determine model from type of first symmetry passed
    if isinstance(generators[0], SL2R):
        model = "H"
    elif isinstance(generators[0], SU11):
        model = "D"
    else:
        raise TypeError("Generators must be passed as SL2R or SU11 instances!")

    if model == "D" and z0 == 1j:
        z0 = 0.0

    boundaryPts = []
    boundaryPtsInv = []
    for g in generators:
        if (model == "H" and not isinstance(g, SL2R)) or (
            model == "D" and not isinstance(g, SU11)
        ):
            raise TypeError(
                "Cannot compute fundamental domain for generators "
                f"{generators[0]} and {g} of different type."
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
            boundaryPts.append(
                (float(np.angle(perpGeo1.td)), float(np.angle(perpGeo1.ud)))
            )
            boundaryPtsInv.append(
                (float(np.angle(perpGeo2.td)), float(np.angle(perpGeo2.ud)))
            )

    # order fundamental intervals in the Schottky surface convention
    boundaryPts.extend(boundaryPtsInv)

    return boundaryPts


def plotFundDom(
    *generators: tSym,
    z0: tScal = 1j,
    transAx: bool = True,
    center: bool = True,
    ax: Any = None,
    **kwargs: object,
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
    :param z0: center of the Dirichlet domain, defaults to i (or 0)
        on the Upper Halfplane (or on the Poincare Disk, respectively)
    :param transAx: specifies whether the translation axis is plotted for each
        generator, defaults to true
    :param center: specifies whether the center of the domain is plotted,
        defaults to True
    :param ax: Matplotlib axes object in which the plot should be drawn. If
        None is passed, a new figure and axes are created, defaults to None
    :param \*\*kwargs: Further keyword arguments are passed to
        hypgeo.Geodesic.plot
    :raises InvalidMatrixException: Raised if the generators are neither of
        type SL2R nor of type SU11
    :return: Matplotlib figure and axes objects with the new plot inside
    """
    # determine model from type of first symmetry passed
    if isinstance(generators[0], SL2R):
        model = "H"
    elif isinstance(generators[0], SU11):
        model = "D"
    else:
        raise TypeError(
            "Generators must be passed as SL2R objects or as " + "SU11 objects"
        )

    if model == "D" and z0 == 1j:
        z0 = 0

    if ax is None:
        _, ax = plt.subplots(tight_layout=True)

    kwargs["color"] = kwargs.get("color", kwargs.get("c", "green"))
    kwargs.pop("c", None)
    kwargs["linewidth"] = kwargs.get("linewidth", kwargs.get("lw", 2.0))
    kwargs.pop("lw", None)
    kwargs["clip_on"] = kwargs.get("clip_on", False)

    boundaryPts = sorted(getFundDom(*generators, z0=z0))
    if model == "D" and boundaryPts[0][1] > boundaryPts[-1][1]:
        # if one boundary geodesic encloses angle=+/-pi on the disk, switch its
        # tAngle and uAngle such that uAngle comes anti-clockwise after tAngle
        boundaryPts[0] = boundaryPts[0][::-1]
    for endPts in boundaryPts:
        if model == "D":
            endPts = (np.exp(1j * endPts[0]), np.exp(1j * endPts[1]))
        geo = Geodesic(endPts[0], endPts[1], model=model)
        geo.plot(ax=ax, **kwargs)  # type: ignore

    if center and model == "H":
        if ax.get_ylim()[1] < 1.1 * z0.imag:
            addLim = 1.1 * z0.imag - ax.get_ylim()[1]
            ax.set_xlim(ax.get_xlim()[0] - addLim, ax.get_xlim()[1] + addLim)
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
            ax.text(
                boundaryPts[0][0],
                0,
                r"$\overleftarrow{\infty}$",
                horizontalalignment="left",
                verticalalignment="bottom",
                fontsize="x-large",
            )
            ax.text(
                boundaryPts[0][1],
                0,
                r"$\overrightarrow{\infty}$",
                horizontalalignment="right",
                verticalalignment="bottom",
                fontsize="x-large",
            )

        ax.plot([boundaryPts[0][0], boundaryPts[1][0]], [0, 0], **kwargs)
        ax.plot([boundaryPts[-1][1], boundaryPts[0][1]], [0, 0], **kwargs)
        for i in range(1, len(boundaryPts) - 1):
            ax.plot(
                [boundaryPts[i][1], boundaryPts[i + 1][0]], [0, 0], **kwargs
            )

    if model == "D":
        theta1 = np.rad2deg(boundaryPts[-1][1])
        theta2 = np.rad2deg(boundaryPts[0][0])
        arc = patches.Arc((0, 0), 2, 2, theta1=theta1, theta2=theta2, **kwargs)
        ax.add_patch(arc)

        for i in range(0, len(boundaryPts) - 1):
            theta1 = np.rad2deg(boundaryPts[i][1])
            theta2 = np.rad2deg(boundaryPts[i + 1][0])
            arc = patches.Arc(
                (0, 0), 2, 2, theta1=theta1, theta2=theta2, **kwargs
            )
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

    return ax.get_figure(), ax
