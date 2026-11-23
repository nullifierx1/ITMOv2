# Bootstrap Logic — retrospective delta

## Purpose

Описать согласованное независимое от GUI поведение bootstrap Practice 5: проверку, предпросмотр без записи и применение после подтверждения в UI. Ретроспективная регистрация в OpenSpec не меняет контракт Spec Kit и готовый продукт.

## ADDED Requirements

### Requirement: Independent API
Logic SHALL предоставлять `preview(root, settings)` и `apply(preview)` без PySide6, интерактивного ввода и завершения вызывающего приложения. Настройки API: project_name, namespace, codestyle, keep_bin, keep_examples; корень задаёт приложение, EditorConfig соответствует стилю.

#### Scenario: Call without GUI
- **WHEN** вызывающая программа без GUI-пакета передаёт корень и настройки
- **THEN** Preview, результат Apply и ошибки доступны как данные, без разбора печатного вывода и ручного ввода

### Requirement: Parameter validation
Logic SHALL проверять имя по `[A-Za-z][A-Za-z0-9_]*`, непустой namespace по `[A-Za-z_][A-Za-z0-9_]*(::[A-Za-z_][A-Za-z0-9_]*)*`, без trim и новой проверки ключевых слов C++. Пустой namespace GUI означает имя; стили только chromium/google/llvm/microsoft/mozilla/webkit, default google; keep_bin=true, keep_examples=false.

#### Scenario: Effective settings
- **WHEN** переданы demo_lib и пустой namespace с defaults
- **THEN** Preview содержит namespace demo_lib, google, bin=true, examples=false

#### Scenario: Invalid field
- **WHEN** имя пустое, пробельное, 9demo или с краевыми пробелами, namespace demo:::lib либо стиль неизвестен
- **THEN** возвращена ошибка validation с message и field до записи, без автоматического исправления

### Requirement: Layout check and no writes
Preview SHALL до применения проверять CMakeLists.txt, src/CMakeLists.txt, tests/CMakeLists.txt, cmake/__PROJECT_NAME__Config.cmake.in и перечислять отсутствующие относительные пути. Валидация и Preview не создают, не меняют, не перемещают и не удаляют файлы/каталоги проекта, включая временные файлы.

#### Scenario: Missing template or read failure
- **WHEN** файл шаблона отсутствует, не читается либо не декодируется
- **THEN** ошибка preview сообщает причину и применимый path, отсутствующие пути перечислены, дерево и содержимое неизменны

### Requirement: Ordered preview operations
Preview SHALL возвращать root, эффективные settings и упорядоченные operations с kind=create/update/rename/delete, target_kind=file/directory, относительным path и new_path только для rename. Список учитывает последовательное действие преобразований; delete каталога включает содержимое без обязательного перечисления вложенных файлов.

#### Scenario: Repeat and sequential effects
- **WHEN** Preview повторяется на неизменном шаблоне с теми же настройками
- **THEN** набор действий одинаков, последующие операции учитывают ранее подготовленные изменения; rename содержит оба пути, diff и тексты файлов не требуются

### Requirement: Preserve bootstrap transformations
Apply SHALL сохранять порядок и состав преобразований: .clang-format → .editorconfig → добавление недостающих .vscode/ и .idea/ в .gitignore → замены обозначений → tests/CMakeLists.txt → переименование config/include → bin → examples. Существующие заготовки, перезаписи, набор текстовых файлов, исключения и правила CMake-блоков сохраняются без новых исправлений генератора.

#### Scenario: Apply demo library and optional targets
- **WHEN** на неизменном шаблоне применён Preview для demo_lib с любой из четырёх комбинаций bin/examples
- **THEN** действия соответствуют Preview и прежнему bootstrap с теми же итоговыми настройками; существует include/demo_lib/foo.h, отсутствует include/foo.h; включённые цели используют заготовки, существующие отключённые каталоги удалены с содержимым, отсутствующие не удаляются

### Requirement: Apply binding and failures
`apply(preview)` SHALL использовать root/settings успешного Preview без отдельных настроек и возвращать краткую сводку при успехе. Первый сбой останавливает выполнение; ошибки содержат stage=validation/preview/apply, message и применимые field/path. Структура/чтение при Preview имеют stage=preview, ошибки выполнения — apply; ошибки параметров содержат field.

#### Scenario: Write rename or delete failure
- **WHEN** подтверждённое применение встречает ошибку чтения, декодирования, записи, rename либо delete
- **THEN** последующие действия прекращены, ошибка apply доступна структурированно с применимым path; частичные изменения возможны, подробный учёт необязателен

### Requirement: Existing CLI and JSON behavior
CLI SHALL сохранять позиционное имя, --namespace, --codestyle, --editorconfig, --keep-bin/--no-bin, --keep-examples/--no-examples, --config, --dry-run, прежние вопросы и defaults, без нового подтверждения. JSON остаётся объектом существующих настроек; ошибки конфигурации доступны структурированно до записи.

#### Scenario: Priorities and coercions
- **WHEN** совместно заданы CLI и JSON
- **THEN** непустая явная строка имеет приоритет над конфигурацией, имена конфигурации преобразуются в строки, keep_* — по прежней истинности; явные bin/examples флаги приоритетнее JSON, противоположные флаги дают конфликт, неизвестные JSON-ключи игнорируются, dry_run задаётся CLI

#### Scenario: Interactive and invalid configuration
- **WHEN** имя или namespace отсутствуют либо JSON отсутствует на диске, повреждён или не объект
- **THEN** при неполных настройках сохраняются прежние вопросы с предложенным именем для namespace; пустой namespace из JSON невалиден; неверный JSON даёт ошибку до записи

#### Scenario: Dry run and regression
- **WHEN** выполнен --dry-run либо прежний CLI layout-сценарий
- **THEN** dry-run не пишет, обычный CLI не запрашивает нового подтверждения и сохраняет ожидаемый include-layout

### Requirement: Reproducible acceptance checks
Проверки SHALL покрывать Logic без Qt, GUI с настоящим PySide6 (demo_lib, неверный параметр, отказ без Apply/записи) и регрессию CLI. Все проверки записи используют отдельные копии шаблона; существующие bootstrap layout test и sh scripts/check.sh сохраняют назначение и должны проходить без несвязанных исправлений.

#### Scenario: Isolated acceptance
- **WHEN** выполняется приёмочный набор
- **THEN** рабочий шаблон не является целью записи, Preview/отказ/ошибка проверки оставляют копии неизменными, четыре комбинации bin/examples сопоставлены прежнему bootstrap, ошибки не обозначены успехом
