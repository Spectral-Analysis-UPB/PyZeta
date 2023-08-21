"""
Module containing a symmetrized version of the `IntegralProvider` abstract
base class. Implementations of this variant must be used with symmetry reduced
dynamical determinants/weighted zetas.

Authors:\n
- Philipp Schuette\n
"""

from abc import ABC


# TODO: maybe symmetrized variants can implement IntegralProvider as well?
class SymmetrizedIntegrals(ABC):
    "Abstract base for orbit integrals w.r.t. symmetrized weights."
