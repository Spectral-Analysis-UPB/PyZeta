#!/bin/bash

# remove caches and logs from bin/
rm -rf logs/
rm -rf __pycache__

# change to project root
cd ..

# remove pytest related stuff in project root
rm -rf .mypy_cache
rm -rf .pytest_cache
if [[ -f ".coverage" ]]; then rm .coverage; fi
rm -rf htmlcov

# remove  __pycache__ directories recursively starting with project root
find . -name __pycache__ -type d -exec rm -rf {} \; 2>/dev/null

# remove logs directories recursively starting with project root
find . -name logs -type d -exec rm -rf {} \; 2>/dev/null

# remove .hypothesis directories recursively starting with project root
find . -name .hypothesis -type d -exec rm -rf {} \; 2>/dev/null

# remove documentation build artifacts
rm -rf docs/_build/html/
rm -rf docs/_build/doctrees/
rm -rf docs/_build/pdf/
rm docs/faq/myclass_method1.cprofile

# remove python build artifacts
rm -rf dist/
rm -rf ./build/
rm -rf pyzeta/*.egg-info/
rm -rf *.egg-info/
