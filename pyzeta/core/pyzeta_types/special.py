"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from numpy import bool_, str_, uint8
from numpy.typing import NDArray
from typing_extensions import TypeAlias

# type alias for entries in symbolic words
tLetter: TypeAlias = uint8

# type alias for elements of tWordVec arrays, i.e. words (1d integer arrays)
tWord: TypeAlias = NDArray[tLetter]

# type alias for boolean masks
tMask: TypeAlias = NDArray[bool_]

# type alias for elements of discrete symmetry groups
tGroupElement: TypeAlias = str_

# type alias for irreducible representations of discrete symmetry groups
tIrreducibleRepr: TypeAlias = str
