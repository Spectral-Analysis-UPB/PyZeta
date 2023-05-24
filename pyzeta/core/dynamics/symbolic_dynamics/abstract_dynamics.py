"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from abc import ABC, abstractmethod
from typing import Iterator, Tuple

from numpy.typing import NDArray

from pyzeta.core.pyzeta_types.general import tWordVec
from pyzeta.core.pyzeta_types.special import tGroupElement
from pyzeta.framework.pyzeta_logging.loggable import Loggable


class AbstractSymbolicDynamics(ABC, Loggable):
    """
    Abstract class representation of symbolic dynamics. Concrete
    implementations can hook into this template by implementing the various
    word filtering methods.
    """

    @abstractmethod
    def wordGenerator(
        self,
        maxWordLength: int,
        prime: bool = False,
        permFree: bool = False,
        cyclRed: bool = False,
    ) -> Iterator[Tuple[tWordVec, NDArray[tGroupElement]]]:
        """
        Return a generator that yields all symbolic words up to a maximal word
        length and satisfying certain given properties together with associated
        group elements. Implementations may choose to return an empty array of
        symmetries effectively reducing the symmetry to the trivial one-element
        group.

        :param maxWordLength: maximal word length before the generator expires
        :param prime: flag indicating if non-prime words are filtered
        :param permFree: flag indicating if permutations of words are filtered
        :param cyclRed: flag indicating if non-cyclically reduced words are
            filtered
        :return: a generator of parallel arrays of words and symmetries
        """
