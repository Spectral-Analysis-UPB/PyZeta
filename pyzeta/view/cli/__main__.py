"""
This module provides the main CLI entry point of the PyZeta project through the
function `mainPyZeta`.At the moment it provides facilities to query the
currently installed PyZeta version, view and manipulate settings, (un-)install
plugins, and invoke unit tests on the local installation.

Authors:\n
- Philipp Schuette\n
"""

from sys import argv

from pyzeta.framework.initialization.init_modes import InitModes
from pyzeta.framework.initialization.initialization_handler import (
    PyZetaInitializationHandler,
)
from pyzeta.framework.ioc.container_provider import ContainerProvider
from pyzeta.view.cli.controller_facade import CLIControllerFacade
from pyzeta.view.cli.parser_facade import PyZetaParserInterface

PyZetaInitializationHandler.initPyZetaServices(InitModes.CLI)


class PyZetaEntry:
    "Static entry point of the PyZeta command line interface."

    @staticmethod
    def mainPyZeta() -> None:
        """
        Main entry point for the CLI of the PyZeta project.
        """
        container = ContainerProvider.getContainer()
        parser = container.tryResolve(PyZetaParserInterface)
        settingsArgs, pluginArgs, testingArgs = parser.parseArgs()

        # check if any arguments were provided and respond with usage hint
        if len(argv) < 2:
            print("this is the CLI of the PyZeta package. use '-h' for help.")

        controller = container.tryResolve(CLIControllerFacade)
        controller.handleViewSubcommand(settingsArgs)
        controller.handleChangeSubcommand(settingsArgs)
        controller.handlePluginSubcommand(pluginArgs)
        optionSelected = controller.handleTestingOption(testingArgs)

        # a valid subcommand was selected but with no meaningful options
        if len(argv) == 2 and not optionSelected:
            print("use '-h' with your subcommand for help.")
