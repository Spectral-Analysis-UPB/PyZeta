"""
Module providing an abstract factory that maps named constants to their
corresponding implementations of `IntegralProvider`.

Authors:\n
- Philipp Schuette\n
"""


from typing import Optional

from pyzeta.core.dynamics.function_systems.implementations.fundomain_integrals import (
    FundamentalDomainIntegrals,
)
from pyzeta.core.dynamics.function_systems.implementations.poincare_integrals import (
    PoincareSectionIntegrals,
)
from pyzeta.core.dynamics.function_systems.integral_provider import (
    IntegralProvider,
)
from pyzeta.core.dynamics.function_systems.map_system import (
    HyperbolicMapSystem,
)
from pyzeta.core.dynamics.function_systems.moebius_system import (
    MoebiusMapSystem,
)
from pyzeta.core.pyzeta_types.integral_arguments import tOrbitIntegralInitArgs
from pyzeta.core.pyzeta_types.integrals import OrbitIntegralType
from pyzeta.framework.ioc.container_provider import ContainerProvider
from pyzeta.framework.pyzeta_logging.log_manager import LogManager
from pyzeta.framework.pyzeta_logging.logger_facade import PyZetaLogger
from pyzeta.framework.settings.settings_service import SettingsService


class OrbitIntegralFactory:
    "Abstract factory producing `IntegralProvider` implementations."

    # the module level logger
    _logger: Optional[PyZetaLogger] = None

    @staticmethod
    def getConcreteIntegral(
        integralType: OrbitIntegralType,
        *,
        mapSystem: HyperbolicMapSystem,
        initArgs: tOrbitIntegralInitArgs,
    ) -> IntegralProvider:
        """
        TODO.
        """
        if OrbitIntegralFactory._logger is None:
            OrbitIntegralFactory._logger = LogManager.initLogger(
                __name__.rsplit(".", maxsplit=1)[-1],
                ContainerProvider.getContainer()
                .tryResolve(SettingsService)
                .logLevel,
            )

        OrbitIntegralFactory._logger.debug(
            "requested usage of a %s", integralType.value
        )

        if integralType == OrbitIntegralType.POINCARE:
            return PoincareSectionIntegrals(mapSystem=mapSystem, **initArgs)

        if integralType == OrbitIntegralType.FUNDAMENTAL_DOMAIN:
            if not isinstance(mapSystem, MoebiusMapSystem):
                raise ValueError(
                    f"cannot use {mapSystem} with {integralType}!"
                )
            return FundamentalDomainIntegrals(mapSystem=mapSystem, **initArgs)

        raise ValueError(
            f"your requested system {integralType.value} does not exist"
        )
