# Review — Practice 5, 2026-10-26

## Verdict

PASS для подготовки ретроспективного предложения: обязательные planning-артефакты существуют, согласованы между собой и покрывают исходные UI/Logic требования без добавления функций. Это документальный Review, не приёмка продукта и не подтверждение полного соответствия текущего кода требованиям. Эксперимент завершён до Apply; реализация уже была выполнена через Spec Kit.

Review выполнен вручную после Explore/Propose. В установленном наборе OpenSpec skills отдельного review skill нет, в `openspec --help` отдельной review-команды нет. Команда validate проверяет структуру и формат; полнота переноса и границы проверены дополнительно чтением документов и кода.

## Traceability

Имена в правой колонке — точные заголовки Requirement в `specs/practice-05/bootstrap-gui/spec.md` (G) либо `specs/practice-05/bootstrap-logic/spec.md` (L). Источники — три согласованных документа, ссылки в proposal.md.

| Источник | Покрытие в OpenSpec |
| --- | --- |
| UI FR-001–002 | G Single form and defaults |
| UI FR-003–004 | L Parameter validation, Independent API; G Preview rendering, Result and error recovery |
| UI FR-005 | G Preview rendering; L Ordered preview operations, Layout check and no writes |
| UI FR-006 | G Preview freshness |
| UI FR-007 | G Explicit confirmation; L Apply binding and failures |
| UI FR-008 | G Responsive operation states |
| UI FR-009 | G Result and error recovery |
| UI FR-010 | G Keyboard access |
| UI SC-001–005 | G demo preview, confirm/cancel, freshness, rendering; L Reproducible acceptance checks; tasks 3.1–4.1 |
| Logic FR-001 | L Independent API |
| Logic FR-002 | L Parameter validation; G Single form and defaults |
| Logic FR-003–004 | L Existing CLI and JSON behavior, включая приоритеты, coercion, пустой JSON namespace, конфликты и dry-run |
| Logic FR-005 | L Layout check and no writes |
| Logic FR-006 | L Ordered preview operations |
| Logic FR-007 | L Preserve bootstrap transformations |
| Logic FR-008 | L Apply binding and failures; G Explicit confirmation, Preview freshness |
| Logic FR-009–010 | L Apply binding and failures, Layout check and no writes; G Result and error recovery |
| Logic FR-011 | L Reproducible acceptance checks |
| Logic SC-001–004 | L no writes, четыре bin/examples-комбинации, ошибки и независимый API; tasks 1.1–2.2, 4.1–4.2 |
| Контракт: вход / Preview | L Independent API, Parameter validation, Ordered preview operations; G Preview rendering |
| Контракт: подтверждение / Apply | G Explicit confirmation, Preview freshness, Responsive operation states; L Apply binding and failures |
| Контракт: ошибки / границы / приёмка | G Result and error recovery; L Existing CLI and JSON behavior, Reproducible acceptance checks; design Goals / Non-Goals и Risks |

UI edge cases (возврат значения, длинные пути, блокировки/закрытие, частичные изменения) отражены в G и design. Logic edge cases (файлы структуры, JSON, конфликты, отсутствующие/существующие optional directories, ошибки I/O/Unicode) отражены в L; отсутствие гарантии повторной настройки и внешних правок — в design Risks. Предположения и исключения не превращены в новые функции.

## Consistency and findings

- Proposal перечисляет ровно две capabilities; обе имеют delta specs. ADDED означает добавление к пустому реестру OpenSpec, не изменение поведения продукта. Основные specs не создавались.
- Требования отделены от решений: Qt/QThread и таблицы будущего состояния объяснены в design; API остаётся внешним контрактом. В design нет неразрешённых вопросов, меняющих объём.
- Tasks следуют Logic → Apply/CLI → GUI → общей интеграции; каждый пункт содержит способ проверки, локальные тесты/документация включены в соответствующие группы. Все 10 задач не отмечены выполненными: OpenSpec не реализовывал фичу.
- При Review уточнены границы доказательств: в design Risks и tasks 2.2 явно отражены отклонения текущего кода/регрессии от строгого исторического равенства. `Bootstrapper._is_service_path` исключает specs/.specify/.agents, Python bootstrap-тесты и venv в API; `test_api_and_cli_match_baseline_except_cmake_fix` в bootstrap_cli_test.py нормализует старую цель tests/CMakeLists.txt. Поэтому текущий тест нельзя представлять как доказательство побайтовой совместимости без исключений. Нормативное требование Logic FR-007/SC-002 сохранено, код и исходные specs не исправлялись. Это наблюдение о существующем продукте, а не дефект согласованности proposal и не разрешение расширить эксперимент.
- Исторические статусы в исходных документах неоднородны: spec.md уже Approved v2, контракт ссылается на Draft v2, а существующий plan ещё упоминает ожидание приёмки. Использован явно заданный пользователем согласованный контракт; эти документы оставлены без изменений, новая человеческая приёмка не заявляется.
- Блокирующих пробелов в предложении по заданному объёму не найдено. Полное runtime-соответствие продукта не проверялось: приложения, bootstrap, Python-тесты и sh scripts/check.sh не запускались.

