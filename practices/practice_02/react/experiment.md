# ReAct

## Цель и границы

Цель — найти одну фактическую слабую связь между ADR, планом и тестами за
максимум четыре наблюдаемых шага. Разрешены только перечисленные в prompt
файлы Practice 1; код и web запрещены.

Exact prompt: [`prompts_raw.md`](../raw_files/prompts_raw.md), `REACT`.
Raw response: [`responses_raw.md`](../raw_files/responses_raw.md), `REACT`.

## Наблюдаемые действия модели

| Шаг | Action | Observation | Decision |
|---|---|---|---|
| 1 | Проверить TO BE-контракт ADR. | ADR отклоняет повторные имена и называет уникальность track name новым TO BE-решением. | Проверить план. |
| 2 | Проверить `project_management.md`. | Правила повторов упомянуты при принятии контрактов, но отдельной проверки в плане нет. | Проверить тесты. |
| 3 | Проверить unit, integration и E2E. | Есть add/get/remove, индекс и weak_ptr, но нет явного negative scenario для duplicate track или playlist name. | Проверить AS IS заголовки. |
| 4 | Проверить `library.h` и `playlist_manager.h`. | Индекс хранит вектор позиций на имя; реализация и контракт manager не известны. | Зафиксировать gap без предположения о коде. |

### Принято

- Найденный gap реален: правило повторов есть в ADR, но нет явно названного
  unit, integration или E2E сценария для track и playlist duplicates.
- AS IS `unordered_map<string, vector<size_t>>` не подтверждает уникальность
  имени; это соответствует явной оговорке ADR о новом TO BE-правиле.

### Отклонено

- Нельзя говорить, что текущая реализация уже принимает дубликаты или что
  `PlaylistManager` уже умеет их отклонять: тела методов отсутствуют.

### Скорректировано

Предложение raw response вернуть `false` — разумный TO BE-вариант, потому что
такие целевые сигнатуры уже названы в ADR. Его нельзя выдавать за текущую
сигнатуру `LibraryManager` или `PlaylistManager`.

## Изменённая версия ADR

В [`adr_react.md`](../modified_artifacts/adr_react.md) реально добавлен один
минимальный пункт в «Последствия и главный риск»: правило повторяющихся имён
не имеет явно названного тестового сценария. Пункт не утверждает поведения
текущей реализации. Practice 1 не менялась.

## Ручная проверка

Сверены ADR, [`project_management.md`](../../practice_01/project_management.md),
[`tests_unit.md`](../../practice_01/tests_unit.md),
[`tests_integration.md`](../../practice_01/tests_integration.md),
[`tests_e2e.md`](../../practice_01/tests_e2e.md), `library.h` и
`playlist_manager.h`. Лимит в четыре шага соблюдён в raw response.
