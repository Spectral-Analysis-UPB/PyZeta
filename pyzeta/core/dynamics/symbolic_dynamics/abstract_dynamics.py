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
        nMax: int,
        prime: bool = False,
        permFree: bool = False,
        cyclRed: bool = False,
    ) -> Iterator[Tuple[tWordVec, NDArray[tGroupElement]]]:
        """
        TODO.

        :param nMax:
        :param prime:
        :param permFree:
        :param cyclRed:
        :return:
        """
