"""
Module containing an implementation of the orbit integral provider. This
method for integral calculation corresponds to Gaussian test functions constant
in the fiber coordinate of phase space which in terms of Ruelle distributions
is push-forward along the bundle projection.

Authors:\n
- Philipp Schuette\n
"""

from pyzeta.core.dynamics.function_systems.integral_provider import (
    IntegralProvider,
)


class FundamentalDomainIntegrals(IntegralProvider):
    """
    Class representation of orbit integrals w.r.t. weights on the fundamental
    domain and constant in the fiber.
    """
