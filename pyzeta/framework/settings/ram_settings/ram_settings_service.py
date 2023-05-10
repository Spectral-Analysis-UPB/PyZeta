"""
A simple in-memory implementation of the `SettingsService` interface. Instances
of this service do not persist settings beyond program runtime. Their main use
is during testing of components which depend on settings.

Authors:\n
- Philipp Schuette\n
"""

from pyzeta.framework.pyzeta_logging.log_levels import LogLevel
from pyzeta.framework.settings.settings_service import SettingsService


class RAMSettingsService(SettingsService):
    "Simple, non-persistent implementation of `SettingsService`."

    def __init__(
        self, logLevel: LogLevel = LogLevel.NOTSET, verbose: bool = False
    ) -> None:
        """
        Initialize a new in-memory settings service with given default values.

        :param logLevel:
        :param verbose:
        """
        self._logLevel = logLevel
        self._verbose = verbose

    # docstr-coverage:inherited
    @property
    def logLevel(self) -> LogLevel:
        return self._logLevel

    # docstr-coverage:inherited
    @logLevel.setter
    def logLevel(self, value: LogLevel) -> None:
        self._logLevel = value

    # docstr-coverage:inherited
    @property
    def verbose(self) -> bool:
        return self._verbose

    # docstr-coverage:inherited
    @verbose.setter
    def verbose(self, value: bool) -> None:
        self._verbose = value
