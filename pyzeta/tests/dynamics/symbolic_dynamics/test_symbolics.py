"""
Tests for ordinary (i.e. not symmetry reduced) symbolic dynamics as implemented
in the module `pyzeta.core.dynamics.symbolic_dynamics.symbolic_dynamics. from
the `PyZeta` project.

Authors:
- Sebastian Albrecht\n
- Philipp Schütte\n
"""

import numpy as np
import pytest as pt

from pyzeta.core.dynamics.symbolic_dynamics.symbolic_dynamics import (
    SymbolicDynamics,
)
from pyzeta.core.pyzeta_types.general import tBoolMat
from pyzeta.framework.initialization.initialization_handler import (
    PyZetaInitializationHandler,
)
from pyzeta.tests.resources.symbolics import (
    ADJ_UNIT_TEST_CASES,
    SymbolicsTestCase,
)

PyZetaInitializationHandler.initPyZetaServices()


@pt.mark.parametrize("testCase", ADJ_UNIT_TEST_CASES)
def testSymbolicDynamicsUnit(
    testCase: SymbolicsTestCase, adjUnit: tBoolMat
) -> None:
    "Test functionality of SymbolicDynamics class on 4x4 unit matrix."
    sdyn = SymbolicDynamics(adjUnit)

    # test for an invalid size of given words
    with pt.raises(ValueError):
        sdyn.getSymbolicWords(
            wordLength=testCase.configuration["wordLength"] - 1,
            givenWords=testCase.expectedWords,
        )

    assert np.all(
        sdyn.getSymbolicWords(**testCase.configuration)
        == testCase.expectedWords
    )


def testSymbolicDynamicsInvUnit(adjInverseUnit: tBoolMat) -> None:
    """
    Test functionality of SymbolicDynamics class on 4x4 boolean inverse of the
    unit matrix.
    """
    sdyn = SymbolicDynamics(adjInverseUnit)

    words = np.array(
        [
            [0, 1, 0, 1],
            [0, 1, 0, 2],
            [0, 1, 0, 3],
            [0, 1, 2, 0],
            [0, 1, 2, 1],
            [0, 1, 2, 3],
            [0, 1, 3, 0],
            [0, 1, 3, 1],
            [0, 1, 3, 2],
            [0, 2, 0, 1],
        ]
    )
    generatedWords = sdyn.getSymbolicWords(4)
    assert np.all(generatedWords[:10] == words)

    givenWords = np.array(
        [
            [0, 1, 0],
            [0, 1, 2],
            [0, 1, 3],
            [0, 2, 0],
            [0, 2, 1],
            [0, 2, 3],
            [0, 3, 0],
            [0, 3, 1],
            [0, 3, 2],
            [1, 0, 1],
            [1, 0, 2],
            [1, 0, 3],
            [1, 2, 0],
            [1, 2, 1],
            [1, 2, 3],
            [1, 3, 0],
            [1, 3, 1],
            [1, 3, 2],
            [2, 0, 1],
            [2, 0, 2],
            [2, 0, 3],
            [2, 1, 0],
            [2, 1, 2],
            [2, 1, 3],
            [2, 3, 0],
            [2, 3, 1],
            [2, 3, 2],
            [3, 0, 1],
            [3, 0, 2],
            [3, 0, 3],
            [3, 1, 0],
            [3, 1, 2],
            [3, 1, 3],
            [3, 2, 0],
            [3, 2, 1],
            [3, 2, 3],
        ]
    )
    origGivenWords = np.copy(givenWords)
    appendedWords = sdyn.getSymbolicWords(4, givenWords)
    assert np.all(appendedWords == generatedWords)
    assert np.all(origGivenWords == givenWords)

    wordsPrime = np.array(
        [
            [0, 1, 0, 2],
            [0, 1, 0, 3],
            [0, 1, 2, 0],
            [0, 1, 2, 1],
            [0, 1, 2, 3],
            [0, 1, 3, 0],
            [0, 1, 3, 1],
            [0, 1, 3, 2],
            [0, 2, 0, 1],
            [0, 2, 0, 3],
        ]
    )
    assert np.all(sdyn.getSymbolicWords(4, prime=True)[:10] == wordsPrime)

    wordsPeriodic = np.array(
        [
            [0, 1, 2, 0],
            [0, 1, 3, 0],
            [0, 2, 1, 0],
            [0, 2, 3, 0],
            [0, 3, 1, 0],
            [0, 3, 2, 0],
            [1, 0, 2, 1],
            [1, 0, 3, 1],
            [1, 2, 0, 1],
            [1, 2, 3, 1],
        ]
    )
    assert np.all(
        sdyn.getSymbolicWords(4, periodic=True)[:10] == wordsPeriodic
    )

    wordsPrimePeriodic = np.array(
        [
            [0, 1, 2, 0],
            [0, 1, 3, 0],
            [0, 2, 1, 0],
            [0, 2, 3, 0],
            [0, 3, 1, 0],
            [0, 3, 2, 0],
            [1, 0, 2, 1],
            [1, 0, 3, 1],
            [1, 2, 0, 1],
            [1, 2, 3, 1],
        ]
    )
    assert np.all(
        sdyn.getSymbolicWords(4, prime=True, periodic=True)[:10]
        == wordsPrimePeriodic
    )

    wordsPermFree = np.array(
        [
            [0, 1, 0, 1],
            [0, 1, 0, 2],
            [0, 1, 0, 3],
            [0, 1, 2, 0],
            [0, 1, 2, 1],
            [0, 1, 2, 3],
            [0, 1, 3, 0],
            [0, 1, 3, 1],
            [0, 1, 3, 2],
            [0, 2, 0, 2],
        ]
    )
    assert np.all(
        sdyn.getSymbolicWords(4, permFree=True)[:10] == wordsPermFree
    )


