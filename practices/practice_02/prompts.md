# Журнал экспериментов Практики 2

Исходный [`adr.md`](../practice_01/adr.md) Practice 1 остаётся неизменным
baseline. Для независимого сравнения результатов каждая техника получила
отдельную изменённую копию ADR в
[`modified_artifacts/`](modified_artifacts/).

- Выбранный исходный артефакт Practice 1: [`adr.md`](../practice_01/adr.md),
  раздел «Рассмотренные альтернативы».
- Что улучшаем: доказательность выбора, разделение AS IS/TO BE и трассировку
  принятых TO BE-контрактов до существующих артефактов.
- Как поймём, что изменение полезно: каждая независимая версия ADR содержит
  только эффект своей техники и ссылается на проверяемый локальный evidence.

| Техника | Файл эксперимента | Изменённая версия артефакта | Конкретное изменение | Проверка | Что отклонили |
|---|---|---|---|---|---|
| Few-shot | [`few_shot/experiment.md`](few_shot/experiment.md) | [`adr_few_shot.md`](modified_artifacts/adr_few_shot.md) | Альтернативы получили AS IS evidence и проверяемые TO BE-следствия. [Изменённый ADR](modified_artifacts/adr_few_shot.md) | Сигнатуры `Library` и граница знания о manager. | TO BE в колонке AS IS и домыслы о manager. |
| R.C.T.F. | [`rctf/experiment.md`](rctf/experiment.md) | [`adr_rctf.md`](modified_artifacts/adr_rctf.md) | Альтернативы явно разделены на AS IS и TO BE. [Изменённый ADR](modified_artifacts/adr_rctf.md) | Заголовки, ADR и `analysis.md`. | Runtime-баг индекса и существующая логика manager. |
| Chain of Verification | [`chain_of_verification/experiment.md`](chain_of_verification/experiment.md) | [`adr_chain_of_verification.md`](modified_artifacts/adr_chain_of_verification.md) | Убрано неподтверждённое «рассогласование»; оставлена возможность обхода инвариантов. [Изменённый ADR](modified_artifacts/adr_chain_of_verification.md) | Вопросы модели проверены по заголовкам и unit-артефакту. | Утверждение о доказанной текущей поломке. |
| Tree of Thoughts | [`tree_of_thoughts/experiment.md`](tree_of_thoughts/experiment.md) | [`adr_tree_of_thoughts.md`](modified_artifacts/adr_tree_of_thoughts.md) | Три альтернативы сравнены по одним критериям. [Изменённый ADR](modified_artifacts/adr_tree_of_thoughts.md) | Владение, инварианты, граница и TO BE-проверяемость. | Неизвестная реализация manager. |
| RAG | [`rag/experiment.md`](rag/experiment.md) | [`adr_rag.md`](modified_artifacts/adr_rag.md) | Добавлена трассировка ADR до контекста, use cases и тестов. [Изменённый ADR](modified_artifacts/adr_rag.md) | Только существующие документы Practice 1. | Несуществующие тесты вместо gaps. |
| ReAct | [`react/experiment.md`](react/experiment.md) | [`adr_react.md`](modified_artifacts/adr_react.md) | Добавлен один gap трассировки правила повторяющихся имён. [Изменённый ADR](modified_artifacts/adr_react.md) | Четыре Action–Observation–Decision шага. | Поведение отсутствующей реализации. |

## Независимое ревью

| Замечание другой команды | Где исправили | Evidence |
|---|---|---|
| Двусмысленность |  |  |
| Непроверяемое требование |  |  |
| Пропущенный риск или источник |  |  |
