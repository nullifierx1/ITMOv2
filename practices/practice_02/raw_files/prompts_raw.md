# Используемые промты

## **FEW-SHOT**

```txt
Это эксперимент Few-shot для второй практики.

Работай с @practices/practice_01/adr.md, @practices/practice_01/analysis.md, @practices/practice_01/context.md, @practices/practice_01/example_music_library/library.h, @practices/practice_01/example_music_library/library_manager.h и @practices/practice_01/example_music_library/playlist.h.

Нужно улучшить раздел "Рассмотренные альтернативы" в ADR. Хочу, чтобы аргументы опирались на конкретные AS IS факты и заканчивались проверяемым следствием.

Вот хороший пример.

AS IS: Library::data() возвращает mutable-ссылку на внутренний контейнер.

TO BE: прямой mutable-доступ убирается, изменение состояния идёт через узкие доменные операции.

Почему: объект, который владеет состоянием, сам поддерживает его инварианты.

Evidence: сигнатура Library::data() и поля data_, name_to_idx_

Проверка: в TO BE публичный API Library не возвращает mutable-ссылки на контейнеры.

А вот плохой пример.

"Нужно улучшить инкапсуляцию Library, потому что так архитектура будет правильнее."

Он плохой, потому что тут нет конкретного AS IS факта, evidence и проверки.

Теперь сравни три варианта:

1. оставить прямой mutable-доступ
2. закрыть mutable-доступ, но держать согласованность состояния в LibraryManager
3. закрыть mutable-доступ и держать базовые инварианты внутри Library

Для вариантов 2 и 3 считай mutable-доступ уже закрытым.

Сделай короткую таблицу:

AS IS evidence | Альтернатива | Почему принимается или отклоняется | Проверяемое следствие

Не придумывай реализацию LibraryManager. Не смешивай AS IS и TO BE. Если данных для вывода мало, прямо это напиши. Принятое решение ADR не меняй.

Web не используй.

Перед ответом сохрани этот запрос без изменений в @practices/practice_02/raw_files/prompts_raw.md в раздел FEW-SHOT.

Свой итоговый ответ сохрани без правок в @practices/practice_02/raw_files/responses_raw.md в раздел FEW-SHOT.

Другие файлы не меняй.
```


---

## **R.C.T.F.**

```txt
Это эксперимент R.C.T.F. для второй практики.

Работай с @practices/practice_01/adr.md, @practices/practice_01/analysis.md, @practices/practice_01/context.md, @practices/practice_01/example_music_library/library.h, @practices/practice_01/example_music_library/library_manager.h и @practices/practice_01/example_music_library/playlist.h.

Role: ты архитектор, который проверяет, не смешались ли в ADR факты текущей системы и решения будущей архитектуры.

Context: нас интересует раздел "Рассмотренные альтернативы".

Task: разбери три варианта:
1. оставить mutable-доступ
2. закрыть mutable-доступ, но держать инварианты в manager
3. закрыть mutable-доступ и держать инварианты в Library

Для каждого варианта коротко напиши, что здесь реально AS IS, что относится к TO BE, почему вариант принят или отклонён и какое следствие можно проверить.

Не придумывай реализацию LibraryManager. Если данных мало, так и напиши.

Format: небольшая таблица и пара предложений о том, где ADR смешивает AS IS и TO BE.

Web не используй.

Перед ответом сохрани этот запрос без изменений в @practices/practice_02/raw_files/prompts_raw.md в раздел R.C.T.F.

Свой итоговый ответ сохрани без правок в @practices/practice_02/raw_files/responses_raw.md в раздел R.C.T.F.

Другие файлы не меняй.
```

---

## **CHAIN OF VERIFICATION**

```txt
Это эксперимент Chain of Verification для второй практики.

Работай с @practices/practice_01/adr.md, @practices/practice_01/analysis.md, @practices/practice_01/context.md, @practices/practice_01/example_music_library/library.h, @practices/practice_01/example_music_library/library_manager.h, @practices/practice_01/example_music_library/playlist.h и @practices/practice_01/tests_unit.md.

Проверь раздел "Рассмотренные альтернативы" в ADR.

Сначала дай короткий черновой вывод по трём альтернативам.

Потом составь несколько вопросов к своему же ответу. Например, действительно ли это AS IS, есть ли такой контракт в исходниках, не придумана ли реализация manager.

После этого проверь свои вопросы по файлам и дай исправленный итог.

В ответе оставь три части:
Черновик
Проверка
Итог

Не показывай скрытые рассуждения. Нужны только выводы, вопросы проверки, найденные evidence и финальная версия.

Web не используй.

Перед ответом сохрани этот запрос без изменений в @practices/practice_02/raw_files/prompts_raw.md в раздел CHAIN OF VERIFICATION.

Свой итоговый ответ сохрани без правок в @practices/practice_02/raw_files/responses_raw.md в тот же раздел.

Другие файлы не меняй.
```

