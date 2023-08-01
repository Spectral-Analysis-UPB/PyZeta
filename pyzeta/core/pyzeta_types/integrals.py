"""
Module integrals.py from the package PyZeta.
TODO.

Authors:\n
- Philipp Schuette\n
"""

from enum import Enum


class OrbitIntegralType(Enum):
    "Named constants identifying the available orbit integral providers."
    POINCARE = "PoincareSectionIntegrals"
    FUNDAMENTAL_DOMAIN = "FundamentalDomainIntegrals"
