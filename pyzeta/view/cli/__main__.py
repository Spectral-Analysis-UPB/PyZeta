"""
This module provides the main CLI entry point of the PyZeta project through the
function `mainPyZeta`.At the moment it provides facilities to query the
currently installed PyZEAL version, view and manipulate settings, (un-)install
plugins, and invoke unit tests on the local installation.

Authors:\n
- Philipp Schuette\n
"""

from sys import argv

from pyzeal.cli.controller_facade import CLIControllerFacade
from pyzeal.cli.parser_facade import PyZEALParserInterface
from pyzeta.framework.pyzeta_types.init_modes import InitModes
from pyzeal.utils.service_locator import ServiceLocator

from pyzeta.framework.initialization.initialization_handler import (
    PyZetaInitializationHandler,
)


class PyZetaEntry:
    "Static entry point of the PyZeta command line interface."

    @staticmethod
    def mainPyZeta() -> None:
        """
        Main entry point for the CLI of the PyZeta project.
        """
        PyZetaInitializationHandler.initPyZetaServices(InitModes.CLI)

        parser = ServiceLocator.tryResolve(PyZEALParserInterface)
        settingsArgs, pluginArgs, testingArgs = parser.parseArgs()

        # check if any arguments were provided and respond with usage hint
        if len(argv) < 2:
            print("this is the CLI of the PyZEAL package. use '-h' for help.")

        controller = ServiceLocator.tryResolve(CLIControllerFacade)
        controller.handleViewSubcommand(settingsArgs)
        controller.handleChangeSubcommand(settingsArgs)
        controller.handlePluginSubcommand(pluginArgs)
        optionSelected = controller.handleTestingOption(testingArgs)

        # a valid subcommand was selected but with no meaningful options
        if len(argv) == 2 and not optionSelected:
            print("use '-h' with your subcommand for help.")
