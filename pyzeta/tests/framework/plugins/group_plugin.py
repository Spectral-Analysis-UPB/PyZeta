"""
Module implementing a simple group plugin with trivial functionality for
testing the installation and usage of plugins.

Authors:\n
- Philipp Schuette\n
"""

from json import load
from typing import Callable, Optional, Tuple, Type

from pyzeta.core.pyzeta_types.special import tGroupElement
from pyzeta.core.symmetries.symmetry_group import SymmetryGroup
from pyzeta.core.symmetries.trivial_group import TrivialGroup
from pyzeta.framework.plugins.installation_helper import InstallationHelper
from pyzeta.framework.plugins.pyzeta_plugin import PyZetaPlugin


class TestGroup(TrivialGroup):
    "Custom (trivial) symmetry group implementation to supply as a plugin."

    def __init__(self, arg1: str, arg2: int) -> None:
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2

    def getElements(self) -> Tuple[tGroupElement, ...]:
        "Override this in our custom symmetry group."
        raise NotImplementedError(
            f"test group[{self.arg1} | {self.arg2}] is not fully implemented!"
        )

    def __str__(self) -> str:
        "Just for printing - generic plugins don't actually need this."
        return f"TestGroup({self.arg1}, {self.arg2})"


configFile = InstallationHelper.returnDataPath("group_data.json")
with open(configFile, "r", encoding="utf-8") as f:
    customData = load(f)


class GroupPlugin(PyZetaPlugin[SymmetryGroup]):
    "Test plugin providing a simple custom symmetry group to PyZeta."

    _instance: Optional[PyZetaPlugin[SymmetryGroup]] = None

    @staticmethod
    def initialize() -> Callable[..., SymmetryGroup]:
        "This is the hook of plugins into `PyZeta`."
        arg1, arg2 = customData["arg1"], customData["arg2"]
        return lambda: TestGroup(arg1=arg1, arg2=arg2)

    @staticmethod
    def getInstance() -> PyZetaPlugin[SymmetryGroup]:
        "Plugins should be realized as singletons."
        if GroupPlugin._instance is None:
            GroupPlugin._instance = GroupPlugin()
        return GroupPlugin._instance

    @property
    def pluginType(self) -> Type[SymmetryGroup]:
        "The type provided by the plugin."
        return SymmetryGroup

    @property
    def pluginName(self) -> str:
        "The name of the plugin."
        return "TestGroupPlugin"

    @property
    def pluginVersion(self) -> Tuple[int, int, int]:
        """
        The version of the plugin (the combination of version and name should
        be unique). The semantics are (`major`, `minor`, `patch`).
        """
        return (22, 1, 0)
