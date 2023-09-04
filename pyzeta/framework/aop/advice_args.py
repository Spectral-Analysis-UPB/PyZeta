"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from typing import TypedDict

from typing_extensions import TypeAlias


class ProfilingAdviceArgs(TypedDict, total=True):
    "Initialization arguments for profiling advice."
    statsFile: str


tAdviceInitArgs: TypeAlias = ProfilingAdviceArgs
