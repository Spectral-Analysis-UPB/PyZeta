"""
Module initialization_handler.py from the package PyZeta.
This module handles initialization for the default PyZeta services.

Authors:\n
- Philipp Schuette\n
"""

from typing import Optional

from pyzeta.core.dynamics.function_systems.function_system import (
    FunctionSystem,
)
from pyzeta.core.dynamics.function_systems.integral_provider import (
    IntegralProvider,
)
from pyzeta.core.dynamics.function_systems.map_system import (
    HyperbolicMapSystem,
)
from pyzeta.core.dynamics.symbolic_dynamics.abstract_dynamics import (
    AbstractSymbolicDynamics,
)
from pyzeta.core.factories.function_systems import FunctionSystemFactory
from pyzeta.core.factories.integrals import OrbitIntegralFactory
from pyzeta.core.factories.map_systems import MapSystemFactory
from pyzeta.core.factories.symbolics import SymbolicDynamicsFactory
from pyzeta.framework.initialization.init_modes import InitModes
from pyzeta.framework.ioc.container import Container
from pyzeta.framework.ioc.container_provider import ContainerProvider
from pyzeta.framework.pyzeta_logging.log_manager import LogManager
from pyzeta.framework.pyzeta_logging.logger_facade import PyZetaLogger
from pyzeta.framework.settings.settings_factory import SettingsServiceFactory
from pyzeta.framework.settings.settings_service import SettingsService


class PyZetaInitializationHandler:
    "Static initialization handler for PyZeta services."

    # the module level logger
    _logger: Optional[PyZetaLogger] = None

    # protect from multiple initializations
    initialized = False

    @staticmethod
    def initPyZetaServices(mode: InitModes = InitModes.SCRIPT) -> None:
        """
        Build a container that supports all core functionality and register it
        with the `ContainerProvider`.
        """
        # check for re-initialization
        if PyZetaInitializationHandler.initialized:
            if PyZetaInitializationHandler._logger is None:
                return
            PyZetaInitializationHandler._logger.warning(
                "re-initialization attempt with mode %s detected - skipped!",
                mode.name if mode.name else "[unknown]",
            )
            return

        container = Container()

        # register anything mode-independent first (i.e. settings for logging)
        if mode in (
            InitModes.CLI | InitModes.SCRIPT | InitModes.GUI | InitModes.TEST
        ):
            PyZetaInitializationHandler.initModeIndependentServices(container)

        # at this point a SettingsService must have been registered!
        PyZetaInitializationHandler._logger = LogManager.initLogger(
            __name__.rsplit(".", maxsplit=1)[-1],
            container.tryResolve(SettingsService).logLevel,
        )

        if mode == InitModes.CLI:
            PyZetaInitializationHandler.initCLIServices(container)
        elif mode == InitModes.SCRIPT:
            PyZetaInitializationHandler.initSCRIPTServices(container)
        elif mode == InitModes.GUI:
            PyZetaInitializationHandler.initGUIServices(container)
        elif mode == InitModes.TEST:
            PyZetaInitializationHandler.initTESTServices(container)

        # initialization complete!
        ContainerProvider.setContainer(container)
        PyZetaInitializationHandler.initialized = True
        PyZetaInitializationHandler._logger.info("initialization complete!")

    @staticmethod
    def initModeIndependentServices(container: Container) -> None:
        """
        TODO.

        :param container: container to register services with
        """
        container.registerAsTransient(
            SettingsService, SettingsServiceFactory.getConcreteSettings
        )

    @staticmethod
    def initCLIServices(container: Container) -> None:
        """
        TODO.

        :param container: container to register cli services with
        """

    @staticmethod
    def initSCRIPTServices(container: Container) -> None:
        """
        TODO.

        :param container: container to register scripting services with
        """
        container.registerAsTransient(
            AbstractSymbolicDynamics,
            SymbolicDynamicsFactory.getConcreteSymbolics,
        )
        container.registerAsTransient(
            FunctionSystem, FunctionSystemFactory.getConcreteSystem
        )
        container.registerAsTransient(
            HyperbolicMapSystem, MapSystemFactory.getConcreteMapSystem
        )
        container.registerAsTransient(
            IntegralProvider, OrbitIntegralFactory.getConcreteIntegral
        )

    @staticmethod
    def initTESTServices(container: Container) -> None:
        """
        TODO.

        :param container: container to register testing services with
        """
        container.registerAsTransient(
            AbstractSymbolicDynamics,
            SymbolicDynamicsFactory.getConcreteSymbolics,
        )
        container.registerAsTransient(
            FunctionSystem, FunctionSystemFactory.getConcreteSystem
        )

    @staticmethod
    def initGUIServices(container: Container) -> None:
        """
        TODO.

        :param container: container to register gui services with
        """
