"""
TODO.

Author:\n
- Philipp Schuette\n
"""

import re


class PointCut:
    """
    Class representation of a point cut, i.e. point in time at which some
    advice may be applied.
    """

    __slots__ = ("pattern",)

    def __init__(self, pattern: str = ".*") -> None:
        """
        Initialize a new point cut from a given (method) name pattern.

        :param pattern: name pattern for selection of applicable methods
        """
        self.pattern = re.compile(pattern)

    def match(self, methodName: str) -> bool:
        """
        Determine whether a given runtime configuration matches this point cut.

        :param methodName: method to apply advice to
        :return: boolean flag indicate match status
        """
        return self.pattern.fullmatch(methodName) is not None
