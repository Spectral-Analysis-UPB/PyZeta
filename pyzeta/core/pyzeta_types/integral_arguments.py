"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from typing import TypedDict, Union

from typing_extensions import TypeAlias

from pyzeta.core.pyzeta_types.general import tVec


class PoincareIntegralsArgs(TypedDict, total=True):
    "Init arguments for integrals over Poincare sections."
    supportMinus: tVec
    supportPlus: tVec
    sigMinus: float
    sigPlus: float


class FundamentalDomainIntegralsArgs(TypedDict, total=True):
    "Init arguments for integrals over fundamental domains."
    supportReal: tVec
    supportImag: tVec
    sigma: float


tOrbitIntegralInitArgs: TypeAlias = Union[
    PoincareIntegralsArgs, FundamentalDomainIntegralsArgs
]
