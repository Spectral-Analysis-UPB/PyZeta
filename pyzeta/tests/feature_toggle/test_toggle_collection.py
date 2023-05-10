"""
A collection of simple tests for the feature toggle implementation of `PyZeta`.

Authors:\n
- Philipp Schuette\n
"""

from os.path import dirname, join

import pytest

from pyzeta.framework.feature_toggle.toggle_collection import ToggleCollection
from pyzeta.framework.initialization.initialization_handler import (
    PyZetaInitializationHandler,
)
from pyzeta.framework.ioc.container import Container
from pyzeta.framework.ioc.container_provider import ContainerProvider

# build a suitable container
container = Container()
PyZetaInitializationHandler.initModeIndependentServices(container)
ContainerProvider.setContainer(container)


def testValidToggle() -> None:
    "Test a valid collection of feature flags."

    # pylint: disable=too-few-public-methods
    class ValidToggles(ToggleCollection):
        "A custom collection with two toggles. For demonstration only!"
        toggle1: bool
        toggle2: bool
        toggle3: bool

    # create the toggle
    configFile = join(dirname(__file__), "toggles.json")
    toggles = ValidToggles(configFile)

    # check if the flags are really there
    assert hasattr(toggles, "toggle1")
    assert hasattr(toggles, "toggle2")
    assert hasattr(toggles, "toggle3")

    # check if the flags have correct values
    assert toggles.toggle1
    assert not toggles.toggle2
    assert toggles.toggle3

    # check the accessibility bounds
    for _ in range(10):
        assert not toggles.toggle2
        assert toggles.toggle3
    assert not toggles.toggle1


def testNonExistingToggle() -> None:
    """
    Test a invalid collection of feature flags that is invalid due to
    unconfigured attributes.
    """

    # pylint: disable=too-few-public-methods
    class InvalidToggles(ToggleCollection):
        "A custom collection with two toggles. For demonstration only!"
        toggle1: bool
        toggle2: bool
        toggle3: bool
        thisToggleDoesNotExist: bool

    # check if toggle creation triggers an exception
    configFile = join(dirname(__file__), "toggles.json")
    with pytest.raises(ValueError):
        toggles = InvalidToggles(configFile)
        assert toggles.thisToggleDoesNotExist


def testEmptyToggle() -> None:
    "Test an empty collection of feature flags."

    # pylint: disable=too-few-public-methods
    class EmptyToggles(ToggleCollection):
        "An example for an invalid (empty) collection of toggles."

    # check if toggle creation triggers an exception
    configFile = join(dirname(__file__), "toggles.json")
    with pytest.raises(ValueError):
        toggles = EmptyToggles(configFile)
        assert toggles
