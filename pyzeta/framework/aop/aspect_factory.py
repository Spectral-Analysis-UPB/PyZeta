"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from os import remove
from typing import Any, List, Optional

from pyzeta.framework.aop.advice import Advice
from pyzeta.framework.aop.advice_args import tAdviceInitArgs
from pyzeta.framework.aop.advice_type import AdviceType
from pyzeta.framework.aop.analyzers.profiling_advice import ProfilingAdvice
from pyzeta.framework.aop.aspect import Aspect
from pyzeta.framework.aop.point_cut import PointCut
from pyzeta.framework.aop.rule import Rule
from pyzeta.framework.ioc.container_provider import ContainerProvider
from pyzeta.framework.pyzeta_logging.log_manager import LogManager
from pyzeta.framework.pyzeta_logging.logger_facade import PyZetaLogger
from pyzeta.framework.settings.settings_service import SettingsService


class AspectFactory:
    "Static factory used for creation of pre-defined and custom aspects."

    _logger: Optional[PyZetaLogger] = None

    @staticmethod
    def getConcreteAdvice(
        adviceType: AdviceType,
        initArgs: tAdviceInitArgs,
        pointCutPattern: str,
    ) -> Aspect[Any, None, Any]:
        """
        TODO.
        """
        if AspectFactory._logger is None:
            AspectFactory._logger = LogManager.initLogger(
                __name__.rsplit(".", maxsplit=1)[-1],
                ContainerProvider.getContainer()
                .tryResolve(SettingsService)
                .logLevel,
            )
        AspectFactory._logger.debug("requested usage of %s", adviceType.value)

        if adviceType == AdviceType.PROFILING:
            profilingAdvice: Advice[None, Any] = ProfilingAdvice(**initArgs)
            pointCut: PointCut = PointCut(pointCutPattern)
            # remove any previous statistics files
            try:
                remove(initArgs["statsFile"] + ProfilingAdvice.extension)
            except FileNotFoundError:
                AspectFactory._logger.info("no previous stats file to remove!")

            rules: List[Rule[None, Any]] = [Rule(pointCut, profilingAdvice)]
            return Aspect(rules=rules)

        raise ValueError(f"advice {adviceType.value} currently not supported!")
