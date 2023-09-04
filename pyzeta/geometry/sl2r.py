r"""
Module containing a class implementation of :math:`\mathrm{SL}(2, \mathbb{R})`
matrices acting on the upper half plane :math:`\mathbb{H}` via Moebius
transformations.

Authors:\n
- Tobias Weich\n
- Philipp Schuette\n
- Sebastiant Albrecht\n
"""

from __future__ import annotations

from cmath import isclose
from typing import Any, Optional, Tuple, Union, overload

import matplotlib.pyplot as plt  # type: ignore
import numpy as np
import numpy.linalg as lin

from pyzeta.core.pyzeta_types.general import tMat, tVec
from pyzeta.geometry.constants import tScal
from pyzeta.geometry.geodesic import Geodesic
from pyzeta.geometry.geometry_exceptions import InvalidHalfplanePoint
from pyzeta.geometry.helpers import stabilize


class SL2R:
    r"""
    Utility class representing symmetries of the Upper Halfplane
    :math:`\mathbb{H}`, i.e. elements of :math:`\mathrm{SL}(2, \mathbb{R})`.
    """

    __slots__ = "fixPt", "_A"

    def __init__(self, A: tMat) -> None:
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
        :raises InvalidMatrixException: Raised if `A` has zero determinant.
        """
        self.fixPt: Optional[Tuple[tScal, ...]] = None
        det = A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0]
        if isclose(abs(det), 0.0, abs_tol=1e-6):
            # TODO: does this really make sense?
            # raise InvalidMatrixException(A)
            pass

        self._A = 1.0 / np.sqrt(abs(det)) * A
        # TODO: what's happening here?
        # self._A = A

    def __str__(self) -> str:
        r"""
        Return string representation of an element of
        :math:`\mathrm{SL}(2, \mathbb{R})`.

        :return: String representation of an element of
            :math:`\mathrm{SL}(2, \mathbb{R})`
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
        """
        return f"SL2R({self._A.round(3)})"

    # docstr-coverage: inherited
    @overload
    def __call__(self, z: Geodesic) -> Geodesic:
        ...

    # docstr-coverage: inherited
    @overload
    def __call__(self, z: tScal) -> tScal:
        ...

    # docstr-coverage: inherited
    @overload
    def __call__(self, z: tVec) -> tVec:
        ...

    def __call__(
        self, z: Union[Geodesic, tScal, tVec]
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
        :raises InvalidHalfplanePoint: Raised for points outside Upper
            Halfplane.
        :return: Transformed input
        """
        a: float
        b: float
        c: float
        d: float
        [[a, b], [c, d]] = self._A

        if isinstance(z, Geodesic):
            return Geodesic(self(z.t), self(z.u))

        if isinstance(z, np.ndarray):
            z = stabilize(z, model="H")  # improve numerical stability
            if np.any(np.imag(z) < 0.0):
                invalidIdx = tuple(np.argwhere(np.imag(z) < 0.0)[0])
                raise InvalidHalfplanePoint(z[invalidIdx])
            res = np.zeros_like(z)
            mask = z != np.infty

            res[mask] = (a * z[mask] + b) / (c * z[mask] + d)
            if c != 0:
                res[~mask] = a / c
            else:
                res[~mask] = np.infty
            return res

        z = stabilize(z, model="H")  # improve numerical stability
        if np.imag(z) < 0.0:
            raise InvalidHalfplanePoint(z)
        if z != np.infty:
            return (a * z + b) / (c * z + d)
        if c != 0:
            return a / c
        return np.infty

    def __len__(self) -> float:
        r"""
        Calculate displacement length of a hyperbolic element of
        :math:`\mathrm{SL}(2, \mathbb{R})`.

        :raises ValueError: Raised if the element is not hyperbolic.
        :return: Displacement length
        """
        trace = np.abs(self._A[0, 0] + self._A[1, 1])
        if trace <= 2:
            raise ValueError(
                "no displacement length for element that is not hyperbolic!"
            )

        res: float = 2.0 * np.arccosh(trace / 2.0)
        return res

    def __mul__(self, other: SL2R) -> SL2R:
        r"""
        Calculate matrix product of two elements of
        :math:`\mathrm{SL}(2, \mathbb{R})`.

        :param other: Element of :math:`\mathrm{SL}(2, \mathbb{R})`
        :return: Matrix product of the two elements
        """
        return SL2R(np.matmul(self._A, other._A))

    def __pow__(self, power: int) -> SL2R:
        r"""
        Calculate matrix power of an element of
        :math:`\mathrm{SL}(2, \mathbb{R})`.

        :param power: Power to which the element is raised
        :return: Matrix power of the element
        """
        return SL2R(lin.matrix_power(self._A, power))

    def inverse(self) -> SL2R:
        r"""
        Calculate inverse of an element of :math:`\mathrm{SL}(2, \mathbb{R})`.

        The same as SL2R.__pow__(-1).

        :return: Inverse of the element
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
        """
        if self.fixPt is not None:
            return self.fixPt

        [[a, b], [c, d]] = self._A
        if a * d - b * c < 0:
            raise NotImplementedError(
                "Fixed points not implemented for orientation-reversing trafo"
            )
        if [[a, b], [c, d]] == [[1, 0], [0, 1]]:
            raise ValueError("Trying to calculate fixed points of identity!")

        if c == 0:
            if not isclose(d, a):
                self.fixPt = (b / (d - a), np.infty)
            else:
                self.fixPt = (np.infty,)
            return self.fixPt

        # distinguish parabolic, elliptic, hyperbolic using trace
        trace = abs(a + d)
        # parabolic case:
        if isclose(trace, 2.0):
            x12 = (a - d) / (2.0 * c)
            self.fixPt = (x12,)
        # hyperbolic case:
        elif trace > 2:
            x1 = (a - d - np.sqrt(trace**2 - 4)) / (2.0 * c)
            x2 = (a - d + np.sqrt(trace**2 - 4)) / (2.0 * c)
            self.fixPt = (x1, x2)
        # elliptic case:
        else:
            x12 = (a - d) / (2.0 * c) + np.sqrt(4 - trace**2) * 1j / (
                2.0 * abs(c)
            )
            self.fixPt = (x12,)

        return self.fixPt

    def plotFixPt(
        self, *, ax: Any = None, **kwargs: object
    ) -> Tuple[Any, Any]:
        r"""
        Calculate and plot fixed point(s) of an element of
        :math:`\mathrm{SL}(2, \mathbb{R})`.

        :param ax: Matplotlib axes object in which the plot should be drawn. If
            None is passed, a new figure and axes are created, defaults to None
        :param \*\*kwargs: Keyword arguments are passed to
            matplotlib.pyplot.scatter().
        :raises ValueError: Raised if the element has no fixed points in
            :math:`\mathbb{H}`.
        :return: Matplotlib figure and matplotlib axes object in which the plot
            is drawn
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
        ax.text(
            1,
            1,
            r"$\mathbb{H}$",
            horizontalalignment="right",
            verticalalignment="top",
            transform=ax.transAxes,
            fontsize="xx-large",
        )

        ax.scatter(x, y, **kwargs)
        if np.infty in x:
            ax.scatter(0.5, 1, **kwargs, transform=ax.transAxes)
            ax.text(
                0.5,
                1,
                r"$\infty$",
                horizontalalignment="right",
                verticalalignment="bottom",
                fontsize="x-large",
                transform=ax.transAxes,
            )

        return ax.get_figure(), ax

    def getIsoCirc(self) -> Geodesic:
        """
        TODO: What does this method do? Rename once we are sure, what it does!
        """
        x1 = -self._A[1, 1] / self._A[1, 0] + np.abs(1.0 / self._A[1, 0])
        x2 = -self._A[1, 1] / self._A[1, 0] - np.abs(1.0 / self._A[1, 0])
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
        """
        try:
            x1, x2 = self.getFixPt()  # type: ignore
        except (TypeError, ValueError, NotImplementedError) as error:
            raise ValueError(
                "Can only generate unique geodesic for hyperbolic elements"
            ) from error
        res = Geodesic(x1, x2, model="H")
        return res
