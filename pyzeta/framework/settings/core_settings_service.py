"""
Class `CoreSettingsService` from the package `pyzeta_settings`.
This module defines a protocol for a generic settings provider pertaining to
the core features of `PyZeta`.

Authors:\n
- Philipp Schuette\n
"""

from typing import Protocol, runtime_checkable

from pyzeta.framework.pyzeta_logging.log_levels import LogLevel


@runtime_checkable
class CoreSettingsService(Protocol):
    """
    Class providing a layer of abstraction for storage and retrieval of PyZeta
    core settings. Concrete `SettingService` implementations can choose freely
    their data model and persistence layer.
    """

    @property
    def logLevel(self) -> LogLevel:
        """
        Get the current LogLevel setting.

        :return: Current LogLevel
        """
        ...

    @logLevel.setter
    def logLevel(self, value: LogLevel) -> None:
        """
        Set the LogLevel to `value`.

        :param value: New LogLevel to use
        """
        ...
