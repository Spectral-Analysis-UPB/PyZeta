"""
Module `toggle_exception.py` from the framework portion of `PyZeta`.

This module contains a generic exception signaling that something went wrong
with the configuration of a feature toggle.

Authors:\n
- Philipp Schuette\n
"""


class ToggleException(Exception):
    """
    This exception should be raised if invalid configurations are encountered
    during registration/resolving of services from an IoC Container.
    """

    def __init__(self, msg: str) -> None:
        """
        Initialize a new `ToggleException` exception.

        :param msg: error message
        """
        super().__init__("[feature toggle] " + msg)
