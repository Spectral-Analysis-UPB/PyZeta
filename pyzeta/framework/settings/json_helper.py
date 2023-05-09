"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from json import JSONDecodeError, dump, load
from typing import Dict, Literal, Tuple, Type, Union

from pyzeta.framework.pyzeta_logging.log_levels import LogLevel
from pyzeta.framework.settings.invalid_setting_exception import (
    InvalidSettingException,
)

# admissible keys when changing settings
tCoreSettingsKey = Literal["logLevel"]
tSettingsKey = Literal["verbose"]
# admissible types when assigning to settings properties
tCoreSettingsPropertyType = LogLevel
tSettingsPropertyType = bool


class JSONHelper:
    """
    Static helper class providing methods to read and manipulate json settings.
    """

    _coreSettings: Dict[tCoreSettingsKey, Type[tCoreSettingsPropertyType]] = {
        "logLevel": LogLevel
    }
    _settings: Dict[tSettingsKey, Type[tSettingsPropertyType]] = {
        "verbose": bool
    }

    @staticmethod
    def createOrUpdateCoreSetting(
        filename: str,
        setting: tCoreSettingsKey,
        value: tCoreSettingsPropertyType,
    ) -> None:
        """
        Update a core setting or create a new one if no value had previously
        been set.

        :param filename: the json file to update
        :param setting: setting to create or update
        :param value: New setting value
        :raises InvalidSettingException: If the given value is invalid for the
            specified setting, an `InvalidSettingException` is raised.
        """
        currentSettings: Dict[tCoreSettingsKey, str] = {}
        try:
            with open(filename, "r", encoding="utf-8") as custom:
                currentSettings = load(custom)
        except FileNotFoundError:
            pass
        except JSONDecodeError as exc:
            raise InvalidSettingException(f"{filename=}") from exc

        if setting in JSONHelper._coreSettings:
            if not isinstance(value, JSONHelper._coreSettings[setting]):
                raise InvalidSettingException(setting)
            currentSettings[setting] = value.name
        else:
            raise InvalidSettingException(f"key={setting}")

        with open(filename, "w", encoding="utf-8") as custom:
            dump(currentSettings, custom, indent=4)

    @staticmethod
    def loadCoreSettingsFromFile(
        filename: str, settings: Dict[str, str]
    ) -> None:
        """
        Load the settings stored in `filename` into `settings`.

        :param filename: Settings file to load
        :param settings: Dict to store the read settings in
        """
        try:
            with open(filename, "r", encoding="utf-8") as settingsFile:
                for key, value in load(settingsFile).items():
                    if key not in JSONHelper._coreSettings:
                        continue
                    settings[key] = value
        except FileNotFoundError:
            pass

    @staticmethod
    def createOrUpdateSetting(
        filename: str, setting: tSettingsKey, value: tSettingsPropertyType
    ) -> None:
        """
        Update a setting or create a new setting if no value has been set yet.

        :param filename: the json file to update
        :param setting: setting to create or update
        :param value: New setting value
        :raises InvalidSettingException: If the given value is invalid for the
            specified setting, an `InvalidSettingException` is raised.
        """
        currentSettings: Dict[tSettingsKey, bool] = {}
        try:
            with open(filename, "r", encoding="utf-8") as custom:
                currentSettings = load(custom)
        except FileNotFoundError:
            pass
        except JSONDecodeError as exc:
            raise InvalidSettingException(f"{filename=}") from exc

        if setting in JSONHelper._settings:
            if not isinstance(value, JSONHelper._settings[setting]):
                raise InvalidSettingException(setting)
            currentSettings[setting] = value
        else:
            raise InvalidSettingException(f"key={setting}")

        with open(filename, "w", encoding="utf-8") as custom:
            dump(currentSettings, custom, indent=4)

    @staticmethod
    def loadSettingsFromFile(
        filename: str, settings: Dict[str, Union[str, bool, Tuple[int, int]]]
    ) -> None:
        """
        Load the settings stored in `filename` into `settings`.

        :param filename: File to load
        :param settings: Dict to store the read settings in
        """
        try:
            with open(filename, "r", encoding="utf-8") as settingsFile:
                for key, value in load(settingsFile).items():
                    if key not in JSONHelper._settings:
                        continue
                    if isinstance(value, list):
                        value = tuple(value)
                    settings[key] = value
        except FileNotFoundError:
            pass
