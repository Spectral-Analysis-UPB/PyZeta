"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from __future__ import annotations

from typing import Final, List, Optional, Tuple, Type

import numpy as np
from numpy.typing import NDArray
from typing_extensions import Self

from pyzeta.core.pyzeta_types.general import tVec
from pyzeta.core.pyzeta_types.special import (
    tGroupElement,
    tIrreducibleRepr,
    tLetter,
    tWord,
)
from pyzeta.core.pyzeta_types.tables import (
    tActionTable,
    tCharacterTable,
    tDimensionTable,
    tGroupTable,
    tInversionTable,
    tOrderTable,
)
from pyzeta.core.symmetries.symmetry_group import SymmetryGroup


class TrivialGroup(SymmetryGroup):
    """
    Class representation of the trivial symmetry group. This group can be used
    in conjunction with every Schottky group but does not provide a non-trivial
    symmetry decomposition.
    """

    __slots__ = (
        "_elements",
        "_groupTable",
        "_inversionTable",
        "_characterTable",
        "_orderTable",
        "_dimensionTable",
        "_actionTable",
    )

    _instance: Optional[Self] = None

    def __new__(
        cls: Type[TrivialGroup], *args: object, **kwargs: object
    ) -> TrivialGroup:
        "Override `__new__` to implement singleton behaviour."
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        "Initialize the unique instance of this symmetry group."
        self._elements: Tuple[tGroupElement, ...] = (np.str_("id"),)
        self._groupTable: Final[tGroupTable] = {}
        self._inversionTable: Final[tInversionTable] = {}
        self._characterTable: Final[tCharacterTable] = {}
        self._orderTable: Final[tOrderTable] = {}
        self._dimensionTable: Final[tDimensionTable] = {}
        self._actionTable: Final[tActionTable] = {}

    # docstr-coverage: inherited
    def getElements(self) -> Tuple[tGroupElement, ...]:
        return self._elements

    # docstr-coverage: inherited
    def compose(
        self, elem1: tGroupElement, elem2: tGroupElement
    ) -> tGroupElement:
        if (elem1 not in self._groupTable) or (elem2 not in self._groupTable):
            raise ValueError(
                f"Can't compose: {elem1} and {elem2} not in the same group!"
            )

        return self._groupTable[elem1][elem2]

    # docstr-coverage: inherited
    def applyWord(self, elem: tGroupElement, word: tWord) -> tWord:
        if elem not in self._actionTable:
            raise ValueError(f"{elem} does not belong to this group!")
        res = [self._actionTable[elem][letter] for letter in word]
        return np.array(res, dtype=np.int16)

    # docstr-coverage: inherited
    def applyLetterArray(
        self, elemArray: NDArray[tGroupElement], letterArray: NDArray[tLetter]
    ) -> NDArray[tLetter]:
        result: List[tLetter] = []
        for elem, letter in zip(elemArray, letterArray):
            result.append(self._actionTable[elem][letter])
        return np.array(result)

    # docstr-coverage: inherited
    def elementPower(
        self, baseArray: NDArray[tGroupElement], exponent: int
    ) -> NDArray[tGroupElement]:
        result = np.empty_like(baseArray)
        for idx, elem in enumerate(baseArray):
            temp: tGroupElement = np.str_("id")
            for _ in range(exponent % self.order(elem)):
                temp = self.compose(temp, elem)
            result[idx] = temp
        return result

    # docstr-coverage: inherited
    def conjugate(
        self,
        elem1: tGroupElement,
        elem2: tGroupElement,
    ) -> tGroupElement:
        temp: tGroupElement = self.compose(elem1=elem2, elem2=elem1)
        return self.compose(temp, self._invert(elem2))

    def _invert(self, elem: tGroupElement) -> tGroupElement:
        """
        Invert a given group element within the group. This method is required
        for conjugation and not currently exposed publicly.

        :param elem: group element to invert
        :return: inverted input group element
        """
        if elem not in self._inversionTable:
            raise ValueError(f"Can't invert {elem} in this group!")
        return self._inversionTable[elem]

    # docstr-coverage: inherited
    def shiftAction(self, word: tWord, elem: tGroupElement) -> tWord:
        result = np.roll(word, 1)
        result[0] = self._actionTable[elem][result[0]]
        return result

    # docstr-coverage: inherited
    def wordPower(
        self, word: tWord, elem: tGroupElement, exponent: int
    ) -> Tuple[tWord, tGroupElement]:
        temp: tGroupElement = elem
        resultWord: tWord = word
        wordLen = len(word)
        for _ in range(exponent - 1):
            resultWord = np.concatenate(
                (self.applyWord(elem, resultWord[:wordLen]), resultWord)
            )
            temp = self.compose(temp, elem)
        return resultWord, temp

    # docstr-coverage: inherited
    def order(self, elem: tGroupElement) -> int:
        if elem not in self._orderTable:
            raise ValueError(f"Element {elem} has no order in this group!")
        return self._orderTable[elem]

    # docstr-coverage: inherited
    def character(
        self, irrRepr: tIrreducibleRepr, elems: NDArray[tGroupElement]
    ) -> tVec:
        if irrRepr not in self._characterTable:
            raise ValueError(
                f"representation {irrRepr} does not exist on {self}!",
            )
        return np.array([self._characterTable[irrRepr][elm] for elm in elems])

    # docstr-coverage: inherited
    def getDimension(self, irrRepr: tIrreducibleRepr) -> int:
        if irrRepr not in self._dimensionTable:
            raise ValueError(f"{irrRepr} doesn't belong to the group {self}!")
        return self._dimensionTable[irrRepr]
