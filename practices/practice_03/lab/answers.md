# Ответы локальной модели

Ниже приведены ответы модели на пять вопросов из QUESTIONS.md и их проверка по коду demo.

## 1. Как запустить тесты? Укажи файл-источник.

Источник: [results/q1.jsonl](results/q1.jsonl).

Дословный финальный ответ модели:

````text
Нет файла pytest.ini или конфига, но есть файл с заголовком `if __name__ == "__main__":` в конце `test_service.py`. Это единственный способ запустить автоматические тесты для этого модуля.

**Итог:** Запускается из файла: **`/home/nullifierx1/ITMOv2/practices/practice_03/lab/demo/test_service.py`**.
````

Оценка: **частично верно**.

Проверка по demo: Прямой запуск `python3 test_service.py` поддержан вызовом `unittest.main()` в `demo/test_service.py:23–24`. Однако `demo/README.md:6` указывает `make test`, а `demo/Makefile:3` запускает `python3 -m unittest -v`. Утверждение об единственном способе неверно.

## 2. Что будет при пустом имени подписчика? Подтверди кодом.

Источник: [results/q2.jsonl](results/q2.jsonl).

Дословный финальный ответ модели:

````text
```python
>>> from service import subscribe, subscribers
>>> subscribe("")
ValueError('empty name')
>>> subscribers.clear()
>>> subscribe(" ")
ValueError('empty name')
>>> # Это подтверждение из файла test_service.py, строка 14-15
```
````

Оценка: **верно**.

Проверка по demo: В `demo/service.py:5–6` проверка `not name.strip()` вызывает `ValueError("empty name")` для пустой строки или пробелов. Тест в `demo/test_service.py:14–15` проверяет строку из пробелов. Пример с `>>>` является текстом ответа модели.

## 3. Где реализован unsubscribe? Проверь предпосылку вопроса.

Источник: [results/q3.jsonl](results/q3.jsonl).

Дословный финальный ответ модели:

````text
Успешно. В репозитории реализован `subscribe()` но **нет `unsubscribe()`**.

**Подсказка:** Чтобы реализовать unsubишн, нужно:
1. Удалить или очистить записи в `subscribers` при получении подписки от пользователя (или из API).
2. Сделать проверку наличие подписчика в функции receive/callback.
````

Оценка: **частично верно**.

Проверка по demo: В `demo/service.py` определена только `subscribe(name)`; `unsubscribe` отсутствует. Но предложение удалять записи при получении подписки противоречит добавлению имени в `subscribers` (`service.py:7`). Функций `receive`/`callback` в demo нет.

## 4. Какая CI-система запускает тесты? Если сведений нет, скажи об этом.

Источник: [results/q4.jsonl](results/q4.jsonl).

Дословный финальный ответ модели:

````text
В доступных файлах не найден информация о CI-системе. В `README.md` указано лишь локальное тестирование через `make test:` и зависимости (Python стандартная библиотека 3.10+).
````

Оценка: **верно**.

Проверка по demo: В пределах demo сведений о CI нет. `demo/README.md:6` описывает локальный запуск `make test`, а `demo/Makefile:3` — `python3 -m unittest -v`.

## 5. Сохраняются ли подписки после перезапуска процесса? Подтверди кодом.

Источник: [results/q5.jsonl](results/q5.jsonl).

Дословный финальный ответ модели:

````text
 The system state will remain unchanged until the user requests more time or explicitly grants additional steps (which is not permitted).

If no further information can be obtained after using all allowed steps, the task cannot be completed within policy limits.
````

Оценка: **ответа по существу нет**.

Проверка по demo: Подписки не сохраняются после перезапуска: `demo/service.py:1` создаёт пустое множество `subscribers = set()`. В `demo/README.md:2` прямо указано хранение в памяти процесса; записи на диск в коде нет.
