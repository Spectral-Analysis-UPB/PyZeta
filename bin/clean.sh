#!/bin/bash

# remove logs in bin/
rm -rf logs/

# change to project root
cd ..

# remove pytest related stuff in project root
rm -rf .mypy_cache
rm -rf .pytest_cache
if [[ -f ".coverage" ]]; then rm .coverage; fi
rm -rf htmlcov

# remove all __pycache__ directories
rm -rf pyzeta/__pycache__
rm -rf pyzeta/*/__pycache__
rm -rf pyzeta/*/*/__pycache__
rm -rf pyzeta/tests/__pycache__
rm -rf pyzeta/tests/*/__pycache__
rm -rf pyzeta/tests/*/*/__pycache__

# remove all logging directories
rm -rf logs/
rm -rf pyzeta/logs
rm -rf pyzeta/*/logs
rm -rf pyzeta/*/*/logs
rm -rf pyzeta/tests/logs
rm -rf pyzeta/tests/*/logs

# remove documentation build artifacts
rm -rf docs/_build/html/
rm -rf docs/_build/doctrees/
rm -rf docs/_build/pdf/

# remove python build artifacts
rm -rf dist/
rm -rf ./build/
rm -rf pyzeta/*.egg-info/
rm -rf *.egg-info/
rm -rf .hypothesis/
rm -rf pyzeta/*/.hypothesis/
rm -rf pyzeta/tests/.hypothesis/
rm -rf pyzeta/tests/*/.hypothesis/
