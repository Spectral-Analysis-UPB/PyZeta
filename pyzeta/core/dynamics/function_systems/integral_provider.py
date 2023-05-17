"""
- the interesting potentials for (weighted) zeta functions should know their
  associated surface and use the exposed methods to calculate stuff

Authors:\n
- Philipp Schuette\n
"""

from abc import ABC, abstractmethod

from pyzeta.core.pyzeta_types.general import tIntegralVec, tWordVec


class IntegralProvider(ABC):
    "Abstract base realizing the potentials used in weighted zeta functions."

    @abstractmethod
    def getOrbitIntegrals(self, words: tWordVec) -> tIntegralVec:
        "TODO."
