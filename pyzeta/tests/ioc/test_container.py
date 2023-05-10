"""
Basic tests for the registration and retrieval of configurations from a
container.

Authors:\n
- Philipp Schuette\n
"""

from typing import Protocol, runtime_checkable

import pytest

from pyzeta.framework.ioc.configuration_exception import (
    InvalidServiceConfiguration,
)
from pyzeta.framework.ioc.container import Container


# some classes for testing
@runtime_checkable
class FooInterface(Protocol):
    "Interface for test class."

    def method(self) -> None:
        "This does nothing."
        ...


class Foo(FooInterface):
    "Test class."

    def __init__(self) -> None:
        "Default constructor."

    def method(self) -> None:
        "Interface implementation."


@pytest.mark.container
def testRegisterSingleton() -> None:
    "Test singleton registration."
    container = Container()
    instance: FooInterface = Foo()

    # try valid registration
    assert container is container.registerAsSingleton(FooInterface, instance)
    resolvent = container.tryResolve(FooInterface)

    assert resolvent is instance

    # try invalid registration
    with pytest.raises(InvalidServiceConfiguration):
        container.registerAsSingleton(FooInterface, 0).registerAsSingleton(
            FooInterface, Foo()
        )


@pytest.mark.container
def testRegisterTransient() -> None:
    "Test transient registration."
    container = Container()

    # try valid registration
    assert container is container.registerAsTransient(FooInterface, Foo)
    resolvent1 = container.tryResolve(FooInterface)
    resolvent2 = container.tryResolve(FooInterface)

    assert isinstance(resolvent1, FooInterface)
    assert isinstance(resolvent1, Foo)
    assert isinstance(resolvent2, FooInterface)
    assert isinstance(resolvent2, Foo)

    # check that genuinely new objects were resolved
    assert resolvent1 is not resolvent2


@pytest.mark.container
def testContainerSealing() -> None:
    "Test sealing operation on container."
    container = Container()
    container.seal()

    # try valid registration on sealed container
    with pytest.raises(ValueError):
        container.registerAsSingleton(FooInterface, Foo())

    # try valid registration on sealed container
    with pytest.raises(ValueError):
        container.registerAsTransient(FooInterface, Foo)

    # try sealing container twice
    with pytest.raises(ValueError):
        container.seal()


@pytest.mark.container
def testInvalidConfiguration() -> None:
    "Test if invalid registered configurations raise exceptions."
    container = Container()

    # try to resolve a non-existing configuration
    with pytest.raises(InvalidServiceConfiguration):
        container.tryResolve(FooInterface)

    # register an invalid configuration and try to resolve it
    container.registerAsTransient(FooInterface, lambda: None)  # type: ignore
    with pytest.raises(InvalidServiceConfiguration):
        container.tryResolve(FooInterface)
