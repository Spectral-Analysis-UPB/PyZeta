"""
TODO.

Authors:\n
- Philipp Schuette
"""

from os.path import abspath, dirname, join

import pytest

from pyzeta.core.symmetries.symmetry_group import SymmetryGroup
from pyzeta.framework.initialization.initialization_handler import (
    PyZetaInitializationHandler,
)
from pyzeta.framework.ioc.container import Container
from pyzeta.framework.plugins.installation_helper import InstallationHelper
from pyzeta.framework.plugins.plugin_loader import PluginLoader

PyZetaInitializationHandler.initPyZetaServices()


def testGroupPlugin() -> None:
    "Test installation of the custom group plugin."
    # install plugin and data from the local test directory
    pluginPath = abspath(join(dirname(__file__), "group_plugin.py"))
    dataPath = abspath(join(dirname(__file__), "group_data.json"))
    assert InstallationHelper.installPlugin(pluginPath)
    assert InstallationHelper.installPlugin(dataPath)

    container = Container()
    PluginLoader.loadPlugins(container)

    customGroup = container.tryResolve(SymmetryGroup)
    with pytest.raises(NotImplementedError):
        customGroup.getElements()

    # uninstall plugin and data from the global plugin installation directory
    assert InstallationHelper.uninstallPlugin("group_plugin.py")
    assert InstallationHelper.uninstallPlugin("group_data.json")
