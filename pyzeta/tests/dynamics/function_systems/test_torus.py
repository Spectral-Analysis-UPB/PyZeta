"""
Elementary unit tests for the class implementations of the ordinary and the
geometric funneled torus.

Authors:\n
- Philipp Schuette\n
"""

import numpy as np
import pytest as pt

from pyzeta.core.dynamics.function_systems.implementations import (
    FunnelTorus,
    GeometricFunnelTorus,
)
from pyzeta.core.dynamics.symbolic_dynamics.abstract_dynamics import (
    AbstractSymbolicDynamics,
)
from pyzeta.core.pyzeta_types.symbolics import SymbolicDynamicsType
from pyzeta.framework.initialization.init_modes import InitModes
from pyzeta.framework.initialization.initialization_handler import (
    PyZetaInitializationHandler,
)
from pyzeta.framework.ioc.container_provider import ContainerProvider

# initialize SettingsService
PyZetaInitializationHandler.initPyZetaServices(mode=InitModes.TEST)
container = ContainerProvider.getContainer()


def testFunneledTorus() -> None:
    "Test consistency of calculation of lengths for ordinary funneled tori."
    for params in [
        {"outerLen": 2.0, "innerLen": 2.0, "angle": np.pi / 2.0},
        {"outerLen": 3.0, "innerLen": 4.0, "angle": np.pi / 2.0},
        {"outerLen": 4.0, "innerLen": 4.0, "angle": np.pi / 2.1},
    ]:
        cylinder = FunnelTorus(**params, rotate=False)
        rotatedCylinder = FunnelTorus(**params, rotate=True)
        for words, _ in container.tryResolve(
            AbstractSymbolicDynamics,
            symbolicsType=SymbolicDynamicsType.NON_REDUCED,
            adjacencyMatrix=cylinder.adjacencyMatrix,
        ).wordGenerator(7, cyclRed=True):
            stabilities = cylinder.getStabilities(words)
            stabilitiesRotated = rotatedCylinder.getStabilities(words)
            lengths = -np.log(stabilities)
            lengthsRotated = -np.log(stabilitiesRotated)
            assert np.allclose(lengths, lengthsRotated, atol=1e-6)


def testGeometricFunneledTorus() -> None:
    "Test consistency of calculation of lengths for geometric funneled tori."
    for params in [
        {"outerLen": 2.0, "funnelWidth": 2.0, "twist": 0.0},
        {"outerLen": 3.0, "funnelWidth": 4.0, "twist": 1.0},
        {"outerLen": 5.0, "funnelWidth": 5.0, "twist": 5.0},
    ]:
        cylinder = GeometricFunnelTorus(**params, rotate=False)
        rotatedCylinder = GeometricFunnelTorus(**params, rotate=True)
        for words, _ in container.tryResolve(
            AbstractSymbolicDynamics,
            symbolicsType=SymbolicDynamicsType.NON_REDUCED,
            adjacencyMatrix=cylinder.adjacencyMatrix,
        ).wordGenerator(7, cyclRed=True):
            stabilities = cylinder.getStabilities(words)
            stabilitiesRotated = rotatedCylinder.getStabilities(words)
            lengths = -np.log(stabilities)
            lengthsRotated = -np.log(stabilitiesRotated)
            assert np.allclose(lengths, lengthsRotated, atol=1e-6)