---

## **TREE OF THOUGHTS**

```txt
Это эксперимент Tree of Thoughts для второй практики.

Работай с @practices/practice_01/adr.md, @practices/practice_01/analysis.md, @practices/practice_01/context.md, @practices/practice_01/project_management.md, @practices/practice_01/tests_integration.md, @practices/practice_01/example_music_library/library.h и @practices/practice_01/example_music_library/library_manager.h.

Нужно сравнить три варианта архитектуры Library:

1. оставить mutable-доступ
2. закрыть mutable-доступ, но держать инварианты в LibraryManager
3. закрыть mutable-доступ и держать инварианты внутри Library

Сравни их по одним и тем же критериям: владение состоянием, поддержка инвариантов, граница ответственности и проверяемость тестами.

Не показывай внутреннюю цепочку рассуждений. Покажи сами варианты, evidence, сравнение и итоговый выбор.

Если что-то нельзя подтвердить по файлам, прямо это отметь.
Реализацию manager не придумывай.
Принятое решение ADR не меняй.

Web не используй.

Перед ответом сохрани этот запрос без изменений в @practices/practice_02/raw_files/prompts_raw.md в раздел TREE OF THOUGHTS.

Свой итоговый ответ сохрани без правок в @practices/practice_02/raw_files/responses_raw.md в тот же раздел.

Другие файлы не меняй.
```

---

## **RAG**

```txt
Это эксперимент RAG для второй практики.

Работай с @practices/practice_01/adr.md, @practices/practice_01/problem.md, @practices/practice_01/analysis.md, @practices/practice_01/product_management.md, @practices/practice_01/project_management.md, @practices/practice_01/tests_unit.md, @practices/practice_01/tests_integration.md, @practices/practice_01/tests_e2e.md и @practices/practice_01/tests_load.md.

Нужно проверить, насколько решения из ADR прослеживаются до остальных артефактов первой практики.

Для основных решений найди цепочку:

решение ADR -> подтверждающий контекст -> use case или требование -> тест

Если какого-то звена нет, не додумывай его, а пометь как gap.

Особенно посмотри на скрытие mutable-контейнеров, инварианты внутри доменных объектов, уникальность имён и weak_ptr в Playlist.

Ответ нужен короткий. Сделай таблицу трассировки и после неё напиши, какие пробелы нашлись.

Web не используй.

Перед ответом сохрани этот запрос без изменений в @practices/practice_02/raw_files/prompts_raw.md в раздел RAG.

Свой итоговый ответ сохрани без правок в @practices/practice_02/raw_files/responses_raw.md в раздел RAG.

Другие файлы не меняй.
```

---

## **REACT**

```txt
Это эксперимент ReAct для второй практики.

Работай с @practices/practice_01/adr.md, @practices/practice_01/analysis.md, @practices/practice_01/project_management.md, @practices/practice_01/tests_unit.md, @practices/practice_01/tests_integration.md, @practices/practice_01/tests_e2e.md, @practices/practice_01/example_music_library/library.h, @practices/practice_01/example_music_library/library_manager.h, @practices/practice_01/example_music_library/playlist.h и @practices/practice_01/example_music_library/playlist_manager.h.

Найди одну реальную несогласованность или слабую связь между ADR, планом проекта и тестами.

Сделай максимум четыре коротких шага.

Action: что проверяешь
Observation: что реально нашёл
Decision: что проверишь следующим

Это журнал действий и наблюдений, а не скрытая цепочка рассуждений.

В конце напиши найденный gap, evidence и минимальную правку, которая сделала бы артефакты согласованнее.

Не придумывай отсутствующий код.
Web не используй.

Перед ответом сохрани этот запрос без изменений в @practices/practice_02/raw_files/prompts_raw.md в раздел REACT.

Свой итоговый ответ сохрани без правок в @practices/practice_02/raw_files/responses_raw.md в раздел REACT.

Другие файлы не меняй.
```
