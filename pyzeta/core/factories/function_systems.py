"""
Module providing an abstract factory that maps named constants to their
corresponding implementations of `FunctionSystem`.

Authors:\n
- Philipp Schuette\n
"""

from typing import Optional

from pyzeta.core.dynamics.function_systems.function_system import (
    FunctionSystem,
)
from pyzeta.core.dynamics.function_systems.implementations import (
    FunnelTorus,
    GeometricFunnelTorus,
    HyperbolicCylinder,
)
from pyzeta.core.pyzeta_types.function_systems import FunctionSystemType
from pyzeta.core.pyzeta_types.system_arguments import tFunctionSystemInitArgs
from pyzeta.framework.ioc.container_provider import ContainerProvider
from pyzeta.framework.pyzeta_logging.log_manager import LogManager
from pyzeta.framework.pyzeta_logging.logger_facade import PyZetaLogger
from pyzeta.framework.settings.settings_service import SettingsService


class FunctionSystemFactory:
    "Abstract factory producing `FunctionSystem` implementations."

    # the module level logger
    _logger: Optional[PyZetaLogger] = None

    @staticmethod
    def getConcreteSystem(
        systemType: FunctionSystemType,
        *,
        initArgs: tFunctionSystemInitArgs,
    ) -> FunctionSystem:
        """
        TODO.
        """
        if FunctionSystemFactory._logger is None:
            FunctionSystemFactory._logger = LogManager.initLogger(
                __name__.rsplit(".", maxsplit=1)[-1],
                ContainerProvider.getContainer()
                .tryResolve(SettingsService)
                .logLevel,
            )

        FunctionSystemFactory._logger.debug(
            "requested usage of a %s", systemType.value
        )

        if systemType == FunctionSystemType.FUNNEL_TORUS:
            return FunnelTorus(**initArgs)

        if systemType == FunctionSystemType.GEOMETRIC_FUNNEL_TORUS:
            return GeometricFunnelTorus(**initArgs)

        if systemType == FunctionSystemType.HYPERBOLIC_CYLINDER:
            return HyperbolicCylinder(**initArgs)

        raise ValueError(
            f"your requested system {systemType.value} does not exist"
        )
