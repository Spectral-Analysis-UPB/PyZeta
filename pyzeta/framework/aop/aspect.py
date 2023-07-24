"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from inspect import getmembers, ismethod
from typing import Dict, TypeVar

from pyzeta.framework.aop.advice import Advice
from pyzeta.framework.aop.point_cut import PointCut
from pyzeta.framework.pyzeta_logging.loggable import Loggable

T = TypeVar("T")


class Aspect(Loggable):
    "Implementation of the central abstraction of aspect oriented programming."

    __slots__ = ("rules",)

    def __init__(self) -> None:
        """
        Initialize a new aspect from a given set of rules, i.e. pairs of
        point cuts and corresponding advice.
        """
        rules: Dict[PointCut, Advice] = {}

    def __call__(self, instance: T) -> T:
        """
        Apply a given aspect to some object instance.

        :param instance: object to modify with the aspect
        """
        for name, value in getmembers(instance, ismethod):
            self.logger.debug(
                "found method %s with value %s", name, str(value)
            )
        return instance

    def registerRule(self) -> None:
        """
        Register a new rule consisting of a point cut together with an advice.
        """
