"""
TODO.

Authors:\n
- Sebastian Albrecht\n
- Philipp Schuette\n
"""

from cmath import isclose
from typing import Any, Tuple, Union, overload

import numpy as np

from pyzeta.core.pyzeta_types.general import tVec
from pyzeta.geometry.constants import CAYLEY, INV_CAYLEY, tScal
from pyzeta.geometry.geometry_exceptions import (
    InvalidDiskPoint,
    InvalidHalfplanePoint,
    InvalidModelException,
)


# docstr-coverage: inherited
@overload
def stabilize(z: tScal, model: str = "H", tol: float = 1e-9) -> tScal:
    ...


# docstr-coverage: inherited
@overload
def stabilize(z: tVec, model: str = "H", tol: float = 1e-9) -> tVec:
    ...


def stabilize(
    z: Union[tScal, tVec], model: str = "H", tol: float = 1e-9
) -> Union[tScal, tVec]:
    r"""
    Stabilize computations in the module by taking care of small numerical
    errors that push boundary points out of the respective model.

    From the mathematical theory it is usually clear that results of
    computations in this module are points that lie inside the hyperbolic plane
    :math:`\mathbb{H}` or the Poincare disc :math:`\mathbb{D}` (or on their
    respective boundaries). In some cases, numerical computations produce very
    small errors (< 10^-9) that lie outside the respective boundary (i.e.
    points with very small negative imaginary part, in the case of
    :math:`\mathbb{H}`, or with absolute value very small above 1, in the case
    of :math:`\mathbb{D}`).

    :param z: Point or vector in the chosen `model`
    :param model: Model for hyperbolic space ('H' or 'D'), defaults to 'H'
    :param tol: Absolute tolerance, defaults to 1e-9
    :raises InvalidModelException: Raised if `model` is neither 'H' nor 'D'.
    :return: Point or vector with errors within `tolerance` removed.
    """
    model = model.upper()
    if model == "H":
        if isinstance(z, np.ndarray):
            mask = np.logical_and(
                np.isclose(z.imag, 0.0, rtol=0.0, atol=tol), z.imag < 0.0
            )
            if np.any(mask):
                z = np.where(mask, z.real, z)
        elif isclose(z.imag, 0.0, rel_tol=0, abs_tol=tol) and z.imag < 0.0:
            z = z.real
    elif model == "D":
        if isinstance(z, np.ndarray):
            mask = np.logical_and(
                np.isclose(np.abs(z), 1.0, rtol=0.0, atol=tol), np.abs(z) > 1.0
            )
            if np.any(mask):
                z = np.where(mask, z / abs(z), z)
        elif isclose(abs(z), 1.0, rel_tol=0.0, abs_tol=tol) and abs(z) > 1.0:
            z = z / abs(z)
    else:
        raise InvalidModelException(model)
    return z


def HtoD(z: tScal) -> complex:
    r"""
    Map point from the Upper Halfplane to the Poincare Disk.

    The Cayley transformation
    :math:`C = \begin{pmatrix} -1 & i \\ 1 & i \end{pmatrix}` maps the upper
    halfplane :math:`\mathbb{H}` onto the poincare disc :math:`\mathbb{D}`.

    :param z: Point on the Upper Halfplane
    :return: Point on the Poincare Disk
    """
    res: complex
    cT = CAYLEY
    if abs(z) == np.infty:
        res = cT[0, 0] / cT[1, 0]
    else:
        res = (cT[0, 0] * z + cT[0, 1]) / (cT[1, 0] * z + cT[1, 1])

    # convert to float to satisfy optional static type checking; could be
    # removed with proper type annotation for `tVec`:
    res = complex(res)

    res = stabilize(res, model="D")  # improve numerical stability
    return res


def DtoH(z: tScal) -> complex:
    r"""
    Map point from the Poincare Disk to the Upper Halfplane.

    The inverse Cayley transformation
    :math:`C = \begin{pmatrix} 1 & -1 \\ i & i \end{pmatrix}` maps the poincare
    disc :math:`\mathbb{D}` onto the upper halfplane :math:`\mathbb{H}`.

    :param z: Point on the Poincare Disk
    :return: Point on the Upper Halfplane
    """
    res: complex
    icT = INV_CAYLEY
    if z == -(icT[1, 0] / icT[1, 1]):
        res = np.infty
    else:
        res = (icT[0, 0] * z + icT[0, 1]) / (icT[1, 0] * z + icT[1, 1])

    # convert to float to satisfy optional static type checking; could be
    # removed with proper type annotation for `tVec`:
    res = complex(res)

    res = stabilize(res, model="H")  # improve numerical stability
    return res


def styleHyperbolicPlanePlot(
    model: str,
    ax: Any,
    xLimits: Tuple[float, float],
    yLimits: Tuple[float, float],
) -> None:
    """
    Style a plot of the upper halfplane of Poincare disc models of hyperbolic
    space within given limits. Limits are only applied in the upper halfplane
    model because the closed unit disc is compact.

    :param model: the model to use for styling
    :param ax: given matplotlib axes to style
    :param xLimits: the x-axis limits to apply
    :param yLimits: the y-axis limits to apply
    """
    if model == "H":
        ax.set_xlim(xLimits)
        ax.set_ylim(yLimits)
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


def checkConsistencyAndConvert(
    z1: tScal, z2: tScal, model: str
) -> Tuple[tScal, tScal]:
    """
    Check consistency of a given pair of points in the given model and map
    the points to the upper halfplane if necessary.

    TODO.
    """
    if model == "D":
        if abs(z1) > 1:
            raise InvalidDiskPoint(z1)
        if abs(z2) > 1:
            raise InvalidDiskPoint(z2)
        return DtoH(z1), DtoH(z2)
    if model == "H":
        if z1.imag < 0:
            raise InvalidHalfplanePoint(z1)
        if z2.imag < 0:
            raise InvalidHalfplanePoint(z2)
        return z1, z2

    raise InvalidModelException(model)
