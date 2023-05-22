"""
TODO.

Authors:\n
- Philipp Schuette
"""

from typing import Dict

from pyzeta.core.pyzeta_types.special import (
    tGroupElement,
    tIrreducibleRepr,
    tLetter,
)

# type aliases related to discrete symmetry groups of function systems
tGroupTable = Dict[tGroupElement, Dict[tGroupElement, tGroupElement]]
tInversionTable = Dict[tGroupElement, tGroupElement]
tOrderTable = Dict[tGroupElement, int]
tCharacterTable = Dict[tIrreducibleRepr, Dict[tGroupElement, complex]]
tDimensionTable = Dict[tIrreducibleRepr, int]
tActionTable = Dict[tGroupElement, Dict[tLetter, tLetter]]
