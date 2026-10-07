# Practice 4

## 1. Project

Исходный проект: `lib-templater`. Рабочая копия: `practices/practice_04/lib-templater`. Здесь выполнены две небольшие задачи: Feature A, рабочий scaffold GoogleTest/CTest; Feature B, public include layout, который создаёт bootstrap.

## 2. Configured environment

### AGENTS.md

В `AGENTS.md` зафиксированы scope Feature A/B, известные ограничения вне scope, порядок работы и основная проверка. За рамками задачи остались проблема `BUILD_BIN=ON`, расхождение C++20/C++23 и настройка `BUILD_TESTS/BUILD_TESTING` в CI. Перед изменениями нужно прочитать связанные файлы и style guide, показать failing check, внести минимальную правку и выполнить проверку.

### Ready skill

Project-local skill `test-driven-development` взят из `obra/superpowers`. В него входят `SKILL.md` и `writing-good-tests.md`; OpenCode находил этот skill. На практике он задал порядок RED → минимальный GREEN для обеих Feature и не дал смешать проверяемые изменения с побочными правками.

### Context7 MCP

Context7 задан в project-local `opencode.json`. В сохранённой OpenCode-сессии `ses_ef8264c1dffeHQPR6wW9ztAkcm` по теме GoogleTest зафиксированы завершённые вызовы `context7.query-docs`. Запрос с `libraryId` `/websites/cmake_cmake_help` — `gtest_discover_tests CMake GoogleTest module documentation with example` — вернул страницы [FindGTest](https://cmake.org/cmake/help/latest/module/FindGTest.html) и [GoogleTest](https://cmake.org/cmake/help/latest/module/GoogleTest.html), подтвердив, что `gtest_discover_tests` обнаруживает тесты из executable и регистрирует их в CTest; в ответе был пример `include(GoogleTest)` и `gtest_discover_tests(example)`. Второй завершённый запрос с `libraryId` `/websites/google_github_io_googletest` — `Googletest Primer minimal TEST and EXPECT_TRUE example` — вернул [GoogleTest Quickstart](https://google.github.io/googletest/quickstart-cmake.html) с минимальным примером `TEST(...)` и подключением `<gtest/gtest.h>`. Реальный tool также использовался при работе с документацией OpenCode V2. Сервис был доступен не всегда: возникала временная DNS-ошибка `ENOTFOUND`, а позже OpenCode снова показал `context7 connected`.

### Style guide

В style guide четыре правила: сохранять текущий CMake layout и добавлять зависимости только по необходимости; проверять изменения через GoogleTest, CTest и runner; соблюдать `.clang-format` и `.editorconfig`; держать diff небольшим и не трогать unrelated проблемы.

### Verification hook

Для OpenCode 2.0.20 plugin `check-after-edit` написан через `Plugin.define`. Он подписывается на `execute.after`, реагирует на `write`, `edit` и `apply_patch`, а runner запускает через `node:child_process.spawn`. Hook дописывает в результат автоматический FAIL или PASS. Отдельно были показаны FAIL с `EXPECT_TRUE(false)` и PASS после возврата `EXPECT_TRUE(true)`.

## 3. Feature A

На шаге RED `tests/CMakeLists.txt` ссылался на отсутствующий `test_foo.cpp`. Минимальный GREEN заменил source на `foo_ut.cpp` и добавил `Smoke.TrueIsTrue`. CTest прошёл: `1/1` PASS.

Commit: `688e90e fix(practice_04): repair test scaffold`.

## 4. Feature B

Работа шла в отдельной рабочей копии на ветке `practice-04-b` и в новой OpenCode-сессии. RED показал отсутствие `include/demo_lib/foo.h`; для проверки добавлен `tests/bootstrap_layout_test.py`. Минимальный GREEN перенёс `include/foo.h` в `include/__PROJECT_NAME__/foo.h`, `bootstrap.py` менять не потребовалось. После review subagent `@explore` ветка была fast-forward merged.

Commit: `bab8c4f fix(practice_04): fix generated include layout`.

## 5. HANDOFF

`docs/HANDOFF.md` собирает состояние проекта, основные исходники, команды проверки и ограничения. Новая OpenCode-сессия по `AGENTS.md` и `HANDOFF.md` правильно восстановила Feature A, Feature B, verification и out-of-scope ограничения.

Commit: `c5ec796 docs(practice_04): add project handoff`.

## 6. Own MCP

Собственный MCP называется `template-inspector`. В нём один tool: `template-inspector.template_inspect`. Он read-only проверяет public include layout шаблона.

Успешный вызов с `projectName = demo_lib` завершился со статусом `completed` и вернул:

```json
{
  "project_name": "demo_lib",
  "template_header": "include/__PROJECT_NAME__/foo.h",
  "expected_generated_header": "include/demo_lib/foo.h",
  "template_header_exists": true,
  "legacy_flat_header_exists": false,
  "template_ready": true
}
```

Ошибочный вызов с `projectName = ../bad` завершился со статусом `error` и вернул `Invalid projectName: expected a simple project identifier`. После него MCP server остался `connected`. Tool не запускает bootstrap, Git или команды из пользовательского ввода, он только читает состояние нужных файлов.

Commit: `dcb44db feat(practice_04): add template inspector MCP`.

## 7. Verification

Основной project runner: `sh scripts/check.sh`. В текущей Windows-среде `sh` не было в PATH, поэтому финальная проверка прошла эквивалентными Windows-командами: CMake configure, CMake build, CTest и Python 3.12 `bootstrap_layout_test.py`. Feature A PASS; Feature B PASS.

## 8. Reflection

Ограничения scope, test-first подход, отдельный MCP-tool и автоматический hook сделали изменения проще для проверки и снизили риск затронуть unrelated код. Подробная студенческая рефлексия: [reflection.md](reflection.md).

## 9. Commits

| Commit | Назначение |
| --- | --- |
| `d79bb24` | baseline import |
| `ae85dd3` | AGENTS + verification runner |
| `06a24d3` | TDD skill |
| `a2c46fb` | Context7 MCP |
| `688e90e` | Feature A |
| `14a288e` | style guide + hook |
| `bab8c4f` | Feature B |
| `c5ec796` | HANDOFF |
| `dcb44db` | own MCP |
