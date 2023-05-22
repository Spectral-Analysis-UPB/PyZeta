"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from numpy import int16, str_
from numpy.typing import NDArray
from typing_extensions import TypeAlias

# type alias for elements of discrete symmetry groups
tGroupElement: TypeAlias = str_

# type alias for entries in symbolic words
tLetter: TypeAlias = int16

# type alias for elements of tWordVec arrays, i.e. words (1d integer arrays)
tWord: TypeAlias = NDArray[tLetter]
