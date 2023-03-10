#!/bin/bash

cd ..
echo "starting formatting, linting, type checking [and tests]..."
echo "--- use '--tests' to also run tests ---"
echo ""

echo "|-----------------------------------------------------------|"
echo "|[running black and isort on sources, tests, and benchmarks]|"
echo "|-----------------------------------------------------------|"
black src/
black tests/
isort src/
isort tests/
echo ""

echo "|--------------------------------------------------|"
echo "|[running flake8 on sources, tests, and benchmarks]|"
echo "|--------------------------------------------------|"
flake8 src/ \
    && flake8 tests/ \
    && echo "no linting errors with flake8!"
echo ""

echo "|-------------------------------------|"
echo "|[running pylint on tests and sources]|"
echo "|-------------------------------------|"
pylint src/ tests/
echo ""

echo "|------------------------------------------------|"
echo "|[running mypy on sources, tests, and benchmarks]|"
echo "|------------------------------------------------|"
export MYPYPATH=src \
    && mypy src/ --namespace-packages --explicit-package-bases \
    && mypy tests/ \
    && echo "type hints look good!"
echo ""

echo "|--------------------------------------------------------------|"
echo "|[running docstring coverage on sources, tests, and benchmarks]|"
echo "|--------------------------------------------------------------|"
docstr-coverage -p src/
docstr-coverage -p tests/
echo ""

if [[ "$1" == "--tests" ]]
then
    echo "|---------------------------|"
    echo "|[running tests with pytest]|"
    echo "|---------------------------|"
    pytest --cov=src/ --cov-report=html tests/
    echo ""
fi

echo "--> all done!"
