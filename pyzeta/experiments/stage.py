"""
Module containing an abstract base for a single stage to be executed during an
experiment. Such stages implement the command pattern.

Authors:\n
- Philipp Schuette\n
"""

from abc import ABC, abstractmethod


class Stage(ABC):
    "Abstract class representation of a stage executed during an experiment."

    @abstractmethod
    def execute(self) -> None:
        "Execute the stage as part of a containing experiment."
