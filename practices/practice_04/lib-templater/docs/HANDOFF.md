# Practice 4 handoff

## Current state

- Feature A completed:
  working GoogleTest/CTest scaffold.
- Feature B completed:
  bootstrap generates public header under
  include/<project_name>/.
- Project verification is GREEN.

## Main sources

- AGENTS.md
- docs/style-guide.md
- scripts/check.sh
- tests/foo_ut.cpp
- tests/bootstrap_layout_test.py
- tools/bootstrap.py

## Verification

Одна команда:

sh scripts/check.sh

Она проверяет:
- CMake configure/build;
- GoogleTest через CTest;
- bootstrap public include layout.

## Agent environment

- OpenCode 2.0.20.
- project skill:
  test-driven-development.
- Context7 MCP configured.
- check-after-edit plugin запускает verification
  после file-changing tools.

## Constraints

- BUILD_BIN=ON baseline issue remains OUT OF SCOPE.
- C++20/C++23 inconsistency remains OUT OF SCOPE.
- CI BUILD_TESTS/BUILD_TESTING inconsistency remains OUT OF SCOPE.
- Не исправлять unrelated issues без отдельного поручения.

## Completed workflow

Кратко:
- Feature A: RED → GREEN.
- Style guide + automatic hook: demonstrated FAIL/PASS.
- Feature B: separate worktree, RED → GREEN,
  subagent review, fast-forward merge.
