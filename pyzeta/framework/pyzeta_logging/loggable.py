"""
Module providing a simple mixin class which enables logging functionality.

Authors:\n
- Philipp Schuette\n
"""

from typing import Protocol

from pyzeta.framework.pyzeta_logging.log_levels import LogLevel
from pyzeta.framework.pyzeta_logging.log_manager import LogManager
from pyzeta.framework.pyzeta_logging.logger_facade import PyZetaLogger
from pyzeta.framework.settings.json_settings_service import JSONSettingsService


class Loggable(Protocol):
    "Mixin for combination with classes which support logging."

    __slots__ = ("_logger",)

    _logger: PyZetaLogger

    @property
    def logger(self) -> PyZetaLogger:
        """
        The logger instance associated with this Loggable class. Instance
        creation happens upon first property access.

        :returns: the logger of this class
        """
        # TODO: resolve settings service from container!
        if not hasattr(self, "_logger"):
            settingsService = JSONSettingsService()
            self._logger = LogManager.initLogger(
                self.__module__.rsplit(".", maxsplit=1)[-1],
                settingsService.logLevel,
            )
        return self._logger

    def setLevel(self, level: LogLevel) -> None:
        """
        Set the log level.

        :param level: the new log level
        """
        self.logger.setLevel(level=level.value)
