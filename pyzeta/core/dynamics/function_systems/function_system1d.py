"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from abc import ABC, abstractmethod


class FunctionSystem1d(ABC):
    "Abstract representation of an (iterated) function system."

    @abstractmethod
    def getStabilities(self, words: tWordVec) -> tVec:
        "TODO."

    @abstractmethod
    def getFixedPoints(self, words: tWordVec) -> tVec:
        "TODO."
