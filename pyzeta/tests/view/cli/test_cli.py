"""
This module contains tests for the command-line interface, apart from the
parsing.

Authors:\n
- Luca Wasmuth\n
- Philipp Schuette\n
"""

from functools import partial
from typing import Callable, Tuple, TypedDict, Union
from unittest.mock import PropertyMock, create_autospec, patch

import pytest

from pyzeta.framework.ioc.container import Container
from pyzeta.framework.ioc.container_provider import ContainerProvider
from pyzeta.framework.pyzeta_logging.log_levels import LogLevel
from pyzeta.framework.settings.ram_settings.ram_settings_service import (
    RAMSettingsService,
)
from pyzeta.framework.settings.settings_service import SettingsService
from pyzeta.view.cli.__main__ import PyZetaEntry
from pyzeta.view.cli.cli_controller import CLIController
from pyzeta.view.cli.cli_parser import PyZetaParser
from pyzeta.view.cli.controller_facade import CLIControllerFacade
from pyzeta.view.cli.install_test_facade import InstallTestingHandlerFacade
from pyzeta.view.cli.install_test_handler import InstallTestingHandler
from pyzeta.view.cli.parse_results import (
    InstallTestingParseResults,
    PluginParseResults,
    SettingsParseResults,
)
from pyzeta.view.cli.parser_facade import PyZetaParserInterface

container = Container()
container.registerAsTransient(
    PyZetaParserInterface, PyZetaParser
).registerAsTransient(CLIControllerFacade, CLIController).registerAsTransient(
    InstallTestingHandlerFacade, InstallTestingHandler
).registerAsSingleton(
    SettingsService, RAMSettingsService()
)
ContainerProvider.setContainer(container)


class SettingsDict(TypedDict, total=False):
    """
    Container class to ensure correct typing of settings options to be tested.
    """

    logLevel: str
    verbose: str


def mockArgs(
    newSetting: SettingsDict,
) -> Tuple[
    SettingsParseResults, PluginParseResults, InstallTestingParseResults
]:
    """
    Generate `SettingsParseResults` and `PluginParseResults` instances
    containing the settings given by `newSetting`.

    :param newSetting: Dict of settings and values
    :return: ParseResults with appropriate settings
    """
    settingsParseResult = SettingsParseResults(
        doPrint=True,
        logLevel=newSetting.get("logLevel", ""),
        verbose=newSetting.get("verbose", ""),
    )
    pluginParseResult = PluginParseResults(
        listPlugins=False,
        listModules=False,
        install="",
        uninstall="",
    )
    testingParseResult = InstallTestingParseResults(doTest=False)
    return settingsParseResult, pluginParseResult, testingParseResult


tSettingsTypes = Union[bool, LogLevel]

newSettings: Tuple[SettingsDict, ...] = (
    {"verbose": "True"},
    {"logLevel": "INFO"},
)
changeMethods: Tuple[str, ...] = (
    "changeVerbositySetting",
    "changeLogLevelSetting",
)
defaultSettingProperties: Tuple[str, ...] = (
    "verbose",
    "logLevel",
)
beforeValues: Tuple[tSettingsTypes, ...] = (
    False,
    LogLevel.WARNING,
)
afterValues: Tuple[tSettingsTypes, ...] = (
    True,
    LogLevel.INFO,
)


@pytest.mark.parametrize("testSetup", zip(newSettings, changeMethods))
def testChangeCall(testSetup: Tuple[SettingsDict, str]) -> None:
    """
    Test if `change...Setting` gets called correctly.
    """
    newSetting: SettingsDict = testSetup[0]
    changeMethod = (
        "pyzeta.view.cli.cli_controller.CLIController." + testSetup[1]
    )
    with patch(
        "pyzeta.view.cli.cli_parser.PyZetaParser.parseArgs"
    ) as mockParse:
        mockParse.side_effect = partial(mockArgs, newSetting=newSetting)
        with patch(changeMethod) as doNothing:
            entry = PyZetaEntry()
            entry.mainPyZeta()
            doNothing.assert_called_once()


@pytest.mark.parametrize(
    "testSetup",
    zip(newSettings, defaultSettingProperties, beforeValues, afterValues),
)
def testChangeSettingsCall(
    testSetup: Tuple[
        SettingsDict,
        str,
        tSettingsTypes,
        tSettingsTypes,
    ]
) -> None:
    """
    Test if `change...Setting` correctly updates the newSetting.
    """
    newSetting: SettingsDict = testSetup[0]
    defaultSettingProperty = (
        "pyzeta.framework.settings.ram_settings.ram_settings_service."
        "RAMSettingsService." + testSetup[1]
    )
    beforeValue = testSetup[2]
    afterValue = testSetup[3]
    with patch(
        "pyzeta.view.cli.cli_parser.PyZetaParser.parseArgs"
    ) as mockParse:
        mockParse.side_effect = partial(mockArgs, newSetting=newSetting)
        with patch(
            defaultSettingProperty, new_callable=PropertyMock
        ) as mockedProp:
            mockedProp.return_value = beforeValue
            entry = PyZetaEntry()
            entry.mainPyZeta()
            mockedProp.assert_called_with(afterValue)


@pytest.mark.parametrize(
    "changeFunction",
    [
        CLIController.changeLogLevelSetting,
        CLIController.changeVerbositySetting,
    ],
)
def testCLIControllerInvalidName(
    changeFunction: Callable[[str, SettingsService], None]
) -> None:
    """
    Test if CLIController correctly exits when an invalid name is given
    for a newSetting.

    :param changeFunction: Function to test, parametrized by pytest
    """
    mockSettings = create_autospec(
        SettingsService, spec_set=True, instance=True
    )
    with pytest.raises(SystemExit):
        changeFunction("THIS_DOES_NOT_EXIST", mockSettings)
