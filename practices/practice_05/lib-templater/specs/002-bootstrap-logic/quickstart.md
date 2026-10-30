# Quickstart: проверка Practice 5 после реализации

Реализация и проверки завершены; результаты и границы доказательств записаны ниже. Контракт: [UI ↔ Logic](../contract.md); Python binding: [bootstrap-api.md](contracts/bootstrap-api.md); данные: [data-model.md](data-model.md). Инструкция копирования и запуска GUI — в [README](../../README.md#short-desktop-demonstration).

## Среда

Python 3.12; для GUI — PySide6 из [requirements-gui.txt](../../requirements-gui.txt). Для Practice 4: Linux/WSL, sh, CMake >= 3.20, Ninja, C++ compiler и возможность получить GoogleTest при первом configure. Не менять текущий C++ standard или CI ради подготовки среды.

Все команды выполняются из корня lib-templater. Запись при проверках — только в отдельных копиях шаблона. Автотесты используют TemporaryDirectory и копируют нужные template-файлы по примеру bootstrap_layout_test; виртуальные окружения и build-output в fixture не включаются.

## 1. Независимость Logic и совместимость CLI

В отдельной среде без PySide6, установка зависимостей не нужна:

```sh
python -m venv .venv-logic
.venv-logic/bin/python -m unittest discover -s tests -p 'bootstrap_logic_test.py' -v
.venv-logic/bin/python -m unittest discover -s tests -p 'bootstrap_cli_test.py' -v
.venv-logic/bin/python tests/bootstrap_layout_test.py
```

В Windows использовать `.venv-logic/Scripts/python.exe` вместо `.venv-logic/bin/python`. Ожидается успешный прогон без Qt и без консольного ввода тестирующего человека.

| Проверка | Наблюдаемый результат |
| --- | --- |
| demo_lib, пустой namespace | эффективный namespace=demo_lib; root/settings/operations доступны |
| повторный Preview | тот же состав и порядок операций на неизменённом шаблоне |
| Snapshot до/после Preview | совпадают относительные пути, типы и байты файлов; ничего не создано/перемещено/удалено |
| Последовательные этапы | более поздние чтения видят ранее подготовленный текст; родители, rename и несколько update отражены в порядке действий |
| Неверные имя/namespace/style | validation с field и правилом, без записи |
| Нет обязательных файлов | preview с перечнем отсутствующих относительных путей, без записи |
| Ошибка чтения/декодирования | preview с причиной/path, без записи |
| apply(preview) | summary; include/demo_lib/foo.h существует, include/foo.h отсутствует |
| Сбой записи/rename/delete | apply с причиной/path, следующие действия не выполняются; успех не возвращается |

Ошибки доступа воспроизводить управляемым fault injection в unittest.mock: права ОС недостаточно переносимы. Непустой Preview проверять и на копии с существующим bin/examples, чтобы deletion действительно присутствовал.

Для четырёх комбинаций bin/examples [CLI-тест](../../tests/bootstrap_cli_test.py) сравнивает деревья и байты нового API, нового CLI и baseline `b768cd8` на одинаковых минимальных копиях. Исключён только файл самого скрипта `tools/bootstrap.py`; ожидаемое содержимое `tests/CMakeLists.txt` отличается ровно согласованной заменой `__PROJECT_NAME__::__PROJECT_NAME__` на `demo_lib::demo_lib`. Весь CMake-файл из сравнения не исключается. Служебные файлы проверяются отдельно: GUI/API их сохраняет, CLI продолжает прежние замены. Поэтому полное историческое равенство без оговорок не заявляется. Baseline читается через `git show b768cd8:practices/practice_05/lib-templater/tools/bootstrap.py`; путь проверяется через `git ls-files --full-name tools/bootstrap.py`. Checkout и рабочий шаблон не изменяются.

CLI-набор проверяет прежние флаги, вопросы/defaults через subprocess stdin, приоритет явных значений над JSON, конфликты +/- флагов, str/bool coercion конфигурации, неизвестные ключи, отсутствие namespace и ошибочный пустой namespace JSON. Отдельно проверить отсутствующий/неверный JSON, не-объект, `--dry-run` без записи и без нового подтверждения; результаты доступны без разбора stdout для API.

## 2. Настоящий PySide6 GUI

В отдельной GUI-среде:

```sh
python -m venv .venv-gui
.venv-gui/bin/python -m pip install -r requirements-gui.txt
.venv-gui/bin/python -m unittest discover -s tests -p 'bootstrap_gui_test.py' -v
```

В Windows использовать `.venv-gui/Scripts/python.exe`. Без дисплея перед GUI-набором задать `QT_QPA_PLATFORM=offscreen`; обычную демонстрацию выполнять с desktop-плагином. Наличие PySide6 и Qt platform plugin — prerequisite, отсутствие пакета не должно выдаваться за успешный GUI-прогон.

GUI-тест создаёт настоящий QApplication и форму с root отдельной копии. Основной успешный сценарий использует реальную Logic; spy допустим для подсчёта Apply, stub — для пустого Preview и управляемых ошибок. Ожидать сигналы/состояние с ограниченным timeout, не полагаться на фиксированные sleep.

| Обязательный сценарий | Ожидаемый результат |
| --- | --- |
| demo_lib → Preview → подтверждение → Apply | до подтверждения snapshot неизменен; после — один Apply, новый header, summary в том же окне |
| Неверное имя 123-lib / namespace demo:: | понятное правило рядом с полем, фокус, ввод сохранён; Apply недоступен, snapshot неизменен |
| Отмена и закрытие подтверждения | ноль Apply, snapshot неизменен, ввод и готовый Preview сохранены |
| Изменение параметра и возврат обратно | старый Preview нельзя применить |
| Пустые operations | «Нет изменений», Apply недоступен |
| Работа worker | события GUI обрабатываются, поля/кнопки заблокированы, повторный Apply невозможен |
| Ошибка Preview / Apply | stage/message/field/path показаны; после Apply предупреждение о частичных изменениях, без успеха |
| Закрытие во время работы | окно/worker не уничтожаются до finished, затем закрытие завершается |
| Длинные списки, пути и сообщения | доступны целиком; rename имеет оба пути, типы обозначены текстом |
| Клавиатура | Tab по форме, фокус виден, Enter в поле не выполняет Apply без подтверждения |

## 3. Ручная демонстрация

Создать отдельную рабочую копию шаблона вне исходного checkout; скопировать tools, src, tests, cmake, include, CMakeLists и существующие style/gitignore/bin/examples, если они есть. Не включать build/venv/.git. В этой копии запустить:

```sh
python tools/bootstrap_gui.py
```

Проверить начальные defaults и неизменяемый root. Ввести demo_lib, оставить namespace пустым, нажать «Предпросмотр». Проверить эффективный namespace, все операции и предупреждение об удалениях. Сначала отменить подтверждение и убедиться в отсутствии записи; затем подтвердить и увидеть успех. Для ошибки ввода/выполнения использовать свежую копию. Уже переименованный шаблон не обязан повторно настраиваться.

Для отдельного неинтерактивного CLI-прогона на ещё одной свежей копии:

```sh
python tools/bootstrap.py demo_lib --namespace demo_lib --codestyle google --editorconfig match-codestyle --no-bin --no-examples
```

## 4. Сохранение Practice 4

На исходном шаблоне, без запуска Apply над ним, в Linux/WSL:

```sh
sh scripts/check.sh
```

Ожидается configure/build с BUILD_TESTS=ON и BUILD_BIN=OFF, минимум один обнаруженный smoke test и PASS bootstrap layout. Команда остаётся основной единой проверкой Practice 4; GUI/Logic-наборы Practice 5 запускаются отдельно. Обычный BUILD_BIN=ON исходного шаблона, C++20/C++23 и CI вне объёма.

## Фактические результаты — 2026-10-26

Проверенный HEAD до документационных правок: `6cf71268e7c42129cd610c289711989dd46ada5f`.
Windows 11 (build 26200), Python 3.12.0; PySide6/Qt 6.10.1. В `.venv-logic` PySide6 отсутствует.

| Команда / проверка | Результат |
| --- | --- |
| `.venv-logic/Scripts/python.exe -B -m unittest discover -s tests -p bootstrap_logic_test.py -v` | 16 PASS |
| `.venv-logic/Scripts/python.exe -B -m unittest discover -s tests -p bootstrap_cli_test.py -v` | 15 PASS |
| `.venv-logic/Scripts/python.exe -B tests/bootstrap_layout_test.py` | PASS |
| `$env:QT_QPA_PLATFORM='windows'; ./.venv-gui/Scripts/python.exe -B -m unittest discover -s tests -p bootstrap_gui_test.py -v` | 13 PASS с desktop-плагином; ранее тот же набор прошёл с offscreen |
| Сгенерированный API проект `demo_lib` во временной копии WSL: configure/build/CTest, BUILD_TESTS=ON, BUILD_BIN=OFF | PASS; обнаружен и выполнен `Smoke.TrueIsTrue` |

Desktop-прогон QtTest открыл настоящие окна и диалоги на свежих копиях: defaults/root, Preview, отмена/закрытие, подтверждение/summary/header, ошибочный ввод и восстановление, worker и отложенное закрытие. Это автоматизированное desktop-прохождение. Из ручной проверки пользователя подтверждён Preview, выявивший затрагивание служебных файлов и повторные операции CMake. После исправлений регрессии проверяют сохранность служебных файлов и правильную цель; отдельная полная человеческая приёмка после исправлений не засвидетельствована.

Для сгенерированного проекта выполнены `cmake -S . -B build -G 'Unix Makefiles' -DBUILD_TESTS=ON -DBUILD_BIN=OFF`, `cmake --build build`, `ctest --test-dir build -N`, `ctest --test-dir build --output-on-failure`. WSL: CMake 3.28.3, GCC 13.3.0. Исходный `sh scripts/check.sh` блокируется CRLF; Ninja в WSL отсутствует, поэтому применены эквивалентные команды с Makefiles. Скрипт не менялся. Рабочий репозиторий через bootstrap не преобразовывался.
