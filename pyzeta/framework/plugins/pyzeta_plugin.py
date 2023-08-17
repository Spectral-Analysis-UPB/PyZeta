"""
This module contains the base interface for plugins. Its methods provide the
necessary functions for plugin handling.

Authors:\n
- Philipp Schuette\n
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Generic, Tuple, Type, TypeVar, Union

from pyzeta.framework.settings.settings_service import SettingsService
from pyzeta.view.cli.parser_facade import PyZetaParserInterface

tPluggable = Union[
    SettingsService,
    PyZetaParserInterface,
]
T_co = TypeVar("T_co", bound=tPluggable, covariant=True)


class PyZetaPlugin(ABC, Generic[T_co]):
    """
    Interface for plugins. Methods for instantiation and plugin information
    need to be implemented by concrete subclasses.
    """

    def __str__(self) -> str:
        "Print a human-readable representation of the plugin."
        major, minor, patch = self.pluginVersion
        maxLength = 30
        cutoff = min(len(self.pluginName), maxLength)
        return (
            f"{self.pluginName[:cutoff]: <{maxLength}} "
            f" @ v{major}.{minor}.{patch}"
        )

    @staticmethod
    @abstractmethod
    def initialize() -> Callable[..., T_co]:
        """
        Returns a factory for the plugin's implementation of `T_co`.

        :return: Factory for plugin implementation of `T_co`.
        """

    @staticmethod
    @abstractmethod
    def getInstance() -> PyZetaPlugin[T_co]:
        """
        Return the singleton instance of `PyZetaPlugin` which provides a
        service of type `T_co`.

        :return: `PyZetaPlugin` instance.
        """

    @property
    @abstractmethod
    def pluginType(self) -> Type[T_co]:
        """
        Return the type provided by the plugin.

        :return: Service type of plugin.
        """

    @property
    @abstractmethod
    def pluginName(self) -> str:
        """
        Return the name of the plugin.

        :return: Plugin name.
        """

    @property
    @abstractmethod
    def pluginVersion(self) -> Tuple[int, int, int]:
        """
        Return the version of the plugin as (`major`, `minor`, `patch`).

        :return: Plugin version.
        """
