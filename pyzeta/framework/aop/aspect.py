"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from inspect import getmembers, isfunction
from typing import Callable, Generic, List, Type, TypeVar, cast

from typing_extensions import ParamSpec

from pyzeta.framework.aop.rule import Rule

T = TypeVar("T")
S = TypeVar("S")
P = ParamSpec("P")


class Aspect(Generic[S, T, P]):
    "Implementation of the central abstraction of aspect oriented programming."

    __slots__ = ("rules",)

    def __init__(self, rules: List[Rule[T, P]]) -> None:
        """
        Initialize a new aspect from a given set of rules, i.e. pairs of
        point cuts and corresponding advice. For consistency reasons rules
        cannot be added or deleted after initialization.

        :param rules: rules contained in the created aspect instance
        """
        self.rules = rules

    def __call__(self, cls: Type[S]) -> None:
        """
        Apply a given aspect to some class.

        :param cls: class to modify with the aspect
        """
        for name, value in getmembers(cls, isfunction):
            currentMethod = cast(Callable[P, T], value)
            for rule in self.rules:
                pointCut, advice = rule.pointCut, rule.advice
                if pointCut.match(name):
                    # any matching method must have signature **P -> T
                    currentMethod = advice(currentMethod)
            setattr(cls, name, currentMethod)
