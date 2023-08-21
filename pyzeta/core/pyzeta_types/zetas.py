"""
Module providing named constants that identify types of implementations of the
abstract `AbstractZeta` base class.

Authors:\n
- Philipp Schuette\n
"""

from enum import Enum


class ZetaType(Enum):
    "Enumeration identifying implementations of zeta functions."
    SELBERG = "SelbergZeta"
    REDUCED_SELBERG = "ReducedSelbergZeta"


class WeightedZetaType(Enum):
    "Enumeration identifying implementations of weighted zeta functions."
    WEIGHTED = "WeightedZeta"
    REDUCED_WEIGHTED = "ReducedWeightedZeta"
