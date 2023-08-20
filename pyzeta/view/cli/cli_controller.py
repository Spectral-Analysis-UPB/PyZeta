"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from os.path import abspath
from typing import Optional

from pyzeta.framework.plugins.installation_helper import InstallationHelper
from pyzeta.framework.plugins.plugin_loader import PluginLoader
from pyzeta.framework.pyzeta_logging.log_levels import LogLevel
from pyzeta.framework.settings.settings_service import SettingsService
from pyzeta.view.cli.controller_facade import CLIControllerFacade
from pyzeta.view.cli.install_test_facade import InstallTestingHandlerFacade
from pyzeta.view.cli.parse_results import (
    InstallTestingParseResults,
    PluginParseResults,
    SettingsParseResults,
)


class CLIController(CLIControllerFacade):
    """
    Controller class handling the business logic of the `PyZeta` command line
    interface.
    """

    def __init__(
        self,
        testingHandler: InstallTestingHandlerFacade,
        settings: SettingsService,
    ) -> None:
        """
        Initialize a new command line interface controller instance.
        """
        self.settingsService = settings
        self.testingHandler = testingHandler

    # docstr-coverage:inherited
    def handleViewSubcommand(self, args: SettingsParseResults) -> None:
        if args.doPrint:
            print(self.settingsService)

    # docstr-coverage:inherited
    def handleChangeSubcommand(self, args: SettingsParseResults) -> None:
        settingsService = self.settingsService
        if args.logLevel:
            self.changeLogLevelSetting(args.logLevel, settingsService)
        if args.verbose:
            self.changeVerbositySetting(args.verbose, settingsService)

    # docstr-coverage:inherited
    def handlePluginSubcommand(self, args: PluginParseResults) -> None:
        if args.listPlugins:
            print("currently installed Plugins:")
            print("----------------------------")
            for plugin in PluginLoader.loadPlugins():
                print(plugin)

        if args.listModules:
            print("installation directory contents:")
            print("--------------------------------")
            for module in PluginLoader.discoverModules():
                print(module)

        if args.install:
            print(f"installing plugin {args.install}...")
            if InstallationHelper.installPlugin(abspath(args.install)):
                print("[success] plugin was installed!")
            else:
                print("[error] the requested plugin does not exist - abort!")
                raise SystemExit(2)

        if args.uninstall:
            print(f"uninstalling plugin {args.uninstall}...")
            if InstallationHelper.uninstallPlugin(args.uninstall):
                print("[success] plugin was uninstalled!")
            else:
                print("[error] the requested plugin does not exist - abort!")
                raise SystemExit(2)

    # docstr-coverage:inherited
    def handleTestingOption(self, args: InstallTestingParseResults) -> bool:
        if args.doTest:
            # slow tests are excluded on purpose
            modules = [
                # "dynamics/function_systems/",
                "dynamics/symbolic_dynamics/",
                "framework/feature_toggle",
                "framework/ioc",
                # "zetas",
            ]
            for module in modules:
                self.testingHandler.testModule(module=module)
            return True
        return False

    @staticmethod
    def changeLogLevelSetting(logLevel: str, service: SettingsService) -> None:
        """
        Try to change the logLevel setting in `service` to `logLevel`.
        If the logLevel is invalid, `SystemExit(2)` is raised.

        :param logLevel: New log level (case-insensitive)
        :param service: Settings service to update.
        :raises SystemExit: Raised when the log level is invalid.
        """
        oldLevel = service.logLevel
        newLevel: Optional[LogLevel] = None
        for level in LogLevel:
            if level.name == logLevel.upper():
                newLevel = level
                break
        if newLevel is None:
            raise SystemExit(2)
        if newLevel != oldLevel:
            service.logLevel = newLevel
            print(
                "changed default log level:   "
                + oldLevel.name
                + " --> "
                + newLevel.name
            )

    @staticmethod
    def changeVerbositySetting(verbose: str, service: SettingsService) -> None:
        """
        Try to update the verbosity setting of `service`. If `verbose` is not
        "true" or "false", `SystemExit(2)` is raised.

        :param verbose: New verbosity setting
        :param service: Setting service to update
        """
        oldVerbosity = service.verbose
        newVerbosity: Optional[bool] = None
        for verbosity in ["true", "false"]:
            if verbose.lower() == verbosity:
                newVerbosity = verbosity == "true"
                break
        if newVerbosity is None:
            raise SystemExit(2)
        if newVerbosity != oldVerbosity:
            service.verbose = newVerbosity
            print(
                "changed default verbosity:   "
                + str(oldVerbosity)
                + " --> "
                + str(newVerbosity)
            )