def testSymbolicDynamicsFull(adjFull: tBoolMat) -> None:
    """
    Test functionality of SymbolicDynamics class on 3x3 completely filled
    matrix.
    """
    sdyn = SymbolicDynamics(adjFull)

    words = np.array(
        [
            [0, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 2],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 1, 2],
            [0, 0, 2, 0],
            [0, 0, 2, 1],
            [0, 0, 2, 2],
            [0, 1, 0, 0],
        ]
    )
    generatedWords = sdyn.getSymbolicWords(4)
    assert np.all(generatedWords[:10] == words)

    givenWords = np.array(
        [
            [0, 0],
            [0, 1],
            [0, 2],
            [1, 0],
            [1, 1],
            [1, 2],
            [2, 0],
            [2, 1],
            [2, 2],
        ]
    )
    appendedWords = sdyn.getSymbolicWords(4, givenWords)
    assert np.all(appendedWords == generatedWords)

    wordsPrime = np.array(
        [
            [0, 0, 0, 1],
            [0, 0, 0, 2],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 1, 2],
            [0, 0, 2, 0],
            [0, 0, 2, 1],
            [0, 0, 2, 2],
            [0, 1, 0, 0],
            [0, 1, 0, 2],
        ]
    )
    assert np.all(sdyn.getSymbolicWords(4, prime=True)[:10] == wordsPrime)

    wordsPeriodic = np.array(
        [
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 2, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 2, 0],
            [0, 2, 0, 0],
            [0, 2, 1, 0],
            [0, 2, 2, 0],
            [1, 0, 0, 1],
        ]
    )
    assert np.all(
        sdyn.getSymbolicWords(4, periodic=True)[:10] == wordsPeriodic
    )

    wordsPrimePeriodic = np.array(
        [
            [0, 0, 1, 0],
            [0, 0, 2, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 2, 0],
            [0, 2, 0, 0],
            [0, 2, 1, 0],
            [0, 2, 2, 0],
            [1, 0, 0, 1],
            [1, 0, 1, 1],
        ]
    )
    assert np.all(
        sdyn.getSymbolicWords(4, prime=True, periodic=True)[:10]
        == wordsPrimePeriodic
    )

    wordsPermFree = np.array(
        [
            [0, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 2],
            [0, 0, 1, 1],
            [0, 0, 1, 2],
            [0, 0, 2, 1],
            [0, 0, 2, 2],
            [0, 1, 0, 1],
            [0, 1, 0, 2],
            [0, 1, 1, 1],
        ]
    )
    assert np.all(
        sdyn.getSymbolicWords(4, permFree=True)[:10] == wordsPermFree
    )


