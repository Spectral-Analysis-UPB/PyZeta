"""
Module containing global constants used in geometry helpers and convenience
functions.

Authors:\n
- Philipp Schuette\n
"""

from typing import Final, Union

from numpy import array, complex128
from numpy.typing import NDArray
from typing_extensions import TypeAlias

# in our convention we have the following correspondence 'H' -> 'D':
# 0 -> 1, 1 -> 1j, infty -> -1, -1 -> -1j
CAYLEY: Final[NDArray[complex128]] = array([[-1.0, 1.0j], [1.0, 1.0j]])
INV_CAYLEY: Final[NDArray[complex128]] = array([[1.0, -1.0], [1.0j, 1.0j]])

# simple type alias used throughout
tScal: TypeAlias = Union[float, complex]
