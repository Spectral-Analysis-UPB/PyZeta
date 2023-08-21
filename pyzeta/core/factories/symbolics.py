"""
Module providing an abstract factory that maps named constants to their
corresponding implementations of `AbstractSymbolicDynamics`.

Authors:\n
- Philipp Schuette\n
"""

from typing import Optional

from pyzeta.core.dynamics.symbolic_dynamics.abstract_dynamics import (
    AbstractSymbolicDynamics,
)
from pyzeta.core.dynamics.symbolic_dynamics.symbolic_dynamics import (
    SymbolicDynamics,
)
from pyzeta.core.pyzeta_types.general import tBoolMat
from pyzeta.core.pyzeta_types.symbolics import SymbolicDynamicsType
from pyzeta.framework.ioc.container_provider import ContainerProvider
from pyzeta.framework.pyzeta_logging.log_manager import LogManager
from pyzeta.framework.pyzeta_logging.logger_facade import PyZetaLogger
from pyzeta.framework.settings.settings_service import SettingsService


class SymbolicDynamicsFactory:
    "Abstract factory producing `AbstractSymbolicDynamics` implementations."

    # the module level logger
    _logger: Optional[PyZetaLogger] = None

    @staticmethod
    def getConcreteSymbolics(
        symbolicsType: SymbolicDynamicsType,
        *,
        adjacencyMatrix: tBoolMat,
    ) -> AbstractSymbolicDynamics:
        """
        TODO.
        """
        if SymbolicDynamicsFactory._logger is None:
            SymbolicDynamicsFactory._logger = LogManager.initLogger(
                __name__.rsplit(".", maxsplit=1)[-1],
                ContainerProvider.getContainer()
                .tryResolve(SettingsService)
                .logLevel,
            )

        SymbolicDynamicsFactory._logger.debug(
            "requested usage of a %s", symbolicsType.value
        )

        if symbolicsType == SymbolicDynamicsType.NON_REDUCED:
            return SymbolicDynamics(adjacencyMatrix=adjacencyMatrix)

        raise ValueError(
            f"your requested symbolics {symbolicsType.value} does not exist"
        )