## Actual skills and CLI

Прочитаны и применены `.agents/skills/openspec-explore/SKILL.md` и `.agents/skills/openspec-propose/SKILL.md`. Отдельного исполняемого CLI `explore`/`propose` нет: это агентские workflows. Update/Apply/Sync/Archive skills не вызывались.

Реально выполненные команды OpenSpec (повторные status/list объединены):

```text
openspec --version
openspec --help
openspec list --json
openspec context --json
openspec list --specs --json
openspec validate --help
openspec new change practice-05-bootstrap-gui-retrospective
openspec status --change practice-05-bootstrap-gui-retrospective --json
openspec instructions proposal --change practice-05-bootstrap-gui-retrospective --json
openspec instructions specs --change practice-05-bootstrap-gui-retrospective --json
openspec instructions design --change practice-05-bootstrap-gui-retrospective --json
openspec instructions tasks --change practice-05-bootstrap-gui-retrospective --json
openspec status --change practice-05-bootstrap-gui-retrospective
openspec show practice-05-bootstrap-gui-retrospective --type change --json
openspec validate practice-05-bootstrap-gui-retrospective --type change --strict --json --no-interactive
```

Установлена версия 1.14.1, schema spec-driven. Первый list выполнен из корня и из lib-templater; оба разрешили существующий root ITMOv2. Остальные команды — из корня. Init и создание store не потребовались. Автоматическая подсказка CLI про instructions apply не выполнялась.

## Validation evidence

Строгая валидация change: valid=true, issues=[], passed=1, failed=0, exit code 0. CLI show распознал 15 deltas и 21 сценарий в двух capabilities. CLI status: 4/4 artifacts complete; isPlanningComplete=true. Поле isComplete=true этого status относится к готовности артефактов, не к выполнению задач. Сырые результаты повторной итоговой проверки сохраняются в validation.json и planning-status.json.

Дополнительная проверка завершена успешно: все 4 локальные Markdown-ссылки разрешаются, хвостовых пробелов нет, tracked diff и index diff пусты. В tasks — 10 невыполненных задач, 0 выполненных. Исходное состояние: единственный untracked путь `.vscode/settings.json`, он не менялся. Итоговый `git status --short`:

```text
?? .vscode/
?? openspec/changes/practice-05-bootstrap-gui-retrospective/
```

Созданы только 9 файлов внутри change: `.openspec.yaml`, `proposal.md`, `design.md`, `tasks.md`, `review.md`, `validation.json`, `planning-status.json` и две delta specs `specs/practice-05/bootstrap-gui/spec.md`, `specs/practice-05/bootstrap-logic/spec.md`.

## Comparison with GitHub Spec Kit

| Фактически наблюдавшийся аспект | OpenSpec в этом эксперименте | Существующие Spec Kit артефакты |
| --- | --- | --- |
| Организация | Один change с proposal, двумя capability deltas, design и tasks | Две feature specs UI/Logic, общий contract; единый plan/tasks под Logic |
| Исследование | Explore — чтение кода и требований без отдельного обязательного файла | Сохранены research.md, data-model.md, contracts/bootstrap-api.md, quickstart.md |
| Планирование | CLI выдаёт инструкции и зависимости артефактов, status показывает 4/4 | Plan фиксирует constitution check, технические решения и фазы, tasks — подробный план |
| Проверка | validate --strict проверил машинный формат, ручной Review добавил трассировку | Имеются requirements checklists и критерии приёмки в specs; CLI Spec Kit здесь не запускался |

В этой задаче OpenSpec дал компактный контейнер change и явную проверяемую схему; детализацию приёмки пришлось осознанно переносить из исходного контракта. Spec Kit хранит больше отдельных плановых документов и явно отражает constitution/согласование двух спецификаций. Сравнение ограничено документами и пройденным подготовительным циклом: скорость/качество реализации, Apply, Sync и Archive не сравнивались; исходный Spec Kit workflow в этом эксперименте не воспроизводился.
