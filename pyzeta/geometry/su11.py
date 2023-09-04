r"""
Module containing a class implementation of :math:`\mathrm{SU}(1, 1)` matrices
acting on the Poincare disc :math:`\mathbb{D}` via Moebius transformations.

Authors:\n
- Tobias Weich\n
- Philipp Schuette\n
- Sebastian Albrecht\n
"""

from __future__ import annotations

from cmath import isclose
from typing import Any, Optional, Tuple, Union, overload

import matplotlib.pyplot as plt  # type: ignore
import numpy as np
import numpy.linalg as lin
from matplotlib import patches

from pyzeta.core.pyzeta_types.general import tMat, tVec
from pyzeta.geometry.constants import CAYLEY, INV_CAYLEY, tScal
from pyzeta.geometry.geodesic import Geodesic
from pyzeta.geometry.geometry_exceptions import (
    InvalidDiskPoint,
    InvalidMatrixException,
)
from pyzeta.geometry.helpers import stabilize


class SU11:
    r"""
    Utility class representing symmetries of the Poincare disc, i.e.
    elements of :math:`\mathrm{SU}(1, 1)`.
    """

    __slots__ = "fixPt", "_A"

    def __init__(self, A: tMat) -> None:
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
        :raises InvalidMatrixException: Raised if `A` has zero
            determinant or if it does not satisfy other defining properties of
            :math:`\mathrm{SU}(1,1)`.
        """
        self.fixPt: Optional[Tuple[float, ...]] = None
        det = abs(A[0, 0]) ** 2 - abs(A[0, 1]) ** 2
        if (
            isclose(abs(det), 0.0, abs_tol=1e-6)
            or not isclose(A[0, 0].conjugate(), A[1, 1])
            or not isclose(A[0, 1].conjugate(), A[1, 0])
        ):
            raise InvalidMatrixException(A)

        self._A = 1.0 / np.sqrt(abs(det)) * A

    def __str__(self) -> str:
        r"""
        Return string representation of an element of :math:`\mathrm{SU}(1,1)`.

        :return: String representation of an element of
            :math:`\mathrm{SU}(1,1)`
        """
        return f"SU11({self._A.round(3)})"

    def __repr__(self) -> str:
        r"""
        Return string representation of an element of :math:`\mathrm{SU}(1,1)`.

        This method works identically as the __str__ method. It is necessary
        for a human readable string representation of lists of SU11 elements.

        :return: String representation of an element of
            :math:`\mathrm{SU}(1,1)`
        """
        return f"SU11({self._A.round(3)})"

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
        :raises InvalidDiskPoint: Raised for points outside Poincare Disk.
        :return: Transformed input
        """
        a: complex
        b: complex
        c: complex
        d: complex
        [[a, b], [c, d]] = self._A

        if isinstance(z, Geodesic):
            return Geodesic(self(z.td), self(z.ud), model="D")
        if isinstance(z, np.ndarray):
            z = stabilize(z, model="D")  # improve numerical stability
            if np.any(np.abs(z) > 1.0):
                invalidIdx = tuple(np.argwhere(np.abs(z) > 1.0)[0])
                raise InvalidDiskPoint(z[invalidIdx])
            return np.array((a * z + b) / (c * z + d))

        z = stabilize(z, model="D")  # improve numerical stability
        if np.abs(z) > 1.0:
            raise InvalidDiskPoint(z)
        return (a * z + b) / (c * z + d)

    def __len__(self) -> float:
        r"""
        Calculate displacement length of a hyperbolic element of
        :math:`\mathrm{SU}(1,1)`.

        :raises ValueError: Raised if the element is not hyperbolic.
        :return: Displacement length
        """
        trace = np.abs(self._A[0, 0] + self._A[1, 1])
        if trace <= 2:
            raise ValueError(
                "Trying to calculate displacement length for element that is"
                + " not hyperbolic"
            )
        res: float = 2.0 * np.arccosh(trace / 2.0)
        return res

    def __mul__(self, other: SU11) -> SU11:
        r"""
        Calculate matrix product of two elements of :math:`\mathrm{SU}(1,1)`.

        :param other: Element of :math:`\mathrm{SU}(1,1)`.
        :return: Matrix product of the two elements
        """
        return SU11(np.matmul(self._A, other._A))

    def __pow__(self, power: int) -> SU11:
        r"""
        Calculate matrix power of an element of :math:`\mathrm{SU}(1,1)`.

        :param power: Power to which the element is raised
        :return: Matrix power of the element
        """
        return SU11(lin.matrix_power(self._A, power))

    def inverse(self) -> SU11:
        r"""
        Calculate inverse of an element of :math:`\mathrm{SU}(1,1)`.

        The same as SU11.__pow__(-1).

        :return: Inverse of the element
        """
        return SU11(lin.inv(self._A))

    def getFixPt(self) -> Tuple[tScal, ...]:
        r"""
        Calculate fixed point(s) of an element of :math:`\mathrm{SU}(1,1)`.

        Only fixed point(s) inside :math:`\mathbb{D}` are returned. Fixed
        points outside :math:`\mathbb{D}` are discarded.

        :raises ValueError: Raised if the element is the unit element.
        :raises NotImplementedError: Raised if the element has negative
            determinant.
        :return: Fixed point(s) inside (the closure of) :math:`\mathbb{D}`
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
            self.fixPt = (0.0,)
            return self.fixPt

        # distinguish parabolic, elliptic, hyperbolic using trace
        trace = abs(a + d)
        # parabolic case:
        if isclose(trace, 2.0):
            x12 = (a - d) / (2.0 * c)
            self.fixPt = (x12,)
        # hyperbolic case:
        elif trace > 2.0:
            x1 = (a - d - np.sqrt(trace**2 - 4)) / (2.0 * c)
            x2 = (a - d + np.sqrt(trace**2 - 4)) / (2.0 * c)
            self.fixPt = (x1, x2)
        # elliptic case:
        else:
            x12 = (abs(a - d) * 1j - np.sqrt(4 - trace**2) * 1j) / (2.0 * c)
            self.fixPt = (x12,)

        return self.fixPt

    def plotFixPt(
        self, *, ax: Any = None, **kwargs: object
    ) -> Tuple[Any, Any]:
        r"""
        Calculate and plot fixed point(s) of an element of
        :math:`\mathrm{SU}(1, 1)`.

        :param ax: Matplotlib axes object in which the plot should be drawn. If
            None is passed, a new figure and axes are created, defaults to None
        :param \*\*kwargs: Keyword arguments for matplotlib.pyplot.scatter().
        :raises ValueError: Raised if not fixed points in :math:`\mathbb{D}`.
        :return: Matplotlib figure and axes object with the new plot inside
        """
        fixPts = self.getFixPt()
        if fixPts is None or fixPts == ():
            raise ValueError(f"{self} has no fixed point(s) in D")

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

        circle = patches.Arc((0, 0), 2, 2)
        ax.add_patch(circle)

        ax.scatter(x, y, **kwargs)

        return ax.get_figure(), ax

    def getIsoCirc(self) -> Geodesic:
        """
        TODO: What does this method do?
        Rename once we are sure what it does!
        """
        g = INV_CAYLEY @ self._A @ CAYLEY
        det = g[0, 0] * g[1, 1] - g[0, 1] * g[1, 0]
        g = 1.0 / np.sqrt(abs(det)) * g

        x1 = -g[1, 1] / g[1, 0] + np.abs(1.0 / g[1, 0])
        x2 = -g[1, 1] / g[1, 0] - np.abs(1.0 / g[1, 0])

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
        """
        try:
            x1, x2 = self.getFixPt()
        except (TypeError, ValueError) as error:
            raise ValueError(
                "Can only generate unique geodesic for hyperbolic elements"
            ) from error
        res = Geodesic(x1, x2, model="D")
        return res
