"""
Static convenience class for reading and displaying profiling statistics. This
module is a (very thin) wrapper around the pstats standard library module.

TODO: enhance the possibilities in this module!

Author:\n
- Philipp Schuette\n
"""

from pstats import Stats


class StatsReader:
    "Static reader class for display of profiling statistics."

    @staticmethod
    def printStats(filename: str) -> None:
        """
        Print statistics from a given .cprofile file.

        :param filename: filename to extract and print statistics from
        """
        stats = Stats(filename)
        stats.strip_dirs().sort_stats("tottime").print_stats()
