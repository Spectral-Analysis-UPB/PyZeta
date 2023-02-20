==============
PyZeta Project
==============

.. image:: https://img.shields.io/badge/Language-Python-blue.svg
   :target: https://www.python.org/

.. image:: http://img.shields.io/badge/benchmarked%20by-asv-blue.svg?style=flat
   :target: https://github.com/Spectral-Analysis-UPB/PyZeta

.. image:: https://img.shields.io/github/v/release/Spectral-Analysis-UPB/PyZeta
   :target: https://github.com/Spectral-Analysis-UPB/PyZeta

.. image:: https://readthedocs.org/projects/pyzeta/badge/?version=latest
   :target: https://pyzeta.readthedocs.io/en/latest/?badge=latest

.. image:: https://github.com/Spectral-Analysis-UPB/PyZeta/workflows/build/badge.svg
   :target: https://github.com/Spectral-Analysis-UPB/PyZeta/actions

.. image:: https://codecov.io/gh/Spectral-Analysis-UPB/PyZeta/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/Spectral-Analysis-UPB/PyZeta

.. image:: https://img.shields.io/badge/docs-docstr--cov-success
   :target: https://pypi.org/project/docstr-coverage/

.. image:: https://img.shields.io/badge/mypy-checked-blue
   :target: https://mypy.readthedocs.io/en/stable/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

.. contents:: Contents
  :depth: 2

--------------------------------------------------------------------------------

------------
Introduction
------------

*PyZeta* is a numerical project written (mostly) in Python. It aims at providing
an easy to use interface for the calculation of Pollicott-Ruelle resonances of the
geodesic flow on *convex cocompact hyperbolic surfaces*, i.e. *Schottky surfaces*.
It is planned to provide resonance calculation tools for scattering systems in
the future.

The implementation of these facilities heavily relies on the connection between
resonances and zeros of *dynamical zeta functions*. The latter are numerically
tractible in the settings mentioned above because of the availability of symbolic
dynamics and a technique known as cycle expansion.

The PyZeta project allows its user to generate resonance plots for illustration in
papers or talks. Furthermore it is capable of calculating so-called weighted zeta
functions which allow a more indepth investigation of resonance structures via certain
generalized densities in phase space called *invariant Ruelle distributions*.

Any resonance related contributions of code or feature requests are welcome!


----------------
Project Features
----------------

At the moment the following features are available:

- several functions and classes for the calculation and visualisation of geometric
  quantities of hyperbolic geometry (module **hypgeo**)
- class representations of the following Schottky surfaces: *hyperbolic cylinder*,
  *funneled torus*, *n-funnel surface* (module **ifs**)
- an abstract base class for custom implementations of hyperbolic surfaces (module **ifs**)
- two different implementations of rootfinding algorithms for holomorphic functions
  in one variable based on the argument principle (module **rootfinder**)
- calculation of quantum mechanical resonances for hyperbolic surfaces (module **zeta**)
- calculation of classical resonances for the geodesic flow on hyperbolic surfaces,
  which for Schottky surfaces coincides with the quantum resonances spectrum by
  the quantum-classical correspondence (module **wzeta**)
- a browser based resonance viewer that allows you to select subsets of resonances
  according to your requirements for future applications in e.g. invariant Ruelle
  distribution calculations (module **selector**)
- calculation of invariant Ruelle distributions for the geodesic flow on hyperbolic
  surfaces (module **wzeta**)

Comprehensive coverage of all modules and an introduction to the mathematics and
numerical methods can be found on `ReadTheDocs <https://pyzeal.readthedocs.io/en/latest//>`_.
We also provide hints to the original maths and physics literature. As part of
the documentation we provide interactive *Jupyter notebooks* which could e.g. serve
as the starting point for your own *PyZeta* based research or applications.


------------
Installation
------------

If you have *Cython* installed, you can simply install this project via pip:

.. code:: bash

   $ pip install pyzeta

If you don't have a local version of *Cython* you need to install it first:

.. code:: bash

   $ pip install cython
   $ pip install pyzeta

Alternatively you can clone this repository, change into the newly created directory
and install it via the following commands (which also installs all dependencies
required for development):

.. code:: bash

   $ pip install cython
   $ pip install -e .[dev]


------------
Requirements
------------

The core (non-development) requirements for this project include some exceedingly
popular numerics packages: *numpy*, *scipy*, *matplotlib*. Furthermore we require
*cython* and rely heavily on *numba* for performance optimization. Finally we use
*bokeh* to build and run our browser based visualisation tool *selector.py*.


===============
Getting Started
===============

There are several straight forward ways to get started with PyZeta, depending on
what you want to do:


-----
Tests
-----

The PyZeta project contains a comprehensive test suite for all modules mentioned
above. While the tests are an integral part of our continuous integration pipeline,
you can just as well run the tests yourself, e.g. to verify your local installation:

.. code:: bash

   $ pytest test/
