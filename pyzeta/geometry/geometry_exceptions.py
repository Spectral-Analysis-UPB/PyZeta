"""
Module containing custom exceptions used with geometry helper and convenience
functions.

Authors:\n
- Philipp Schuette\n
"""


class InvalidModelException(Exception):
    """
    Raised when input model parameter is neither 'H' (Upper Halfplane) nor 'D'
    (Poincare Disk).
    """

    def __str__(self) -> str:
        "String representation of the exception."
        return f"InvalidModelException({self.args[0]})"


class InvalidDiskPoint(Exception):
    """
    Raised when input points expected inside the Poincare Disk have
    absolute value larger than one.
    """

    def __str__(self) -> str:
        "String representation of the exception."
        return f"InvalidDiskPoint({self.args[0]})"


class InvalidHalfplanePoint(Exception):
    """
    Raised when input points expected inside the Upper Half Plane have
    imaginary part less than zero.
    """

    def __str__(self) -> str:
        "String representation of the exception."
        return f"InvalidHalfplanePoint({self.args[0]})"


class InvalidGeodesicException(Exception):
    """
    Raised when a unique geodesic curve cannot be created through a given
    pair of points.
    """

    def __init__(self, val1: complex, val2: complex) -> None:
        """
        Raise an exception that no valid geodesic exists through the points
        `val1` and `val2`.

        :param val1: Point on the complex plane
        :param val2: Point on the complex plane
        """
        super().__init__((val1, val2))

    def __str__(self) -> str:
        "String representation of the exception."
        return f"Cannot create unique geodesic from {self.args[0]}"


class InvalidMatrixException(Exception):
    """
    Raised when input matrix expected in certain Matrix Group does not satisfy
    the defining group properties.
    """

    def __str__(self) -> str:
        "String representation of the exception."
        return f"InvalidSymmetryException({self.args[0]})"
