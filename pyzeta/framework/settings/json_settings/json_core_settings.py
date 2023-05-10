"""
Class JSONCoreSettingsService from the module `pyzeta.settings`.

This module provides a straight-forward implementation of the
`CoreSettingsSerivce` based on a `json` serialization backend.

Authors:\n
- Philipp Schuette\n
"""

from os.path import dirname, join
from typing import Dict, Final

from pyzeta.framework.pyzeta_logging.log_levels import LogLevel
from pyzeta.framework.settings.core_settings_service import CoreSettingsService
from pyzeta.framework.settings.invalid_setting_exception import (
    InvalidSettingException,
)
from pyzeta.framework.settings.json_settings.json_helper import JSONHelper

# location where the default settings should be
DEFAULT_SETTINGS: Final[str] = join(dirname(__file__), "default_settings.json")
# default location where custom settings are saved
CUSTOM_SETTINGS: Final[str] = join(dirname(__file__), "custom_settings.json")


class JSONCoreSettingsService(CoreSettingsService):
    """
    This class provides a layer of abstraction for storage and retrieval of
    PyZeta core settings using JSON for persistence. Any read and/or write
    access to (core) settings must happen through a service like this one.
    """

    __slots__ = ("_level",)

    def __init__(self) -> None:
        """
        Create an instance of a new `CoreSettingsService`. The basis for its
        properties are the currently persisted (user or default) settings.
        """
        currentSettings: Dict[str, str] = {}
        # first load default settings (must always exist)...
        JSONHelper.loadCoreSettingsFromFile(DEFAULT_SETTINGS, currentSettings)
        # ...then try to load custom settings (might not exist)
        JSONHelper.loadCoreSettingsFromFile(CUSTOM_SETTINGS, currentSettings)

        # set default logging level
        for level in LogLevel:
            if level.name == currentSettings["logLevel"]:
                self._level = level

        # check if required defaults were loaded successfully
        for attr in self.__slots__:
            if not hasattr(self, attr):
                raise InvalidSettingException(attr[1:])

    def __str__(self) -> str:
        """
        A printable string representation of the currently active core settings
        configuration.

        :return: string representation of current core setting
        """
        return f"-> default log level:   {self.logLevel.name}\n"

    # docstr-coverage:inherited
    @property
    def logLevel(self) -> LogLevel:
        return self._level

    # docstr-coverage:inherited
    @logLevel.setter
    def logLevel(self, value: LogLevel) -> None:
        self._level = value
        JSONHelper.createOrUpdateCoreSetting(
            CUSTOM_SETTINGS, "logLevel", value
        )
