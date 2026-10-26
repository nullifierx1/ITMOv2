# Practice 5: Spec Kit, GUI bootstrap и ретроспектива OpenSpec

## Почему выбрали Spec Kit

Для основной работы выбрали GitHub Spec Kit. В практике требовались две независимые спецификации, согласованный контракт до кода и проверяемая реализация. [Constitution](lib-templater/.specify/memory/constitution.md), feature specs, plan и tasks закрепили эти условия в репозитории. Поэтому Spec Kit подходил под задачу. Преимущество в скорости разработки этот эксперимент не проверял.

UI Team и Logic Team работали в двух независимых чатах Codex. UI Team описала форму и её состояния, Logic Team задала параметры, файловые эффекты и совместимость CLI. Сохранены [UI spec](lib-templater/specs/001-bootstrap-ui/spec.md) и [Logic spec](lib-templater/specs/002-bootstrap-logic/spec.md). До кода человек согласовал [общий контракт](lib-templater/specs/contract.md) и принял v2.

Порядок работы виден в Git. Коммит `9944241` содержит constitution, `4a82ff2` сохраняет независимые v1, `b768cd8` согласует их через контракт, а `35feb7d` отмечает Approved v2. Затем появились [plan](lib-templater/specs/002-bootstrap-logic/plan.md) и проектирование в `3e201d3`, [26 задач](lib-templater/specs/002-bootstrap-logic/tasks.md) в `7f2d025`, код и регрессии в `9d8bca3`, `ef65744` и тестовых коммитах. Самой переписки чатов в Git нет, сохранены её результаты.

## Что выполнили в двух workflow

| Аспект | GitHub Spec Kit | OpenSpec |
| --- | --- | --- |
| Этапы | Constitution → Specify/согласование → Plan → Tasks → Implement → проверки и документация | Explore → Propose → документальный Review → Validate |
| Артефакты | Две specs, контракт, [research](lib-templater/specs/002-bootstrap-logic/research.md), [data model](lib-templater/specs/002-bootstrap-logic/data-model.md), plan/tasks/checklists | Один change с [proposal](../../openspec/changes/practice-05-bootstrap-gui-retrospective/proposal.md), двумя capability delta specs, design, tasks и [review](../../openspec/changes/practice-05-bootstrap-gui-retrospective/review.md) |
| Проверка | Критерии приёмки, test-first и тесты работающего приложения | `validate --strict`: [valid=true, issues=[], 1 passed](../../openspec/changes/practice-05-bootstrap-gui-retrospective/validation.json). При документальном Review дополнительно сопоставлены требования |
| Результат | Реализованный и протестированный GUI | [4/4 planning-артефакта готовы](../../openspec/changes/practice-05-bootstrap-gui-retrospective/planning-status.json), 10 задач не выполнены |

OpenSpec 1.14.1 использовался ретроспективно только до Review/Validate, без Apply. Sync и Archive тоже не выполнялись. Proposal появился после реализации и не служил её основанием. `isComplete=true` в status означает готовность документов для планирования, а не готовность продукта. Review провели чтением документов, отдельную CLI-команду для него не запускали. Приложение и тесты в эксперименте OpenSpec не запускались.

В эксперименте OpenSpec собрал изменение в одном change и проверил его формат. В Spec Kit осталось больше отдельных проектных документов, связанных с constitution. По этим материалам можно сравнить подготовку и проверку документов. Скорость и качество реализации через OpenSpec оценивать нельзя: Apply не выполнялся.

## Что получилось и как проверили

[GUI](lib-templater/tools/bootstrap_gui.py) содержит одну форму PySide6 с фиксированным root, именем/namespace, шестью стилями и настройками bin/examples. Сценарий работы: Preview без записи → подтверждение → один Apply → результат. При изменении поля Preview сбрасывается. Ошибки показаны у полей, работа идёт в QThread, действия блокируются, а закрытие откладывается до завершения операции. Независимые `preview()`/`apply()` находятся в [bootstrap.py](lib-templater/tools/bootstrap.py). CLI/JSON/вопросы/dry-run сохранены.

Ручная проверка выявила две проблемы. Пользователь заметил, что Preview затрагивает служебные файлы и дважды указывает `tests/CMakeLists.txt`. Повторные записи отражают последовательные этапы, но второй этап раньше возвращал ошибочную CMake-цель. Ссылку исправили, а для GUI/API добавили общий фильтр служебных путей. CLI сохраняет прежний обход. Сравнение с baseline учитывает конкретное исправление CMake, поэтому полного исторического равенства без исключений не заявляем.

Проверки выполнены 2026-10-26. HEAD до документационных правок: `6cf7126`. Среда: Windows 11, Python 3.12.0, [PySide6/Qt 6.10.1](lib-templater/requirements-gui.txt).

| Проверка | Результат |
| --- | --- |
| [Logic](lib-templater/tests/bootstrap_logic_test.py) / [CLI](lib-templater/tests/bootstrap_cli_test.py), отдельная среда без Qt | 16 / 15 PASS |
| [GUI QtTest](lib-templater/tests/bootstrap_gui_test.py) | 13 PASS с desktop-плагином `windows`, ранее тот же набор прошёл с `offscreen` |
| [Layout](lib-templater/tests/bootstrap_layout_test.py) | PASS |
| Сгенерированный `demo_lib`, BUILD_TESTS=ON, BUILD_BIN=OFF, временная копия WSL | configure/build/CTest PASS, обнаружен и выполнен `Smoke.TrueIsTrue` |

Тесты проверяют сохранность служебных файлов после GUI Apply, совпадение всей последовательности Preview с реальными действиями, отказ без записи, ошибки I/O, отзывчивость и четыре сочетания bin/examples. Команды и версии записаны в [результатах проверок](lib-templater/specs/002-bootstrap-logic/quickstart.md). QtTest прошёл desktop-сценарии с настоящими окнами. Полное повторное ручное прохождение человеком после исправлений отдельно не подтверждено.

## Ограничения и демонстрация

В WSL нет Ninja, а `scripts/check.sh` в Windows checkout имеет CRLF. Скрипт не меняли. Эквивалентные проверки прошли с Unix Makefiles, CMake 3.28.3 и GCC 13.3.0. Обычный BUILD_BIN=ON исходного шаблона, расхождение C++20/C++23 и CI остались вне объёма работы. Автоматического отката нет. Ошибка Apply может оставить частичные изменения, повторная настройка сгенерированного проекта не гарантируется.

Для демонстрации нужна свежая временная копия. По [инструкции README](lib-templater/README.md#short-desktop-demonstration) запустить её GUI, проверить root/defaults, ввести неверное имя и исправить его на `demo_lib`. Оставить namespace пустым и запросить Preview. Сначала отменить подтверждение и проверить неизменность файлов. Затем подтвердить Apply и проверить summary, `include/demo_lib/foo.h` и сохранность служебных файлов. Все преобразования выполнялись на временных копиях, рабочий шаблон через bootstrap не изменялся.
