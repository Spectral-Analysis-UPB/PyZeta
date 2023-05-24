"""
Module containing resources such as test cases for the testing of symbolic
dynamics implementations.

Authors:\n
- Philipp Schuette\n
"""

from dataclasses import dataclass
from typing import Final, Tuple, TypedDict

from numpy import array, empty, uint8

from pyzeta.core.pyzeta_types.general import tWordVec


class SymbolicsTestConfigurationRqrd(TypedDict, total=True):
    "Required attributes for symbolic dynamics testing configurations."
    wordLength: int


class SymbolicsTestConfiguration(SymbolicsTestConfigurationRqrd, total=False):
    "Optional attributes for symbolic dynamics testing configurations."
    givenWords: tWordVec
    prime: bool
    permFree: bool
    cyclRed: bool
    periodic: bool


@dataclass
class SymbolicsTestCase:
    "Class representation of a symbolic dynamics test setup."
    configuration: SymbolicsTestConfiguration
    expectedWords: tWordVec


adjUnitCaseAll = SymbolicsTestCase(
    configuration={"wordLength": 4},
    expectedWords=array(
        [[0, 0, 0, 0], [1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3]]
    ),
)

adjUnitCaseAllGiven = SymbolicsTestCase(
    configuration={"wordLength": 4, "givenWords": array([[0], [1], [2], [3]])},
    expectedWords=array(
        [[0, 0, 0, 0], [1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3]]
    ),
)

adjUnitCasePrime = SymbolicsTestCase(
    configuration={
        "wordLength": 4,
        "prime": True,
        "givenWords": array([[0], [1], [2], [3]]),
    },
    expectedWords=empty(shape=(0, 4), dtype=uint8),
)

adjUnitCasePeriodic = SymbolicsTestCase(
    configuration={"wordLength": 4, "periodic": True},
    expectedWords=array(
        [[0, 0, 0, 0], [1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3]]
    ),
)

adjUnitCasePrimePeriodic = SymbolicsTestCase(
    configuration={"wordLength": 4, "periodic": True, "prime": True},
    expectedWords=empty(shape=(0, 4), dtype=uint8),
)

adjUnitCasePermFree = SymbolicsTestCase(
    configuration={"wordLength": 4, "permFree": True},
    expectedWords=array(
        [[0, 0, 0, 0], [1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3]]
    ),
)

adjUnitCaseCyclRed = SymbolicsTestCase(
    configuration={"wordLength": 4, "cyclRed": True},
    expectedWords=array(
        [[0, 0, 0, 0], [1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3]]
    ),
)

# define tuples of test cases for easy import in test modules
ADJ_UNIT_TEST_CASES: Final[Tuple[SymbolicsTestCase, ...]] = (
    adjUnitCaseAll,
    adjUnitCaseAllGiven,
    adjUnitCaseCyclRed,
    adjUnitCasePeriodic,
    adjUnitCasePermFree,
    adjUnitCasePrime,
    adjUnitCasePrimePeriodic,
)

# TODO: refactor missing test cases as shown above!
ADJ_INVERSE_UNIT_TEST_CASES: Final[Tuple[SymbolicsTestCase, ...]] = ()

ADJ_FULL_TEST_CASES: Final[Tuple[SymbolicsTestCase, ...]] = ()

ADJ_SPARSE_TEST_CASES: Final[Tuple[SymbolicsTestCase, ...]] = ()

ADJ_BLOCK_TEST_CASES: Final[Tuple[SymbolicsTestCase, ...]] = ()

ADJ_SCHOTTKY_TEST_CASES: Final[Tuple[SymbolicsTestCase, ...]] = ()
