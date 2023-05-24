"""
Very simple base implementation for collections of feature flags. This is part
of the `PyZeta` framework.

Usage example:

.. code-block:: python

    MyToggles(ToggleCollection):
        toggle1: bool
        toggle2: bool

    toggles = MyToggles("toggles.json")

Authors:\n
- Philipp Schuette\n
"""

from json import load
from typing import Dict, Type, TypedDict

from pyzeta.framework.feature_toggle.feature_flag import FeatureFlag
from pyzeta.framework.feature_toggle.toggle_exception import ToggleException
from pyzeta.framework.pyzeta_logging.loggable import Loggable


class LoadedToggleRequired(TypedDict):
    "This is need to be able to mix required and optional keys pre python3.11."
    name: str
    value: bool
    description: str


class LoadedToggle(LoadedToggleRequired, total=False):
    "The type of a toggle configuration loaded from json."
    timesAccessible: int


# pylint: disable=too-few-public-methods
class ToggleCollection(Loggable):
    "Subclass this class to implement your own collection of feature flags."

    def __init__(self, filename: str) -> None:
        """
        Initialize a new collection of feature toggles from a given `.json`
        config file.

        :param filename: name of the .json config file
        """
        annotations = self._retrieveAnnotations()
        self._config = self._loadFromJson(filename)

        if undeclaredToggles := set(self._config) - set(annotations):
            raise ToggleException(
                f"excess toggles [{undeclaredToggles}] in config file!"
            )

        if unconfiguredToggles := set(annotations) - set(self._config):
            raise ToggleException(
                f"unconfigured toggles [{unconfiguredToggles}] in script!"
            )

        for toggle, config in self._config.items():
            self._createAttr(toggle, config)

    def __str__(self) -> str:
        "Custom string representation of a collection of feature flags."
        return f"{self._config}"

    def _retrieveAnnotations(self) -> Dict[str, Type[object]]:
        "Retrieve the annotations of the toggle collection."
        if not (annotations := getattr(self, "__annotations__", None)):
            raise ToggleException(
                "valid collection must contain >=1 annotated variables!"
            )

        result: Dict[str, Type[object]] = {}
        for attr, attrType in annotations.items():
            if attrType != bool:
                raise ToggleException(f"{attr} must be bool, not {attrType}!")
            # further checks on the attributes present could be done here
            result[attr] = attrType
        return result

    def _loadFromJson(self, filename: str) -> Dict[str, LoadedToggle]:
        "Load a collection of toggles from a .json file."
        try:
            with open(filename, "r", encoding="utf-8") as configFile:
                config = load(configFile)
        except Exception as ex:
            raise ToggleException(f"config file {filename} invalid!") from ex

        result: Dict[str, LoadedToggle] = {}
        for toggleName, toggleConfig in config.items():
            # further checks on the loaded configuration could be done here
            result[toggleName] = toggleConfig
        return result

    def _createAttr(self, toggle: str, config: LoadedToggle) -> None:
        "Create a toggle instance attribute from a config."
        flag = FeatureFlag(**config, logger=self.logger)
        setattr(self, toggle, flag)
