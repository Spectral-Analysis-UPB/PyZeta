"""
Module providing named constants that identify types of implementations of the
`AbstractSymbolicDynamics` base class.

Authors:\n
- Philipp Schuette\n
"""

from enum import Enum


class SymbolicDynamicsType(Enum):
    "Enumeration identifying implementations of symbolic dynamics."
    NON_REDUCED = "SymbolicDynamics"
    REDUCED = "ReducedSymbolicDynamics"
