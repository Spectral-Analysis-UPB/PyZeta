"""
Very basic implementation of feature flags. Instances of these flags are useful
to e.g. toggle certain (parts of) workflows in complex numerical experiments.

Authors:\n
- Philipp Schuette\n
"""
from dataclasses import dataclass
from logging import Logger


@dataclass
class FeatureFlag:
    "Simple implementation of a feature flag."
    name: str
    value: bool
    description: str
    logger: Logger
    timesAccessible: int = 1

    def __bool__(self) -> bool:
        # TODO: replace this with framework logging!
        self.logger.warning(
            "feature flag %s with value %s accessed!",
            self.name,
            str(self.value),
        )
        if self.timesAccessible != 0:
            self.timesAccessible -= 1
            return self.value
        self.logger.error("too many accesses to feature flag %s!", self.name)
        return False
