"""
Module initialization_handler.py from the package PyZeta.
This module handles initialization for the default PyZeta services.

Authors:\n
- Philipp Schuette\n
"""

from typing import Optional

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
        if mode in (InitModes.CLI | InitModes.SCRIPT | InitModes.GUI):
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

    @staticmethod
    def initGUIServices(container: Container) -> None:
        """
        TODO.

        :param container: container to register gui services with
        """
