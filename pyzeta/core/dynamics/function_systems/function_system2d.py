"""
- only expose methods which are absolutely required by zeta functions or
  dynamical determinants
- use separate services to provide the potentials to the zeta functions
- use internal caching and similar mechanisms to reduce redundancy

Authors:\n
- Philipp Schuette\n
"""

from abc import ABC, abstractmethod
from typing import Tuple


class FunctionSystem2d(ABC):
    "Abstract representation of an (iterated) function system."

    @abstractmethod
    def getStabilities(self, words: tWordVec) -> Tuple[tVec, tVec]:
        "TODO."

    @abstractmethod
    def getFixedPoints(self, words: tWordVec) -> Tuple[tVec, tVec]:
        "TODO."
