# Шаблон C++ библиотеки

Это CMake-проект с установкой и поддержкой `find_package`. В шаблоне есть публичные заголовки, тесты GoogleTest/CTest, настройки стиля и GitHub Actions. Скрипт bootstrap задаёт имя проекта и namespace, выбирает стиль кода и настраивает необязательные `bin/` и examples.

## CLI: быстрая настройка

```bash
python tools/bootstrap.py project_name
```

Скрипт заменяет плейсхолдеры именем `project_name`, обновляет namespace и настройки стиля. Недостающие параметры он запрашивает в консоли. Аргументы, JSON-конфигурация и интерактивные вопросы сохранены.

Предварительный просмотр CLI без записи:

```bash
python tools/bootstrap.py project_name --dry-run
```

## Структура проекта

```txt
├─ include/project_name/   # Public API
├─ src/               # Library implementation
├─ bin/               # Executable (optional, for local testing)
├─ tests/             # Unit tests
├─ cmake/             # CMake modules (install, dependencies)
├─ tools/             # Bootstrap script
└─ CMakeLists.txt
```

## Сборка и C++ тесты

Требования текущего CMake-проекта:

```txt
- CMake ≥ 3.20
- C++ compiler with C++23 support for the current CMake settings
```

```bash
cmake -S . -B build -DBUILD_TESTS=ON -DBUILD_BIN=OFF
cmake --build build
```

В исходном шаблоне каталога `bin/` нет, поэтому для этой сборки указан `BUILD_BIN=OFF`. Обычная сборка неизменённого шаблона с `BUILD_BIN=ON` остаётся вне исправлений Practice 5.

```bash
ctest --test-dir build --output-on-failure
```

Тесты получают GoogleTest через `FetchContent`. При первом configure нужен доступ к источнику зависимости.

### Необязательная бинарная цель

Команда ниже относится к созданной и собранной бинарной цели. После сборки с `BUILD_BIN=OFF` такого исполняемого файла не будет.

```bash
./build/bin/main
```

В Windows путь к цели: `build/bin/main`.

### Установка и подключение библиотеки

```bash
cmake --install build --prefix /usr/local
```

```cmake
find_package(project_name CONFIG REQUIRED)

add_executable(app main.cpp)
target_link_libraries(app PRIVATE project_name::project_name)
```

Параметры CMake:

```cmake
BUILD_TESTS     # ON/OFF
BUILD_BIN       # ON/OFF
ENABLE_INSTALL  # ON/OFF
```

## GUI bootstrap: Practice 5

GUI проверен на Python 3.12 с PySide6 6.10.1 из [requirements-gui.txt](requirements-gui.txt). Logic и CLI достаточно стандартной библиотеки Python. Команды ниже нужно выполнять из этого каталога.

Windows PowerShell:

```powershell
python -m venv .venv-gui
.\.venv-gui\Scripts\python.exe -m pip install -r requirements-gui.txt
.\.venv-gui\Scripts\python.exe tools/bootstrap_gui.py
```

Linux/macOS:

```sh
python -m venv .venv-gui
.venv-gui/bin/python -m pip install -r requirements-gui.txt
.venv-gui/bin/python tools/bootstrap_gui.py
```

Форма определяет корень проекта по расположению приложения и показывает его без возможности редактирования. Пользователь задаёт имя проекта и namespace. Пустой namespace означает использование имени проекта. Начальные настройки: `google`, bin включён, examples выключены. EditorConfig соответствует выбранному стилю.

Preview показывает операции в порядке их выполнения и не меняет файлы. После изменения любого поля требуется новый Preview. Apply запускается только после подтверждения. Отмена или закрытие диалога сохраняет ввод и Preview, файлы не меняются.

GUI Preview и Apply используют один фильтр. Он сохраняет `specs/`, `.specify/`, `.agents/`, `tests/bootstrap_*_test.py` и локальные окружения Python: `.venv`, `.venv-*`, `venv`, а также каталоги с `pyvenv.cfg`. CLI продолжает прежний обход дерева. Оба способа запуска используют исправленную CMake-цель сгенерированной библиотеки. Если путь указан несколько раз, это последовательные этапы bootstrap. Такие операции не объединяются.

