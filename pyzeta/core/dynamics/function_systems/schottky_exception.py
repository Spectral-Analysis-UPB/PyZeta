"""
Custom exception to be raised whenever a request concerning Schottky surfaces
cannot be satisfied.

Authors:\n
- Philipp Schuette\n
"""


class InvalidSchottkyException(Exception):
    "Raised when a request for a Schottky surface can't be satisfied."

    def __str__(self) -> str:
        "Simple string representation of a Schottky related exception."
        return f"Can't create Schottky surface from {self.args[0]}"