def testSymbolicDynamicsSparse(adjSparse: tBoolMat) -> None:
    "Test functionality of SymbolicDynamics class on 5x5 sparse matrix."
    sdyn = SymbolicDynamics(adjSparse)

    words = np.array(
        [
            [0, 0, 0],
            [0, 0, 2],
            [0, 0, 4],
            [0, 2, 0],
            [0, 2, 2],
            [0, 2, 4],
            [0, 4, 0],
            [0, 4, 2],
            [0, 4, 4],
            [1, 1, 1],
        ]
    )
    generatedWords = sdyn.getSymbolicWords(3)
    assert np.all(generatedWords[:10] == words)

    givenWords = np.array(
        [
            [0, 0],
            [0, 2],
            [0, 4],
            [1, 1],
            [1, 3],
            [2, 0],
            [2, 2],
            [2, 4],
            [3, 1],
            [3, 3],
            [4, 0],
            [4, 2],
            [4, 4],
        ]
    )
    appendedWords = sdyn.getSymbolicWords(3, givenWords)
    assert np.all(appendedWords == generatedWords)

    wordsPrime = np.array(
        [
            [0, 0, 2],
            [0, 0, 4],
            [0, 2, 0],
            [0, 2, 2],
            [0, 2, 4],
            [0, 4, 0],
            [0, 4, 2],
            [0, 4, 4],
            [1, 1, 3],
            [1, 3, 1],
        ]
    )
    assert np.all(sdyn.getSymbolicWords(3, prime=True)[:10] == wordsPrime)

    wordsPeriodic = np.array(
        [
            [0, 0, 0],
            [0, 2, 0],
            [0, 4, 0],
            [1, 1, 1],
            [1, 3, 1],
            [2, 0, 2],
            [2, 2, 2],
            [2, 4, 2],
            [3, 1, 3],
            [3, 3, 3],
        ]
    )
    assert np.all(
        sdyn.getSymbolicWords(3, periodic=True)[:10] == wordsPeriodic
    )

    wordsPrimePeriodic = np.array(
        [
            [0, 2, 0],
            [0, 4, 0],
            [1, 3, 1],
            [2, 0, 2],
            [2, 4, 2],
            [3, 1, 3],
            [4, 0, 4],
            [4, 2, 4],
        ]
    )
    assert np.all(
        sdyn.getSymbolicWords(3, prime=True, periodic=True)
        == wordsPrimePeriodic
    )

    wordsPermFree = np.array(
        [
            [0, 0, 0],
            [0, 0, 2],
            [0, 0, 4],
            [0, 2, 2],
            [0, 2, 4],
            [0, 4, 2],
            [0, 4, 4],
            [1, 1, 1],
            [1, 1, 3],
            [1, 3, 3],
        ]
    )
    assert np.all(
        sdyn.getSymbolicWords(3, permFree=True)[:10] == wordsPermFree
    )


