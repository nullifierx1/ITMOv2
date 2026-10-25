# Quickstart: проверка Practice 5 после реализации

Сейчас создан только план: новые модули и тесты ниже ещё не существуют. Команды описывают будущую приёмку, а не выполненные проверки. Контракт: `specs/contract.md`; Python binding: `specs/002-bootstrap-logic/contracts/bootstrap-api.md`; данные: `specs/002-bootstrap-logic/data-model.md`.

## Среда

Python 3.12; для GUI — PySide6 из будущего `requirements-gui.txt`. Для Practice 4: Linux/WSL, sh, CMake >= 3.20, Ninja, C++ compiler и возможность получить GoogleTest при первом configure. Не менять текущий C++ standard или CI ради подготовки среды.

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

Для каждой из четырёх комбинаций bin/examples сравнить итоговые деревья (относительные пути и типы) и байты файлов созданных проектов нового API и исходного CLI на идентичных копиях. Из сравнения исключить только точный относительный путь `tools/bootstrap.py`, поскольку версии самого скрипта различаются. Никакой нормализации путей или содержимого и никаких дополнительных исключений; все остальные пути, типы и байты должны совпадать. Исходный baseline — `tools/bootstrap.py` из текущего до реализации коммита `b768cd8`; получить его read-only через `git show b768cd8:practices/practice_05/lib-templater/tools/bootstrap.py` в родительском Git-репозитории. Перед фиксацией fixture проверить путь через `git ls-files --full-name tools/bootstrap.py`. Копию исходного скрипта размещать на месте tools/bootstrap.py только в baseline-fixture, чтобы root определялся прежним способом. Для обоих прогонов использовать одинаковые настройки, имя и состав fixture.

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

## Запись результатов при реализации

Указать проверенный commit, Python/PySide6 версии, ОС и Qt platform, команды и pass/fail. До минимального исправления сохранить failing check; после — его успешный результат и необходимые регрессии. Текущий этап планирования не заявляет прохождение ещё не созданных тестов и не выполняет bootstrap над рабочим проектом.
