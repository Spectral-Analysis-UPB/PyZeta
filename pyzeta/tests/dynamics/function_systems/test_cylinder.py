"""
Elementary unit tests for the class implementation of hyperbolic cylinders.

Authors:\n
- Philipp Schuette\n
- Sebastian Albrecht\n
"""

import numpy as np
import pytest as pt

from pyzeta.core.dynamics.function_systems.implementations import (
    FlowAdaptedCylinder,
    HyperbolicCylinder,
)
from pyzeta.framework.initialization.init_modes import InitModes
from pyzeta.framework.initialization.initialization_handler import (
    PyZetaInitializationHandler,
)

# initialize SettingsService
PyZetaInitializationHandler.initPyZetaServices(mode=InitModes.TEST)


def testCylinder() -> None:
    "Test correct calculation of lengths for the hyperbolic cylinder."
    for width in [1.0, 2.0, 5.0, 10.0, 20.0]:
        for maxLetters in [20, 30]:
            cylinder = HyperbolicCylinder(funnelWidth=width)
            allZeros = np.zeros((maxLetters), dtype=np.uint8)
            allOnes = np.ones((maxLetters), dtype=np.uint8)
            words = np.array([allZeros, allOnes])

            for i in range(1, maxLetters + 1):
                stabilities = cylinder.getStabilities(words[:, :i])
                lengths = -np.log(stabilities)
                assert np.allclose(lengths, np.array([i * width, i * width]))


@pt.mark.parametrize("rotate", [True, False])
def testFlowAdaptedCylinder(rotate: bool) -> None:
    "Test correct calculation of lengths for the flow adapted cylinder."
    for width in [1.0, 2.0, 5.0, 10.0, 20.0]:
        for maxPairs in [10, 20]:
            cylinder = FlowAdaptedCylinder(funnelWidth=width, rotate=rotate)
            oneFour = np.array([0, 3] * maxPairs, dtype=np.uint8)
            twoThree = np.array([1, 2] * maxPairs, dtype=np.uint8)
            fourOne = np.array([3, 0] * maxPairs, dtype=np.uint8)
            threeTwo = np.array([2, 1] * maxPairs, dtype=np.uint8)
            words = np.array([oneFour, twoThree, fourOne, threeTwo])

            for i in range(2, 2 * maxPairs + 1, 2):
                stabilities = cylinder.getStabilities(words[:, :i])
                lengths = -np.log(stabilities)
                assert np.allclose(lengths, np.array([(i // 2) * width] * 4))
