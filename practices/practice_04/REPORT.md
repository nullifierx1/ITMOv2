# Practice 4

## 1. Project

Исходный проект — `lib-templater`; рабочая копия находится в `practices/practice_04/lib-templater`. В рамках практики были выполнены две небольшие задачи: Feature A — рабочий scaffold GoogleTest/CTest, Feature B — public include layout, создаваемый bootstrap.

## 2. Configured environment

### AGENTS.md

`AGENTS.md` определяет scope Feature A/B, известные ограничения вне scope, порядок работы и основную проверку. Вне scope оставлены проблема `BUILD_BIN=ON`, несоответствие C++20/C++23 и настройка `BUILD_TESTS/BUILD_TESTING` в CI. Для изменений он требует прочитать связанные файлы и style guide, показать failing check, сделать минимальное исправление и выполнить проверку.

### Ready skill

Project-local skill `test-driven-development` добавлен из `obra/superpowers`. В него входят `SKILL.md` и `writing-good-tests.md`; OpenCode обнаруживал этот skill. На практике он задал последовательность RED → минимальный GREEN для обеих Feature и помог отделить проверяемое изменение от побочных правок.

### Context7 MCP

Context7 настроен в project-local `opencode.json`. Реальный tool `context7.query-docs` использовался для документации GoogleTest, CMake и OpenCode V2. Доступность сервиса не была постоянной: наблюдалась временная DNS-ошибка `ENOTFOUND`, позднее OpenCode снова показал `context7 connected`.

### Style guide

Style guide закрепляет четыре правила: сохранять текущий CMake layout и добавлять зависимости только по необходимости; проверять изменения через GoogleTest, CTest и runner; соблюдать `.clang-format` и `.editorconfig`; держать diff минимальным и не исправлять unrelated проблемы.

### Verification hook

В OpenCode 2.0.20 plugin `check-after-edit` создан через `Plugin.define`. Он подписывается на `execute.after`, реагирует на `write`, `edit` и `apply_patch`, а runner запускает через `node:child_process.spawn`. Hook добавляет к результату автоматический FAIL или PASS; отдельно были показаны FAIL с `EXPECT_TRUE(false)` и PASS после возврата `EXPECT_TRUE(true)`.

## 3. Feature A

На шаге RED `tests/CMakeLists.txt` ожидал `test_foo.cpp`, которого не было. Минимальный GREEN заменил source на `foo_ut.cpp` и добавил `Smoke.TrueIsTrue`. Итоговая проверка CTest: `1/1` PASS.

Commit: `688e90e fix(practice_04): repair test scaffold`.

## 4. Feature B

Работа выполнялась в отдельной рабочей копии на ветке `practice-04-b` в новой OpenCode-сессии. RED состоял в том, что `include/demo_lib/foo.h` отсутствовал; для этого был добавлен `tests/bootstrap_layout_test.py`. Минимальный GREEN перенёс `include/foo.h` в `include/__PROJECT_NAME__/foo.h`; менять `bootstrap.py` не потребовалось. После review subagent `@explore` ветка была fast-forward merged.

Commit: `bab8c4f fix(practice_04): fix generated include layout`.

## 5. HANDOFF

`docs/HANDOFF.md` фиксирует состояние проекта, основные исходники, команды проверки и ограничения. Новая OpenCode-сессия по `AGENTS.md` и `HANDOFF.md` правильно восстановила Feature A, Feature B, verification и out-of-scope ограничения.

Commit: `c5ec796 docs(practice_04): add project handoff`.

## 6. Own MCP

Собственный MCP называется `template-inspector`; его единственный tool — `template-inspector.template_inspect`. Это read-only проверка public include layout шаблона.

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

Ошибочный вызов с `projectName = ../bad` завершился со статусом `error` и вернул `Invalid projectName: expected a simple project identifier`. После него MCP server остался `connected`; tool не запускает bootstrap, Git или команды из пользовательского ввода и только читает состояние нужных файлов.

Commit: `dcb44db feat(practice_04): add template inspector MCP`.

## 7. Verification

Основной project runner — `sh scripts/check.sh`. В текущей Windows-среде `sh` не был доступен в PATH, поэтому финальная проверка была выполнена эквивалентными Windows-командами: CMake configure, CMake build, CTest и Python 3.12 `bootstrap_layout_test.py`. Feature A PASS; Feature B PASS.

## 8. Reflection

Краткий вывод: ограничения scope, test-first подход, отдельный MCP-tool и автоматический hook сделали изменения более проверяемыми и снизили риск затронуть unrelated код. Подробная студенческая рефлексия находится в [reflection.md](reflection.md).

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
