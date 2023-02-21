#!/bin/bash

if [ "$1" = "--details" ]; then
    sloccount --wide --details ../src/ ../tests/
else
    sloccount --wide ../src/ ../tests/
fi
