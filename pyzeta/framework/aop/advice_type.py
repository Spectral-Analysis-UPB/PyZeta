"""
Module `pyzeta.framework.aop.advice_type` defining named constants which map to
pre-defined advice implementations.

Authors:\n
- Philipp Schuette\n
"""

from enum import Enum


class AdviceType(Enum):
    "Named constants enumerating the pre-defined advice implementations."
    PROFILING = "ProfilingAdvice"
