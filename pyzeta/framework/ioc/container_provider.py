"""
Module container_provider.py from the package PyZeta.
TODO

Authors:\n
- Philipp Schuette\n
"""

from typing import Optional

from pyzeta.framework.ioc.container import Container


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
