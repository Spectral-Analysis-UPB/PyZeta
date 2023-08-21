This is the documentation of the **PyZeta** project, welcome!

This numerical open source project implements a variety of different functionality centered around classical Pollicott-Ruelle,
semiclassical, and quantum resonances for **chaotic** dynamical systems.
Concrete examples for the latter are convex obstacle scattering systems but also convex-cocompact hyperbolic surfaces.
The resonances themselves have many interesting and important applications for example in decay of correlations, quantum-classical
correspondence, convergence to equilibrium, or control theory.

Work on **PyZeta** began as part of a PhD thesis [Sch2023]_ on *weighted zeta functions* for
*invariant Ruelle distributions* but has since extended its scope to pretty much any resonance related numerical methods.
The name **PyZeta** derives from the ubiquitous use of *zeta functions* to calculate both
resonances as well as other resonance related data. These zetas are generally *holomorphic*
or *meromorphic* functions

.. math::
   :nowrap:

   \begin{equation}
      \zeta: \mathbb{C} \rightarrow \mathbb{C}
   \end{equation}


which encode some interesting dynamical quantities in their zeros or poles. For an overview over the underlying
mathematical theory as well as links to the original publications giving precise definitions and theorems see :ref:`theory`.

.. note::

    This is an ongoing project. Any contributions such as feature requests, bug reports, or
    collaborations on documentation, theoretical background, or practical implementation are
    much appreciated!

-------------------------------

.. [Sch2023] Schuette, Philipp. Invariant Ruelle Distributions on Open Hyperbolic Systems -- An Analytical and Numerical Investigation. PhD Thesis (2023)
