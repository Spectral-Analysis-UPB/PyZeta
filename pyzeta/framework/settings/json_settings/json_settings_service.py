"""
This module provides a straight-forward implementation of the `SettingsSerivce`
based on a `json` serialization backend.

Authors:\n
- Philipp Schuette\n
"""

from os.path import dirname, join
from typing import Dict, Final, Tuple, Union

from pyzeta.framework.pyzeta_logging.log_levels import LogLevel
from pyzeta.framework.settings.invalid_setting_exception import (
    InvalidSettingException,
)
from pyzeta.framework.settings.json_settings.json_core_settings import (
    JSONCoreSettingsService,
)
from pyzeta.framework.settings.json_settings.json_helper import JSONHelper
from pyzeta.framework.settings.settings_service import SettingsService

# location where the default settings should be
DEFAULT_SETTINGS: Final[str] = join(dirname(__file__), "default_settings.json")
# default location where custom settings are saved
CUSTOM_SETTINGS: Final[str] = join(dirname(__file__), "custom_settings.json")


class JSONSettingsService(SettingsService):
    """
    This class provides a layer of abstraction for storage and retrieval of
    PyZeta related settings using JSON for persistence. Any read and/or write
    access to settings must happen through a service like this one.
    """

    __slots__ = ("_coreSettings", "_verbose")

    def __init__(self) -> None:
        """
        Create an instance of a new `SettingsService`. The basis for its
        properties are the currently persisted (user or default) settings.
        """
        self._coreSettings = JSONCoreSettingsService()
        currentSettings: Dict[str, Union[str, bool, Tuple[int, int]]] = {}
        # first load default settings (must always exist)...
        JSONHelper.loadSettingsFromFile(DEFAULT_SETTINGS, currentSettings)
        # ...then try to load custom settings (might not exist)
        JSONHelper.loadSettingsFromFile(CUSTOM_SETTINGS, currentSettings)

        # set default verbosity
        verbosity = currentSettings.get("verbose", None)
        if verbosity is not None:
            self._verbose = bool(verbosity)

        # check if required settings were loaded successfully
        for attr in self.__slots__:
            if not hasattr(self, attr):
                raise InvalidSettingException(attr[1:])

    def __str__(self) -> str:
        """
        A printable string representation of the currently active settings
        configuration.

        :return: string representation of current setting
        """
        return (
            f"Currently active settings configuration:\n{self._coreSettings}"
            f"-> default verbosity:   {self.verbose}\n"
        )

    # docstr-coverage:inherited
    @property
    def logLevel(self) -> LogLevel:
        return self._coreSettings.logLevel

    # docstr-coverage:inherited
    @logLevel.setter
    def logLevel(self, value: LogLevel) -> None:
        self._coreSettings.logLevel = value

    # docstr-coverage:inherited
    @property
    def verbose(self) -> bool:
        return self._verbose

    # docstr-coverage:inherited
    @verbose.setter
    def verbose(self, value: bool) -> None:
        self._verbose = value
        JSONHelper.createOrUpdateSetting(CUSTOM_SETTINGS, "verbose", value)
