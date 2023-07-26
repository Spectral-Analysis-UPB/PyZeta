"""
Basic implementation of cProfile-based profiler in the aspect oriented
framework in PyZeta.

Authors:\n
- Philipp Schuette\n
"""

from cProfile import Profile
from typing import TypeVar

from typing_extensions import ParamSpec

from pyzeta.framework.aop.advice import Advice

# define type variables for the profiling advice
T = TypeVar("T")
P = ParamSpec("P")


class ProfilingAdvice(Advice[T, P]):
    "Simple custom profiling advice used within a profiling aspect."

    __slots__ = ("_statsFile", "_profile")

    extension: str = ".cprofile"

    def __init__(self, statsFile: str = "stats.temp") -> None:
        """
        Initialize a new piece of profiling advice for usage within an aspect.

        :param statsFile: name of file to write statistics to
        """
        # I have no idea why this raises a typing error on the second arg...?
        super().__init__(
            preFunc=self._start, postFunc=self._stop  # type: ignore
        )
        self._profile = Profile()
        self._statsFile = statsFile

    def _start(self, *_: P.args, **__: P.kwargs) -> None:
        self._profile.enable()

    def _stop(self, result: T, *_: P.args, **__: P.kwargs) -> T:
        self._profile.disable()
        self._profile.dump_stats(self.statsFile + ProfilingAdvice.extension)

        return result

    @property
    def statsFile(self) -> str:
        """
        Return the name of the statistics file (pstats.Stats compatible).

        :return: name of the statistics file
        """
        return self._statsFile
