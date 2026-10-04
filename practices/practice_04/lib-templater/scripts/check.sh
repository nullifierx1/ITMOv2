#!/usr/bin/env bash
set -euo pipefail

# Run from lib-templater root
cmake -S . -B build -G Ninja \
  -DBUILD_TESTS=ON \
  -DBUILD_BIN=OFF

cmake --build build

ctest --test-dir build --output-on-failure
