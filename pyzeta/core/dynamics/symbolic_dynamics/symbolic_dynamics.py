"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from typing import Iterator, Optional, Tuple

from numpy import empty
from numpy.typing import NDArray

from pyzeta.core.dynamics.symbolic_dynamics.abstract_dynamics import (
    AbstractSymbolicDynamics,
)
from pyzeta.core.dynamics.symbolic_dynamics.helpers.filters import (
    appendWordsFast,
    filterPermsFast,
    getWordsFast,
    isCyclRedFast,
    isPeriodicFast,
    isPrimeFast,
)
from pyzeta.core.pyzeta_types.general import tBoolMat, tWordVec
from pyzeta.core.pyzeta_types.special import tGroupElement, tLetter


class SymbolicDynamics(AbstractSymbolicDynamics):
    "Class representation of a plain (without reduction) symbolic dynamics."

    __slots__ = ("_adj", "_alphabetSize")

    def __init__(self, adjacencyMatrix: tBoolMat) -> None:
        """
        Initialize a new symbolic dynamics instance from a given adjacency
        relation.

        :param adjacencyMatrix: square adjacency matrix of the dynamics
        """
        self._adj = adjacencyMatrix
        self._alphabetSize = adjacencyMatrix.shape[0]
        self.logger.info(
            "new symbolic dynamics for %s initialized!", str(self._adj)
        )

    def __str__(self) -> str:
        "Simple string representation of symbolic dynamics implementations."
        return f"{self.__class__.__name__}({self._alphabetSize}, {self._adj})"

    def getSymbolicWords(
        self,
        wordLength: int,
        givenWords: Optional[tWordVec] = None,
        *,
        prime: bool = False,
        permFree: bool = False,
        cyclRed: bool = False,
        periodic: bool = False,
    ) -> tWordVec:
        """
        Generate all words of length `wordLength` satisfying (a combination of)
        various attributes.

        If an array of `givenWords` is passed then the resulting words are
        constructed by appending to them. Therefore usually `givenWords` should
        contain all possible words of some length <`wordLength`.

        :param wordLength: Length of words to be generated
        :param givenWords: Array of starting words of length <`wordLength`
        :param prime: generate only prime words
        :param permFree: exclude permutations of words
        :param cyclRed: generate only cyclically reduced words
        :param periodic: generate only periodic words
        :return: Array of words of length `wordLength` with given properties
        :raises ValueError: raised if `givenWords` have length >`wordLength`
        """
        if givenWords is None:
            words = getWordsFast(wordLength, self._adj)
        else:
            if (givenWordsLen := givenWords.shape[1]) > wordLength:
                raise ValueError(
                    f"can't append words of length {givenWordsLen} to words of"
                    f" shorter length {wordLength}!"
                )

            if givenWordsLen == wordLength:
                words = givenWords.astype(dtype=tLetter)
            else:
                words = appendWordsFast(
                    wordLength, self._adj, givenWords.astype(dtype=tLetter)
                )

        if prime:
            # pylint: disable=no-value-for-parameter
            words = words[isPrimeFast(words)]
        if permFree:
            words = words[filterPermsFast(words)]
        if cyclRed:
            # pylint: disable=no-value-for-parameter
            words = words[isCyclRedFast(words, self._adj)]
        if periodic:
            # pylint: disable=no-value-for-parameter
            words = words[isPeriodicFast(words)]

        self.logger.debug("generated symbolic words %s", str(words))
        return words  # type: ignore

    # docstr-coverage: inherited
    def wordGenerator(
        self,
        maxWordLength: int,
        prime: bool = False,
        permFree: bool = False,
        cyclRed: bool = False,
    ) -> Iterator[Tuple[tWordVec, NDArray[tGroupElement]]]:
        if maxWordLength < 1:
            return

        allWords = getWordsFast(n=1, adj=self._adj)
        currentElems = empty([], dtype=tGroupElement)

        # return words of length one
        yield self.getSymbolicWords(
            wordLength=1,
            givenWords=allWords,
            prime=prime,
            permFree=permFree,
            cyclRed=cyclRed,
        ), currentElems

        for wordLength in range(2, maxWordLength + 1):
            allWords = appendWordsFast(wordLength, self._adj, allWords)
            yield self.getSymbolicWords(
                wordLength=wordLength,
                givenWords=allWords,
                prime=prime,
                permFree=permFree,
                cyclRed=cyclRed,
            ), currentElems
