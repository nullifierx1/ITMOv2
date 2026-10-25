# Project

- C++ library template.
- CMake >= 3.20.
- Source: src/
- Public headers: include/
- Tests: tests/
- Bootstrap tool: tools/bootstrap.py.
- Style sources:
  .clang-format
  .editorconfig

# Practice 4 scope

Feature A — working test scaffold.

При BUILD_TESTS=ON и BUILD_BIN=OFF:
- CMake должен ссылаться только на существующие test sources;
- configure/build должны проходить;
- CTest должен обнаруживать минимум один smoke test.

Feature B — generated public include layout.

После bootstrap для project_name=demo_lib:
- публичный header должен находиться в
  include/demo_lib/foo.h;
- структура должна соответствовать README;
- не оставлять public header в include/foo.h.

# Known baseline issue outside scope

Обычный BUILD_BIN=ON сейчас падает,
потому что CMake ожидает отсутствующий bin/.

Не исправлять это в рамках A или B.

Также не исправлять без отдельного поручения:
- C++20/C++23 inconsistency;
- BUILD_TESTS/BUILD_TESTING в CI;
- прочие unrelated issues.

# Workflow

- Перед изменением читать относящийся код и проверки.
- Перед изменением кода прочитать docs/style-guide.md
  и соблюдать его правила.
- Для Feature A/B использовать test-first workflow.
- Сначала показать failing check.
- Затем минимальное исправление.
- Не делать unrelated refactoring.
- Не менять публичный контракт или зависимости без причины.
- Не делать commit без приёмки пользователя.

# Verification

Основная проверка Practice 4 должна запускаться
одной командой:

sh scripts/check.sh
