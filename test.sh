#!/bin/bash
# Flexible script to run Python SDK tests with Docker

# Change to the root directory before running Docker commands
cd "$(dirname "$0")"

# Check if demo.ogg exists and download if needed
if [ ! -f "tests/data/demo.ogg" ]; then
    echo "Downloading demo.ogg test file..."
    mkdir -p tests/data
    curl -o tests/data/demo.ogg https://music.ai/demo.ogg
fi

# Process command line arguments
if [ $# -gt 0 ]; then
    # If arguments are provided, run specific tests
    docker-compose -f tests/docker/docker-compose.test.yml run --rm python-sdk-tests $*
    exit $?
else
    # If no arguments are provided, build and run all tests
    docker-compose -f tests/docker/docker-compose.test.yml up --build
    exit $?
fi
