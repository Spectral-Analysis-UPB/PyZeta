"""
Module containing general type aliases for use with the algorithms in the
pyzeta.core package.

Authors:\n
- Philipp Schuette\n
"""

from numpy import bool_, complex128, float64, uint8
from numpy.typing import NDArray
from typing_extensions import TypeAlias

# type used for 1d arrays of complex numbers
tVec: TypeAlias = NDArray[complex128]

# type used for 2d arrays of complex numbers
tMat: TypeAlias = NDArray[complex128]

# type used for 1d arrays of 2x2 matrices of complex numbers (effectively 3d)
tMatVec: TypeAlias = NDArray[float64]

# type used for 1d arrays of symbolic words (effectively 2d arrays)
tWordVec: TypeAlias = NDArray[uint8]

# type used for 1d arrays of orbit integral matrices (effectively 3d arrays)
tIntegralVec: TypeAlias = NDArray[float64]

# type used for 2d matrices of boolean values
tBoolMat: TypeAlias = NDArray[bool_]
