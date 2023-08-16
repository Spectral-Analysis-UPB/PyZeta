"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from typing import TypedDict, Union

from numpy import float64
from numpy.typing import NDArray
from typing_extensions import TypeAlias

from pyzeta.core.pyzeta_types.general import tVec


class PoincareIntegralsArgs(TypedDict, total=True):
    "Init arguments for integrals over Poincare sections."
    supportMinus: NDArray[float64]
    supportPlus: NDArray[float64]
    sigMinus: float
    sigPlus: float


class FundamentalDomainIntegralsArgs(TypedDict, total=True):
    "Init arguments for integrals over fundamental domains."
    supportReal: NDArray[float64]
    supportImag: NDArray[float64]
    sigma: float


class ConstantIntegralsArgs(TypedDict, total=True):
    "Init arguments for constant orbit integrals are empty."


tOrbitIntegralInitArgs: TypeAlias = Union[
    PoincareIntegralsArgs,
    FundamentalDomainIntegralsArgs,
    ConstantIntegralsArgs,
]