def testSymbolicDynamicsBlock(adjBlock: tBoolMat) -> None:
    "Test functionality of SymbolicDynamics class on 3x3 block matrix."
    sdyn = SymbolicDynamics(adjBlock)

    words = np.array(
        [
            [0, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 2],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 1, 2],
            [0, 0, 2, 2],
            [0, 1, 0, 0],
            [0, 1, 0, 1],
            [0, 1, 0, 2],
        ]
    )
    generatedWords = sdyn.getSymbolicWords(4)
    assert np.all(generatedWords[:10] == words)

    givenWords = np.copy(generatedWords)
    appendedWords = sdyn.getSymbolicWords(4, givenWords)
    assert np.all(appendedWords == generatedWords)

    wordsPrime = np.array(
        [
            [0, 0, 0, 1],
            [0, 0, 0, 2],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 1, 2],
            [0, 0, 2, 2],
            [0, 1, 0, 0],
            [0, 1, 0, 2],
            [0, 1, 1, 0],
            [0, 1, 1, 1],
        ]
    )
    assert np.all(sdyn.getSymbolicWords(4, prime=True)[:10] == wordsPrime)

    wordsPeriodic = np.array(
        [
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [1, 0, 0, 1],
            [1, 0, 1, 1],
            [1, 1, 0, 1],
            [1, 1, 1, 1],
            [2, 2, 2, 2],
        ]
    )
    assert np.all(sdyn.getSymbolicWords(4, periodic=True) == wordsPeriodic)

    wordsPrimePeriodic = np.array(
        [
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [1, 0, 0, 1],
            [1, 0, 1, 1],
            [1, 1, 0, 1],
        ]
    )
    assert np.all(
        sdyn.getSymbolicWords(4, prime=True, periodic=True)
        == wordsPrimePeriodic
    )

    wordsPermFree = np.array(
        [
            [0, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 2],
            [0, 0, 1, 1],
            [0, 0, 1, 2],
            [0, 0, 2, 2],
            [0, 1, 0, 1],
            [0, 1, 0, 2],
            [0, 1, 1, 1],
            [0, 1, 1, 2],
        ]
    )
    assert np.all(
        sdyn.getSymbolicWords(4, permFree=True)[:10] == wordsPermFree
    )


def testSymbolicDynamicsSchottky(adjSchottky: tBoolMat) -> None:
    "Test functionality of SymbolicDynamics class on 4x4 Schottky matrix."
    sdyn = SymbolicDynamics(adjSchottky)

    words = np.array(
        [
            [0, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 3],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 1, 2],
            [0, 0, 3, 0],
            [0, 0, 3, 2],
            [0, 0, 3, 3],
            [0, 1, 0, 0],
        ]
    )
    generatedWords = sdyn.getSymbolicWords(4)
    assert np.all(generatedWords[:10] == words)

    givenWords = np.array(
        [
            [0, 0],
            [0, 1],
            [0, 3],
            [1, 0],
            [1, 1],
            [1, 2],
            [2, 1],
            [2, 2],
            [2, 3],
            [3, 0],
            [3, 2],
            [3, 3],
        ]
    )
    appendedWords = sdyn.getSymbolicWords(4, givenWords)
    assert np.all(appendedWords == generatedWords)

    wordsPrime = np.array(
        [
            [0, 0, 0, 1],
            [0, 0, 0, 3],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 1, 2],
            [0, 0, 3, 0],
            [0, 0, 3, 2],
            [0, 0, 3, 3],
            [0, 1, 0, 0],
            [0, 1, 0, 3],
        ]
    )
    assert np.all(sdyn.getSymbolicWords(4, prime=True)[:10] == wordsPrime)

    wordsPeriodic = np.array(
        [
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 3, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 3, 0, 0],
            [0, 3, 3, 0],
            [1, 0, 0, 1],
            [1, 0, 1, 1],
            [1, 1, 0, 1],
        ]
    )
    assert np.all(
        sdyn.getSymbolicWords(4, periodic=True)[:10] == wordsPeriodic
    )

    wordsPrimePeriodic = np.array(
        [
            [0, 0, 1, 0],
            [0, 0, 3, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 3, 0, 0],
            [0, 3, 3, 0],
            [1, 0, 0, 1],
            [1, 0, 1, 1],
            [1, 1, 0, 1],
            [1, 1, 2, 1],
        ]
    )
    assert np.all(
        sdyn.getSymbolicWords(4, prime=True, periodic=True)[:10]
        == wordsPrimePeriodic
    )

    wordsPermFree = np.array(
        [
            [0, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 3],
            [0, 0, 1, 1],
            [0, 0, 1, 2],
            [0, 0, 3, 2],
            [0, 0, 3, 3],
            [0, 1, 0, 1],
            [0, 1, 0, 3],
            [0, 1, 1, 1],
        ]
    )
    assert np.all(
        sdyn.getSymbolicWords(4, permFree=True)[:10] == wordsPermFree
    )

    wordsCyclRed = np.array(
        [
            [0, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 3],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 3, 0],
            [0, 0, 3, 3],
            [0, 1, 0, 0],
            [0, 1, 0, 1],
            [0, 1, 0, 3],
        ]
    )
    assert np.all(sdyn.getSymbolicWords(4, cyclRed=True)[:10] == wordsCyclRed)


