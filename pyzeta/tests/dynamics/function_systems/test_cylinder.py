"""
Elementary unit tests for the class implementation of hyperbolic cylinders.

Authors:\n
- Philipp Schuette\n
- Sebastian Albrecht\n
"""

import numpy as np

from pyzeta.core.dynamics.function_systems import HyperbolicCylinder
from pyzeta.framework.initialization.initialization_handler import (
    PyZetaInitializationHandler,
)

PyZetaInitializationHandler.initPyZetaServices()


def test_cylinder() -> None:
    "Test correct calculation of lengths for the hyperbolic cylinder."
    for width in [1.0, 2.0, 5.0, 10.0, 20.0]:
        for maxLetters in [20, 30]:
            cylinder = HyperbolicCylinder(funnelWidth=width)
            allZeros = np.zeros((maxLetters), dtype=np.int16)
            allOnes = np.ones((maxLetters), dtype=np.int16)
            words = np.array([allZeros, allOnes])

            for i in range(1, maxLetters + 1):
                stabilities = cylinder.getStabilities(words[:, :i])
                lengths = -np.log(stabilities)
                assert np.allclose(lengths, np.array([i * width, i * width]))
