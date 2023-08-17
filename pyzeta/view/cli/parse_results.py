"""
This module contains dataclasses for storing results of command-line parsing.

Authors:\n
- Philipp Schuette\n
"""

from dataclasses import dataclass


@dataclass
class SettingsParseResults:
    """
    Container for parsing results related to settings.
    """

    doPrint: bool
    logLevel: str
    verbose: str


@dataclass
class PluginParseResults:
    """
    Container for parsing results related to plugins.
    """

    listPlugins: bool
    listModules: bool
    install: str
    uninstall: str


@dataclass
class InstallTestingParseResults:
    """
    Container for parsing results related to testing of the installation.
    """

    doTest: bool
