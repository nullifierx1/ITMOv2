# Proposal

## Why

Practice 5 уже реализована через GitHub Spec Kit. Этот ретроспективный сравнительный эксперимент от 2026-10-26 проверяет путь OpenSpec Explore → Propose → Review → Validate на той же фиче; этот proposal не предшествовал коду и не служил основанием первоначальной реализации.

## What Changes

- Только документы этого change: представить существующую фичу одной формы PySide6 → Preview → подтверждение → Apply → результат в формате OpenSpec.
- Перенести согласованное поведение из [UI v2](../../../practices/practice_05/lib-templater/specs/001-bootstrap-ui/spec.md), [Logic v2](../../../practices/practice_05/lib-templater/specs/002-bootstrap-logic/spec.md) и [контракта](../../../practices/practice_05/lib-templater/specs/contract.md), без новых требований.
- Зафиксировать существующие архитектурные решения, проверяемые сценарии и результаты документального Review. Задачи — ретроспективная модель возможного плана, а не поручение повторно писать код.
- Остановиться после Review и валидации. OpenSpec Apply, Sync и Archive, bootstrap рабочего репозитория, изменения кода, тестов, Spec Kit, constitution и Git-истории исключены.

## Capabilities

### New Capabilities

Новые только относительно пустого реестра OpenSpec, не относительно продукта. `ADDED` в delta specs обозначает ретроспективную регистрацию уже согласованного поведения; это не запрос новой функциональности.

- `practice-05/bootstrap-gui`: форма, актуальность Preview, подтверждение, состояния выполнения, результат и клавиатура.
- `practice-05/bootstrap-logic`: независимый API, параметры, операции без записи, применение и совместимость CLI/JSON.

### Modified Capabilities

Нет: `openspec list --specs --json` вернул пустой реестр. Исходные спецификации Spec Kit остаются источником согласованных требований.

## Impact

Реальные записи ограничены `openspec/changes/practice-05-bootstrap-gui-retrospective/`. Корень OpenSpec — ITMOv2, целевой код — `practices/practice_05/lib-templater/`. Исследованы `tools/bootstrap.py`, `tools/bootstrap_gui.py`, существующие Python-проверки, `requirements-gui.txt` (PySide6 6.10.1), `scripts/check.sh`, Spec Kit plan и constitution. Их изменение и повторная реализация не планируются. Публичные API — `preview(root, settings)` и `apply(preview)` — сохраняются; зависимость PySide6 относится только к GUI.
