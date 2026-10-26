# Tasks

Ретроспективный образец плана для той же фичи, уже реализованной через Spec Kit. Ни одна задача ниже не выполнялась через OpenSpec и не разрешена к выполнению этим экспериментом; поэтому все checkbox оставлены пустыми. Завершение подготовки документов не означает завершение реализации этим change. Существующие файлы и тесты приведены как проверяемые ориентиры, не как запрос повторно их создать.

## 1. Independent Logic and Preview

- [ ] 1.1 Предоставить Settings/Preview/Operation/ApplyResult и структурированные ошибки в tools/bootstrap.py без Qt; проверка — импорт и вызовы API без GUI-пакета/ручного ввода, описание binding в документации Logic.
- [ ] 1.2 Реализовать проверку полей и структуры без trim и записи; проверка — bootstrap_logic_test.py: invalid_fields_without_trim, missing_required_files_listed_without_changes, read_and_decode_errors_have_path_without_changes.
- [ ] 1.3 Подготовить последовательный Preview в памяти; проверка — неизменность дерева, repeatability, prepared style/gitignore, repeated updates, parent order и optional directories в bootstrap_logic_test.py; документировать операции без обещания diff/rollback.

## 2. Apply and CLI compatibility

- [ ] 2.1 Связать Apply с root/settings Preview и существующими этапами, остановкой при первой ошибке и сводкой; проверка — apply_uses_preview_and_returns_summary, apply_first_write_failure_stops, apply_read_decode_rename_and_delete_failures_stop на временных копиях; документировать частичные изменения.
- [ ] 2.2 Сохранить CLI/JSON/вопросы/dry-run без нового подтверждения; проверка — bootstrap_cli_test.py: interactive_defaults, json_priority, coercion, conflicting_flags, bad_configs, dry_run_without_writes и четыре bin/examples-комбинации. Перед заключением о точном равенстве историческому bootstrap отдельно учесть оговорки review.md, не менять контракт автоматически.

## 3. GUI and local checks

- [ ] 3.1 Подключить форму PySide6 с defaults, пятью полями, неизменяемым root, эффективными настройками и прокруткой; проверка — defaults_and_real_preview_without_writes, operation_order_long_paths_and_scrollbars в bootstrap_gui_test.py; описать запуск и зависимость requirements-gui.txt в README.
- [ ] 3.2 Реализовать актуальность Preview и явное подтверждение; проверка — each_field_change_and_return_invalidates_preview, empty_preview_cannot_apply, confirmation_cancel_and_close_do_not_apply и confirmation_applies_same_preview_once_and_returns_summary.
- [ ] 3.3 Подключить worker, статусы, ошибки и клавиатуру; проверка — QtTest-сценарии responsive/close_deferred, apply_error_warns_partial_changes_without_success, validation_focus_preserved_input_and_recovery, tab_order_and_enter_in_field_do_not_apply; документировать отсутствие отмены выполнения и необходимость нового Preview после Apply.

## 4. Integration acceptance

- [ ] 4.1 Воспроизвести успех demo_lib, неверный параметр и отказ настоящего GUI, самостоятельный Logic-набор без Qt и CLI-регрессию; проверка — отчёт с командами/средой и неизменным рабочим шаблоном, все записи только на отдельных копиях.
- [ ] 4.2 Проверить bootstrap_layout_test.py и существующий sh scripts/check.sh в подходящей среде без несвязанных исправлений; проверка — сохранённые результаты layout/CTest. Этот эксперимент эти проверки продукта не запускает.
