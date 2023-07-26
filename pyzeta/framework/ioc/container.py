"""
Module container.py from the package `pyzeta.framework.ioc`.
This module provides a way to register and locate services used throughout
the project, to enable loading additional services for the plugin system.

Authors:\n
- Philipp Schuette\n
"""

from __future__ import annotations

from inspect import Parameter, signature
from typing import Any, Callable, Dict, Type, TypeVar

from typing_extensions import ParamSpec

from pyzeta.framework.aop.aspect import Aspect
from pyzeta.framework.ioc.configuration_exception import (
    InvalidServiceConfiguration,
)

# type variable for the various signatures of Container methods
S = TypeVar("S")
T = TypeVar("T")
P = ParamSpec("P")


class Container:
    """
    Container class used to add and resolve services as part of dependency
    inversion.
    """

    __slots__ = (
        "_transientServices",
        "_singletonServices",
        "_aspects",
        "_sealed",
    )

    def __init__(self) -> None:
        "Initialize a new container instance."
        self._transientServices: Dict[Type[object], Callable[..., object]] = {}
        self._singletonServices: Dict[Type[object], object] = {}
        self._aspects: Dict[Type[object], Aspect[Any, Any, Any]] = {}
        self._sealed: bool = False

    def registerAsSingleton(
        self, serviceType: Type[T], instance: T
    ) -> Container:
        """
        Register service `instance` as a singleton service. The instance
        resolved will be identical to the instance registered.

        :param serviceType: Type of service
        :param instance: Service instance
        :raises ValueError: If the container is sealed, no new services can be
            registered.
        :raises InvalidServiceConfiguration: Given instance must implement the
            given type
        :return: Return the container instance itself for method chaining
        """
        if self.isSealed():
            raise ValueError(
                f"can't register singleton {serviceType} in sealed container!"
            )
        if isinstance(instance, serviceType):
            self._singletonServices[serviceType] = instance
            return self
        raise InvalidServiceConfiguration(serviceType)

    def registerAsTransient(
        self, serviceType: Type[T], factory: Callable[..., T]
    ) -> Container:
        """
        Register a transient service. Note that you MUST implement a (dummy)
        default constructor if you want to register a class without constructor
        as an instance factory and that class inherits from `typing.Protocol`.

        :param serviceType: Type of service to register.
        :param factory: Factory for the given service
        :raises ValueError: If the container is sealed, no new services can be
            registered.
        :return: Return the container instance itself for method chaining
        """
        if self.isSealed():
            raise ValueError(
                f"cannot register transient {serviceType} on sealed container!"
            )
        self._transientServices[serviceType] = factory
        return self

    def tryResolve(self, serviceType: Type[T], **kwargs: object) -> T:
        """
        Try to resolve the requested service type by first searching registered
        singleton and then registered transient configurations.

        :param serviceType: Type of service to resolve
        :raises InvalidServiceConfiguration: If the given `serviceType` can
            not be resolved, an exception is raised
        :return: An instance of the given service. If the service is
            transient, the factory is called with the parameters given
            by `**kwargs`.
        """
        # try to resolve as singleton
        instance = self._singletonServices.get(serviceType, None)
        if isinstance(instance, serviceType):
            if aspect := self._aspects.get(serviceType, None):
                aspect(type(instance))
            return instance

        # try to resolve as transient
        factory = self._transientServices.get(serviceType, None)
        if factory is None:
            raise InvalidServiceConfiguration(serviceType)
        sig = signature(factory)
        arguments: Dict[str, object] = {}

        # try to instantiate an instance from the factory and given kwargs or
        # default parameters of the factory - additional kwargs are ignored
        for param in sig.parameters:
            try:
                arguments[param] = kwargs[param]
            except KeyError:
                if (arg := sig.parameters[param].default) != Parameter.empty:
                    arguments[param] = arg
                else:
                    arguments[param] = self.tryResolve(
                        sig.parameters[param].annotation
                    )
        instance = factory(**arguments)
        if isinstance(instance, serviceType):
            if aspect := self._aspects.get(serviceType, None):
                aspect(type(instance))
            return instance

        # resolving failed
        raise InvalidServiceConfiguration(serviceType)

    def seal(self) -> None:
        """
        Seal the container to prevent additional services from being
        registered.

        :raises ValueError: Raises an exception if the container has already
            been sealed.
        """
        if self._sealed:
            raise ValueError("cannot re-seal an already sealed container!")
        self._sealed = True

    def isSealed(self) -> bool:
        """
        Return `True` if the container is sealed.

        :return: `True` if container is sealed
        """
        return self._sealed

    def clearConfigurations(self) -> None:
        """
        Clear all previous configurations, unsealing the container in the
        process.
        """
        self._transientServices.clear()
        self._singletonServices.clear()
        self._sealed = False

    def registerAspect(
        self, aspect: Aspect[S, T, P], serviceType: Type[S]
    ) -> Container:
        """
        Register an aspect for a given type of service. The aspect intercepts
        calls to resolve the service type and adorns the concrete return
        types lazily.

        :param aspect: Aspect to apply to the service
        :param serviceType: The type of service whose implementations gets
            aspect gets applied to
        :return: Return the container instance for method chaining
        """
        if self.isSealed():
            raise ValueError(
                f"cannot register aspect {aspect} for {serviceType} if sealed!"
            )
        self._aspects[serviceType] = aspect
        return self