Preview и Apply работают в отдельном потоке. Пока операция выполняется, поля и кнопки заблокированы. Ошибка Apply может оставить частичные изменения. Перед повторной попыткой нужно проверить файлы. Автоматического отката и отмены работающей операции нет. Повторная настройка уже сгенерированного проекта не гарантируется, поэтому для демонстрации нужна свежая временная копия.

### Проверки Python

Logic и CLI проверяются в отдельном окружении без Qt:

```powershell
python -m venv .venv-logic
.\.venv-logic\Scripts\python.exe -B -m unittest discover -s tests -p bootstrap_logic_test.py -v
.\.venv-logic\Scripts\python.exe -B -m unittest discover -s tests -p bootstrap_cli_test.py -v
.\.venv-logic\Scripts\python.exe -B tests/bootstrap_layout_test.py
.\.venv-gui\Scripts\python.exe -B -m unittest discover -s tests -p bootstrap_gui_test.py -v
```

В Linux/macOS вместо `.venv-logic\Scripts\python.exe` и `.venv-gui\Scripts\python.exe` используются соответствующие пути `bin/python`. GUI-тестам нужны PySide6 и настоящий QApplication. Без дисплея можно задать `QT_QPA_PLATFORM=offscreen`. Для показа окна на рабочем столе эту настройку нужно убрать.

Сравнение CLI с baseline требует Git и коммит `b768cd8` в истории репозитория. Все тесты файловой генерации используют временные копии, не рабочий checkout.

### Проверки Practice 4

Общая команда проверки сохранена:

```sh
sh scripts/check.sh
```

Для неё нужны Linux/WSL, shell-скрипт с LF, Ninja, компилятор с поддержкой текущего C++23 и доступ к GoogleTest при первом configure. В проверенном Windows checkout скрипт имеет CRLF, а в WSL нет Ninja. Поэтому эквивалентные проверки выполнялись на временных копиях с Unix Makefiles:

```sh
cmake -S . -B build -G 'Unix Makefiles' -DBUILD_TESTS=ON -DBUILD_BIN=OFF
cmake --build build
ctest --test-dir build -N
ctest --test-dir build --output-on-failure
```

Эти команды нужно запускать и внутри сгенерированной временной библиотеки `demo_lib`. Проверка исходного шаблона не подтверждает, что цели сгенерированного проекта собираются.

<a id="short-desktop-demonstration"></a>

### Короткий сценарий демонстрации

Создать свежую копию и запустить её GUI через установленный интерпретатор. PowerShell, из этого каталога:

```powershell
$demoRoot = Join-Path ([IO.Path]::GetTempPath()) ('practice5-demo-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $demoRoot | Out-Null
foreach ($entry in @('tools', 'src', 'include', 'tests', 'cmake', 'specs', '.specify', '.agents', 'CMakeLists.txt', '.clang-format', '.editorconfig', '.gitignore', 'bin', 'examples')) {
    if (Test-Path -LiteralPath $entry) { Copy-Item -LiteralPath $entry -Destination $demoRoot -Recurse }
}
& .\.venv-gui\Scripts\python.exe (Join-Path $demoRoot 'tools/bootstrap_gui.py')
```

1. Проверить корень и начальные настройки. Ввести `123-lib`, запросить Preview, увидеть ошибку у поля и исправить имя на `demo_lib`.
2. Оставить namespace пустым. В Preview проверить эффективный namespace `demo_lib`, порядок операций, оба пути rename и отсутствие служебных файлов.
3. Открыть подтверждение и отменить его. Ввод и Preview должны сохраниться, файлы остаться прежними.
4. Подтвердить Apply. Проверить сводку успеха и `include/demo_lib/foo.h` в копии. Файла `include/foo.h` быть не должно. Служебные файлы должны сохранить исходные байты.
5. Для нового запуска взять свежую копию. В отдельном сценарии ошибки Apply проверить сообщение о возможных частичных изменениях и отсутствие сообщения об успехе.

Подробности: [итоговый отчёт](../REPORT.md), [результаты проверок](specs/002-bootstrap-logic/quickstart.md), [UI specification](specs/001-bootstrap-ui/spec.md), [Logic specification](specs/002-bootstrap-logic/spec.md) и [общий контракт](specs/contract.md).
