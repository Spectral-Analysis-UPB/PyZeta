"""
Module containing an abstract base for concrete `PyZeta` experiments. Such
experiments consist of stages which are executed in a given order and may in
addition be associated with further (meta)data.

Authors:\n
- Philipp Schuette\n
"""

from abc import ABC, abstractmethod
from typing import Iterable

from pyzeta.experiments.stage import Stage


class Experiment(ABC):
    "Abstract base for `PyZeta` experiments."

    __slots__ = ("_stages",)

    def __init__(self, stages: Iterable[Stage]) -> None:
        "Initialize a new experiment from a given collection of stages."
        self._stages = stages

    @abstractmethod
    def executeStages(self) -> None:
        "Execute the stages making up the experiment."
        for stage in self._stages:
            stage.execute()
