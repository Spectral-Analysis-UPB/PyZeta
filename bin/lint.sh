#!/bin/bash

cd ..
echo "starting formatting, linting, type checking [and tests]..."
echo "--- use '--tests' to also run tests ---"
echo ""

echo "|-----------------------------------------------------------|"
echo "|[running black and isort on sources, tests, and benchmarks]|"
echo "|-----------------------------------------------------------|"
black pyzeta/
isort pyzeta/
echo ""

echo "|---------------------------------------------------|"
echo "|[running linters on sources, tests, and benchmarks]|"
echo "|---------------------------------------------------|"
pylama pyzeta/ && echo "no linting errors with pylama!"
pylint pyzeta/
echo ""

echo "|------------------------------------------------|"
echo "|[running mypy on sources, tests, and benchmarks]|"
echo "|------------------------------------------------|"
mypy pyzeta/ && echo "type hints look good!"
echo ""

echo "|--------------------------------------------------------------|"
echo "|[running docstring coverage on sources, tests, and benchmarks]|"
echo "|--------------------------------------------------------------|"
docstr-coverage -b docs/_static/ -p pyzeta/
echo ""

echo "|--------------------------|"
echo "|[validating json schemata]|"
echo "|--------------------------|"
check-jsonschema -v \
    --schemafile pyzeta/framework/feature_toggle/toggle_schema.json \
    pyzeta/tests/framework/feature_toggle/toggles.json
check-jsonschema -v \
    --schemafile pyzeta/framework/settings/json_settings/settings_schema.json \
    pyzeta/framework/settings/json_settings/default_settings.json
echo ""

if [[ "$1" == "--tests" ]]
then
    echo "|---------------------------|"
    echo "|[running tests with pytest]|"
    echo "|---------------------------|"

    PARALLEL=""
    shift

    while [[ "$#" -ge 1 ]]
    do
        if [[ "$1" == "--parallel" ]]
        then
            PARALLEL="-n auto"
        fi
        shift
    done

    pytest --cov=pyzeta/ --cov-report=html  $PARALLEL pyzeta/tests/
    echo ""
fi

echo "|-------------------------|"
echo "|[testing CLI entry point]|"
echo "|-------------------------|"
pyzeta --version
echo ""

echo "--> all done!"
