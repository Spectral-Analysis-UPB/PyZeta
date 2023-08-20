"""
Module container_provider.py from the package PyZeta.
The static (global) ContainerProvider exposes the global container instance
valid for the current project instance. Every object that requires a container
and cannot obtain it from anywhere else should request it from here.

Authors:\n
- Philipp Schuette\n
"""

from typing import Optional, Type, TypeVar

from typing_extensions import ParamSpec

from pyzeta.framework.aop.aspect import Aspect
from pyzeta.framework.ioc.container import Container

S = TypeVar("S")
T = TypeVar("T")
P = ParamSpec("P")


class ContainerProvider:
    "Static folder providing a pre-built (during initialization) container."

    _container: Optional[Container] = None

    @staticmethod
    def getContainer() -> Container:
        "Return the pre-built container instance."
        if ContainerProvider._container is None:
            raise ValueError("No pre-built container available right now!")
        return ContainerProvider._container

    @staticmethod
    def setContainer(container: Container) -> None:
        "Register a pre-built container instance."
        ContainerProvider._container = container

    @staticmethod
    def registerAspectGlobally(
        aspect: Aspect[S, T, P], serviceType: Type[S]
    ) -> None:
        "Register an aspect for a type on the global container instance."
        ContainerProvider.getContainer().registerAspect(aspect, serviceType)