def testSymbolicDynamicsWordGen(adjSchottky: tBoolMat) -> None:
    """
    Test functionality of the Word Generator of the SymbolicDynamics class
    on 4x4 Schottky matrix.
    """
    sdyn = SymbolicDynamics(adjSchottky)

    allWords = [
        np.array([[0], [1], [2], [3]]),
        np.array(
            [
                [0, 0],
                [0, 1],
                [0, 3],
                [1, 0],
                [1, 1],
                [1, 2],
                [2, 1],
                [2, 2],
                [2, 3],
                [3, 0],
            ]
        ),
        np.array(
            [
                [0, 0, 0],
                [0, 0, 1],
                [0, 0, 3],
                [0, 1, 0],
                [0, 1, 1],
                [0, 1, 2],
                [0, 3, 0],
                [0, 3, 2],
                [0, 3, 3],
                [1, 0, 0],
            ]
        ),
        np.array(
            [
                [0, 0, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 0, 3],
                [0, 0, 1, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 2],
                [0, 0, 3, 0],
                [0, 0, 3, 2],
                [0, 0, 3, 3],
                [0, 1, 0, 0],
            ]
        ),
    ]
    allWordsGen4 = sdyn.wordGenerator(maxWordLength=4)
    for i, (words, _) in enumerate(allWordsGen4):
        numWords = min(words.shape[0], 10)
        assert np.all(allWords[i] == words[:numWords])

    allWordsGen12 = sdyn.wordGenerator(maxWordLength=12)
    for i, (words, _) in enumerate(allWordsGen12):
        assert words.shape[0] == 4 * 3**i

    allWordsPermFreeCyclRed = [
        np.array([[0], [1], [2], [3]]),
        np.array(
            [[0, 0], [0, 1], [0, 3], [1, 1], [1, 2], [2, 2], [2, 3], [3, 3]]
        ),
        np.array(
            [
                [0, 0, 0],
                [0, 0, 1],
                [0, 0, 3],
                [0, 1, 1],
                [0, 3, 3],
                [1, 1, 1],
                [1, 1, 2],
                [1, 2, 2],
                [2, 2, 2],
                [2, 2, 3],
            ]
        ),
        np.array(
            [
                [0, 0, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 0, 3],
                [0, 0, 1, 1],
                [0, 0, 3, 3],
                [0, 1, 0, 1],
                [0, 1, 0, 3],
                [0, 1, 1, 1],
                [0, 1, 2, 1],
                [0, 1, 2, 3],
            ]
        ),
    ]
    allWordsPermFreeCyclRedGen = sdyn.wordGenerator(
        maxWordLength=4, permFree=True, cyclRed=True
    )
    for i, (words, _) in enumerate(allWordsPermFreeCyclRedGen):
        numWords = min(words.shape[0], 10)
        assert np.all(allWordsPermFreeCyclRed[i] == words[:numWords])
