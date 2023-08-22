"""
Module providing named constants that identify types of implementations of the
abstract `FunctionSystem` base class.

Authors:\n
- Philipp Schuette\n
"""

from enum import Enum


class FunctionSystemType(Enum):
    "Enumeration identifying implementations of iterated function systems."
    HYPERBOLIC_CYLINDER = "HyperbolicCylinder"
    FLOW_CYLINDER = "FlowAdaptedCylinder"
    FUNNEL_TORUS = "FunnelTorus"
    GEOMETRIC_FUNNEL_TORUS = "GeometricFunnelTorus"
    FUNNEL_SURFACE = "FunnelSurface"
