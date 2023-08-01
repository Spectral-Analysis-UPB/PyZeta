"""
Module providing an abstract factory that maps named constants to their
corresponding implementations of `HyperbolicMapSystem`.

Authors:\n
- Philipp Schuette\n
"""

from typing import Optional

from pyzeta.core.dynamics.function_systems.implementations import (
    FlowAdaptedCylinderMap,
    FunnelTorusMap,
    GeometricFunnelTorusMap,
    HyperbolicCylinderMap,
)
from pyzeta.core.dynamics.function_systems.map_system import (
    HyperbolicMapSystem,
)
from pyzeta.core.pyzeta_types.map_systems import MapSystemType
from pyzeta.core.pyzeta_types.system_arguments import tMapSystemInitArgs
from pyzeta.framework.ioc.container_provider import ContainerProvider
from pyzeta.framework.pyzeta_logging.log_manager import LogManager
from pyzeta.framework.pyzeta_logging.logger_facade import PyZetaLogger
from pyzeta.framework.settings.settings_service import SettingsService


class MapSystemFactory:
    "Abstract factory producing `HyperbolicMapSystem` implementations."

    # the module level logger
    _logger: Optional[PyZetaLogger] = None

    @staticmethod
    def getConcreteMapSystem(
        systemType: MapSystemType,
        *,
        initArgs: tMapSystemInitArgs,
    ) -> HyperbolicMapSystem:
        """
        TODO.
        """
        if MapSystemFactory._logger is None:
            MapSystemFactory._logger = LogManager.initLogger(
                __name__.rsplit(".", maxsplit=1)[-1],
                ContainerProvider.getContainer()
                .tryResolve(SettingsService)
                .logLevel,
            )

        MapSystemFactory._logger.debug(
            "requested usage of a %s", systemType.value
        )

        if systemType == MapSystemType.FUNNEL_TORUS:
            return FunnelTorusMap(**initArgs)

        if systemType == MapSystemType.FLOW_CYLINDER:
            return FlowAdaptedCylinderMap(**initArgs)

        if systemType == MapSystemType.GEOMETRIC_FUNNEL_TORUS:
            return GeometricFunnelTorusMap(**initArgs)

        if systemType == MapSystemType.HYPERBOLIC_CYLINDER:
            return HyperbolicCylinderMap(**initArgs)

        raise ValueError(
            f"your requested system {systemType.value} does not exist"
        )
