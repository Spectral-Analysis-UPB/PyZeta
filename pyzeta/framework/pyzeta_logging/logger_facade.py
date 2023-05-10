"""
Class PyZetaLogger from the package pyzeta_logging.

This module provides a facade for `logging.Logger` class from the standard
library `logging` module. Any access to loggers in this project should happen
only through this interface.

Authors:\n
- Philipp Schuette\n
"""

from typing import Protocol, Union


class PyZetaLogger(Protocol):
    "The logging interface used throughout the PyZeta project."

    def debug(self, msg: str, *args: Union[str, int, float]) -> None:
        """
        Log `msg` with severity DEBUG.

        :param msg: Message to log
        """
        ...

    def info(self, msg: str, *args: Union[str, int, float]) -> None:
        """
        Log `msg` with severity INFO.

        :param msg: Message to log
        """
        ...

    def warning(self, msg: str, *args: Union[str, int, float]) -> None:
        """
        Log `msg` with severity WARNING.

        :param msg: Message to log
        """
        ...

    def error(self, msg: str, *args: Union[str, int, float]) -> None:
        """
        Log `msg` with severity ERROR.

        :param msg: Message to log
        """
        ...

    def critical(self, msg: str, *args: Union[str, int, float]) -> None:
        """
        Log `msg` with severity CRITICAL.

        :param msg: Message to log
        """
        ...

    def setLevel(self, level: int) -> None:
        """
        Set the logging level to `level`

        :param level: New level of the logger
        """
        ...

    def isEnabledFor(self, level: int) -> bool:
        """
        Test if logging is enabled for level `level`.

        :param level: Level to test
        :return: If logging is enabled for level `level`
        """
        ...
