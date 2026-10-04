#!/usr/bin/env bash
# Portable strict mode without pipefail for some shells
set -eu

# Run from lib-templater root
cmake -S . -B build -G Ninja \
  -DBUILD_TESTS=ON \
  -DBUILD_BIN=OFF

cmake --build build

ctest --test-dir build --output-on-failure

# Feature B: bootstrap layout test (use Python in WSL)
/usr/bin/python3 tests/bootstrap_layout_test.py
