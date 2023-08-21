"""
Module providing an abstract factory that maps named constants to their
corresponding implementations of `AbstractZeta`.

Authors:\n
- Philipp Schuette\n
"""

from typing import Optional

from pyzeta.core.pyzeta_types.function_systems import FunctionSystemType
from pyzeta.core.pyzeta_types.integral_arguments import tOrbitIntegralInitArgs
from pyzeta.core.pyzeta_types.integrals import OrbitIntegralType
from pyzeta.core.pyzeta_types.map_systems import MapSystemType
from pyzeta.core.pyzeta_types.system_arguments import (
    tFunctionSystemInitArgs,
    tMapSystemInitArgs,
)
from pyzeta.core.pyzeta_types.zetas import WeightedZetaType, ZetaType
from pyzeta.core.zetas.abstract_wzeta import AbstractWeightedZeta
from pyzeta.core.zetas.abstract_zeta import AbstractZeta
from pyzeta.core.zetas.selberg_zeta import SelbergZeta
from pyzeta.core.zetas.wzeta import WeightedZeta
from pyzeta.framework.ioc.container_provider import ContainerProvider
from pyzeta.framework.pyzeta_logging.log_manager import LogManager
from pyzeta.framework.pyzeta_logging.logger_facade import PyZetaLogger
from pyzeta.framework.settings.settings_service import SettingsService


class ZetaFactory:
    "Abstract factory producing `AbstractZeta` implementations."

    # the module level logger
    _logger: Optional[PyZetaLogger] = None

    @staticmethod
    def getConcreteZeta(
        zetaType: ZetaType,
        *,
        functionSystem: FunctionSystemType,
        systemInitArgs: tFunctionSystemInitArgs,
    ) -> AbstractZeta:
        """
        TODO.
        """
        if ZetaFactory._logger is None:
            ZetaFactory._logger = LogManager.initLogger(
                __name__.rsplit(".", maxsplit=1)[-1],
                ContainerProvider.getContainer()
                .tryResolve(SettingsService)
                .logLevel,
            )

        ZetaFactory._logger.debug("requested usage of a %s", zetaType.value)

        if zetaType == ZetaType.SELBERG:
            return SelbergZeta(
                functionSystem=functionSystem, systemInitArgs=systemInitArgs
            )

        if zetaType == ZetaType.REDUCED_SELBERG:
            pass

        raise ValueError(
            f"your requested system {zetaType.value} does not exist"
        )

    @staticmethod
    def getConcreteWeightedZeta(
        zetaType: WeightedZetaType,
        *,
        mapSystem: MapSystemType,
        systemInitArgs: tMapSystemInitArgs,
        integralType: OrbitIntegralType,
        integralInitArgs: tOrbitIntegralInitArgs,
    ) -> AbstractWeightedZeta:
        """
        TODO.
        """
        if ZetaFactory._logger is None:
            ZetaFactory._logger = LogManager.initLogger(
                __name__.rsplit(".", maxsplit=1)[-1],
                ContainerProvider.getContainer()
                .tryResolve(SettingsService)
                .logLevel,
            )

        if zetaType == WeightedZetaType.WEIGHTED:
            return WeightedZeta(
                mapSystem=mapSystem,
                systemInitArgs=systemInitArgs,
                integralType=integralType,
                integralInitArgs=integralInitArgs,
            )

        if zetaType == WeightedZetaType.REDUCED_WEIGHTED:
            pass

        raise ValueError(
            f"your requested system {zetaType.value} does not exist"
        )
