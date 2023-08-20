"""
Test the JSONHelper for correct exception throwing behavior.

Authors:\n
- Philipp Schuette\n
- Luca Wasmuth\n
"""
from unittest.mock import MagicMock, patch

import pytest

from pyzeta.framework.pyzeta_logging.log_levels import LogLevel
from pyzeta.framework.settings.invalid_setting_exception import (
    InvalidSettingException,
)
from pyzeta.framework.settings.json_settings.json_helper import (
    JSONHelper,
    tCoreSettingsKey,
    tSettingsKey,
)


@patch("pyzeta.framework.settings.json_settings.json_helper.dump")
@patch("builtins.open")
@patch("pyzeta.framework.settings.json_settings.json_helper.load")
@pytest.mark.parametrize(
    "settingName",
    ["INVALID_KEY"],
)
def testInvalidCoreSettings(
    loadMock: MagicMock,
    openMock: MagicMock,
    dumpMock: MagicMock,
    settingName: tCoreSettingsKey,
) -> None:
    """
    Test exception raising when an invalid core setting is given.

    :param settingName: Setting name to test, parametrized by pytest
    """
    with pytest.raises(InvalidSettingException):
        # at least one of these should fail, no matter which
        # settingName is used
        JSONHelper.createOrUpdateCoreSetting(
            "DOES_NOT_EXIST.json",
            settingName,
            LogLevel.WARNING,
        )
    dumpMock.assert_not_called()
    openMock.assert_called()
    loadMock.assert_called()


@patch("pyzeta.framework.settings.json_settings.json_helper.dump")
@patch("builtins.open")
@patch("pyzeta.framework.settings.json_settings.json_helper.load")
@pytest.mark.parametrize("settingName", ["INVALID_KEY", "logLevel", "verbose"])
def testInvalidSettings(
    loadMock: MagicMock,
    openMock: MagicMock,
    dumpMock: MagicMock,
    settingName: tSettingsKey,
) -> None:
    """
    Test exception raising when an invalid setting is given.

    :param settingName: Setting name to test, parametrized by pytest
    """
    with pytest.raises(InvalidSettingException):
        # at least one of these should fail, no matter which
        # settingName is used
        JSONHelper.createOrUpdateSetting(
            "DOES_NOT_EXIST.json", settingName, "invalidValue"  # type: ignore
        )
    dumpMock.assert_not_called()
    openMock.assert_called()
    loadMock.assert_called()
