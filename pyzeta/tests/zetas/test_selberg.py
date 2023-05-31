"""
Module containing simple unit tests for Selberg zeta functions.

Authors:\n
- Philipp Schuette\n
"""

import numpy as np
from pyzeal.pyzeal_types.algorithm_types import AlgorithmTypes
from pyzeal.pyzeal_types.estimator_types import EstimatorTypes
from pyzeal.rootfinders.rootfinder import RootFinder

from pyzeta.core.pyzeta_types.function_systems import FunctionSystemType
from pyzeta.core.pyzeta_types.system_arguments import HyperbolicCylinderArgs
from pyzeta.core.zetas.selberg_zeta import SelbergZeta
from pyzeta.framework.initialization.init_modes import InitModes
from pyzeta.framework.initialization.initialization_handler import (
    PyZetaInitializationHandler,
)

# initialize SettingsService
PyZetaInitializationHandler.initPyZetaServices(mode=InitModes.TEST)


def testCylinderResonances() -> None:
    "Test Selberg zeta by calculating resonances on the hyperbolic cylinder."
    initArgs: HyperbolicCylinderArgs = {"funnelWidth": 5.0}
    zeta = SelbergZeta(
        functionSystem=FunctionSystemType.HYPERBOLIC_CYLINDER,
        systemInitArgs=initArgs,
    )

    nMax = 6
    finder = RootFinder(
        f=lambda s: zeta(s, nMax=nMax),
        algorithmType=AlgorithmTypes.SIMPLE_ARGUMENT,
        estimatorType=EstimatorTypes.SUMMATION_ESTIMATOR,
    )

    width = initArgs["funnelWidth"]
    expectedResonances = np.array(
        [-2 * np.pi * 1j / width, 0, 2 * np.pi * 1j / width]
    )
    # check if zeta function becomes small on theoretically expected zeros
    zetaEval = zeta(expectedResonances, nMax=2 * nMax)
    assert np.allclose(zetaEval, np.zeros((3,)), 1e-8)

    # start searching for roots of the zeta function
    finder.calculateRoots(
        reRan=(-0.1, 0.1), imRan=(-1.5, 1.5), precision=(3, 2)
    )
    actualResonances = np.sort_complex(finder.roots)
    assert np.allclose(expectedResonances, actualResonances, atol=1e-3)

    assert all(order == 2 for order in finder.orders)
