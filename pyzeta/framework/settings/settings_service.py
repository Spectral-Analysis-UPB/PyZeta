"""
Class `SettingsService` from the package `pyzeta_settings`.
This module defines a protocol for a generic settings provider.

Authors:\n
- Philipp Schuette\n
"""

from typing import Protocol, runtime_checkable

from pyzeta.framework.settings.core_settings_service import CoreSettingsService


@runtime_checkable
class SettingsService(CoreSettingsService, Protocol):
    """
    Class providing a layer of abstraction for storage and retrieval of PyZeta
    related settings. Concrete `SettingService` implementations can choose
    freely their data model and persistence layer.
    """

    @property
    def verbose(self) -> bool:
        """
        Get current verbosity setting.

        :return: True if verbose mode is enabled.
        """
        ...

    @verbose.setter
    def verbose(self, value: bool) -> None:
        """
        Set the default verbosity setting.

        :param value: New verbosity setting
        """
        ...
