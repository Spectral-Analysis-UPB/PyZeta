"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from dataclasses import dataclass
from typing import Generic, TypeVar

from typing_extensions import ParamSpec

from pyzeta.framework.aop.advice import Advice
from pyzeta.framework.aop.point_cut import PointCut

T = TypeVar("T")
P = ParamSpec("P")


@dataclass
class Rule(Generic[T, P]):
    "Simple container structure representing pairs of point cuts and advice."

    pointCut: PointCut
    advice: Advice[T, P]
