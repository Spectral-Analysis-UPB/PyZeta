"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from typing import TypedDict, Union

from typing_extensions import TypeAlias


class HyperbolicCylinderArgs(TypedDict, total=True):
    "Init arguments for a hyperbolic cylinder."
    funnelWidth: float
    rotate: bool


class CylinderMapArgs(TypedDict, total=True):
    "Init arguments for a (hyperbolic) cylinder based map system."
    funnelWidth: float
    rotate: bool


class GeometricFunnelTorusArgs(TypedDict, total=True):
    "Init arguments for a geometrically defined funneled torus."
    outerLen: float
    funnelWidth: float
    twist: float


class FunnelTorusArgs(TypedDict, total=True):
    "Init arguments for a (non-geometric) funneled torus."
    outerLen: float
    innerLen: float
    angle: float


tFunctionSystemInitArgs: TypeAlias = Union[
    HyperbolicCylinderArgs, GeometricFunnelTorusArgs, FunnelTorusArgs
]

tMapSystemInitArgs: TypeAlias = Union[
    CylinderMapArgs, GeometricFunnelTorusArgs, FunnelTorusArgs
]
