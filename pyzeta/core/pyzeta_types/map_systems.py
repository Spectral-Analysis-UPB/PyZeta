"""
Module map_systems.py from the package PyZeta.
TODO.

Authors:\n
- Philipp Schuette\n
"""

from enum import Enum


class MapSystemType(Enum):
    "Enumeration identifying implementations of hyperbolic map systems."
    HYPERBOLIC_CYLINDER = "HyperbolicCylinder"
    FLOW_CYLINDER = "FlowAdaptedCylinder"
    FUNNEL_TORUS = "FunnelTorus"
    GEOMETRIC_FUNNEL_TORUS = "GeometricFunnelTorus"
    FUNNEL_SURFACE = "FunnelSurface"
