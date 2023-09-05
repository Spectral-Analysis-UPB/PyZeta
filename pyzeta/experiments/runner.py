"""
Module containing a rudimentary base for runners that control the execution of
`PyZeta` experiments. For practical usage this runner should be subclassed to
add control features like logging, conditional execution, post-processing, etc.

Authors:\n
- Philipp Schuette\n
"""

from typing import Iterable

from pyzeta.experiments.experiment import Experiment


class ExperimentRunner:
    "Abstract base for `PyZeta` experiment runners."

    def run(self, experiments: Iterable[Experiment]) -> None:
        "Run a given collection of experiments."
        for experiment in experiments:
            experiment.executeStages()
