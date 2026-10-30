#!/usr/bin/env python3
"""One-window desktop interface for the bootstrap API."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QThread, Qt, Signal, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)

if __package__:
    from . import bootstrap
else:
    import bootstrap


class BootstrapWorker(QThread):
    succeeded = Signal(object)
    failed = Signal(object)

    def __init__(self, stage, args, parent):
        super().__init__(parent)
        self.stage = stage
        self.args = args

    def run(self):
        try:
            function = bootstrap.preview if self.stage == "preview" else bootstrap.apply
            self.succeeded.emit(function(*self.args))
        except bootstrap.BootstrapError as error:
            self.failed.emit(error)
        except Exception as error:
            # An unexpected failure must also return control to the form.
            self.failed.emit(bootstrap.BootstrapError(str(error), stage=self.stage))


class BootstrapWindow(QWidget):
    def __init__(self, root: Path | None = None):
        super().__init__()
        self.root = (bootstrap.ROOT if root is None else Path(root)).resolve()
        self.current_preview = None
        self.worker = None
        self._close_pending = False
        self._error_field = None
        self._confirming = False
        self.setWindowTitle("Настройка C++ библиотеки")
        self.resize(850, 800)

        self.project_name = QLineEdit()
        self.namespace = QLineEdit()
        self.namespace.setPlaceholderText("Пустое значение — использовать имя проекта")
        self.codestyle = QComboBox()
        self.codestyle.addItems(sorted(bootstrap.CLANG_FORMAT_PRESETS))
        self.codestyle.setCurrentText("google")
        self.keep_bin = QCheckBox("Сохранить/создать bin")
        self.keep_bin.setChecked(True)
        self.keep_examples = QCheckBox("Сохранить/создать examples")
        self.root_display = QLineEdit(str(self.root))
        self.root_display.setReadOnly(True)
        self.root_display.setCursorPosition(0)
        self.error_labels = {}

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.addRow("Целевой каталог:", self.root_display)
        for name, title, widget in (
            ("project_name", "Имя проекта:", self.project_name),
            ("namespace", "Namespace:", self.namespace),
            ("codestyle", "Стиль кода:", self.codestyle),
        ):
            form.addRow(title, widget)
            error_label = QLabel()
            error_label.setWordWrap(True)
            error_label.setTextFormat(Qt.PlainText)
            error_label.setVisible(False)
            form.addRow(error_label)
            self.error_labels[name] = error_label
        form.addRow("EditorConfig:", QLabel("Соответствует выбранному стилю"))
        form.addRow(self.keep_bin)
        form.addRow(self.keep_examples)
        layout.addLayout(form)

        self.preview_button = QPushButton("Предпросмотр")
        self.apply_button = QPushButton("Запустить bootstrap")
        self.apply_button.setEnabled(False)
        for button in (self.preview_button, self.apply_button):
            button.setAutoDefault(False)
        buttons = QHBoxLayout()
        buttons.addWidget(self.preview_button)
        buttons.addWidget(self.apply_button)
        layout.addLayout(buttons)
        self.status = QLabel("Предпросмотр ещё не выполнен")
        self.status.setTextFormat(Qt.PlainText)
        self.effective_settings = QLabel()
        self.effective_settings.setTextFormat(Qt.PlainText)
        self.effective_settings.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addWidget(self.effective_settings)
        self.operations = QPlainTextEdit()
        self.result = QPlainTextEdit()
        for title, widget in (("Операции:", self.operations), ("Результат:", self.result)):
            widget.setReadOnly(True)
            widget.setLineWrapMode(QPlainTextEdit.NoWrap)
            widget.setTabChangesFocus(True)
            label = QLabel(title)
            label.setBuddy(widget)
            layout.addWidget(label)
            layout.addWidget(widget, 2 if widget is self.operations else 1)

        self._fields = (self.project_name, self.namespace, self.codestyle,
                        self.keep_bin, self.keep_examples)
        for widget in (self.project_name, self.namespace):
            widget.textChanged.connect(self._invalidate_preview)
        self.codestyle.currentTextChanged.connect(self._invalidate_preview)
        self.keep_bin.toggled.connect(self._invalidate_preview)
        self.keep_examples.toggled.connect(self._invalidate_preview)
        self.preview_button.clicked.connect(self._start_preview)
        self.apply_button.clicked.connect(self._start_apply)
        for first, second in zip(self._fields, self._fields[1:]):
            self.setTabOrder(first, second)
        self.setTabOrder(self.keep_examples, self.preview_button)
        self.setTabOrder(self.preview_button, self.apply_button)
        self.project_name.setFocus()

    @Slot()
    def _invalidate_preview(self):
        self.current_preview = None
        self.apply_button.setEnabled(False)
        self.operations.clear()
        self.effective_settings.clear()
        if self.worker is None:
            self.status.setText("Параметры изменены. Повторите предпросмотр.")

    @Slot()
    def _start_preview(self):
        if self.worker is not None:
            return
        self._invalidate_preview()
        self.result.clear()
        self._error_field = None
        for label in self.error_labels.values():
            label.clear()
            label.setVisible(False)
        settings = bootstrap.Settings(self.project_name.text(), self.namespace.text(),
                                      self.codestyle.currentText(), self.keep_bin.isChecked(),
                                      self.keep_examples.isChecked())
        self._start_worker("preview", (self.root, settings))

    def _start_worker(self, stage, args):
        self.status.setText("Подготовка" if stage == "preview" else "Выполняется")
        for widget in (*self._fields, self.preview_button, self.apply_button):
            widget.setEnabled(False)
        self.worker = BootstrapWorker(stage, args, self)
        self.worker.succeeded.connect(self._on_success)
        self.worker.failed.connect(self._on_error)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    @Slot()
    def _start_apply(self):
        selected = self.current_preview
        if self.worker is not None or self._confirming or selected is None or not selected.operations:
            return
        self._confirming = True
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Warning)
        dialog.setWindowTitle("Подтверждение bootstrap")
        dialog.setTextFormat(Qt.PlainText)
        dialog.setText(
            f"Целевой каталог: {selected.root}\n\n"
            "Применить перечисленные файловые изменения? Они могут включать удаления. "
            "Изменения не будут автоматически отменены."
        )
        dialog.setStandardButtons(QMessageBox.Apply | QMessageBox.Cancel)
        dialog.button(QMessageBox.Apply).setText("Применить")
        dialog.button(QMessageBox.Cancel).setText("Отмена")
        dialog.setDefaultButton(QMessageBox.Cancel)
        dialog.setEscapeButton(QMessageBox.Cancel)
        answer = dialog.exec()
        self._confirming = False
        dialog.deleteLater()
        if answer != QMessageBox.Apply or self.current_preview is not selected:
            return
        self.current_preview = None
        self.result.clear()
        self._start_worker("apply", (selected,))

    @Slot(object)
    def _on_success(self, value):
        if isinstance(value, bootstrap.Preview):
            self.current_preview = value
            settings = value.settings
            self.effective_settings.setText(
                f"Имя: {settings.project_name}; namespace: {settings.namespace}; "
                f"стиль: {settings.codestyle}; bin: {settings.keep_bin}; examples: {settings.keep_examples}"
            )
            self.operations.setPlainText("\n".join(
                f"{op.kind} {op.target_kind}: {op.path}"
                + (f" → {op.new_path}" if op.new_path is not None else "")
                for op in value.operations
            ))
            self.status.setText("Предпросмотр готов" if value.operations else "Нет изменений")
        else:
            self.status.setText("Bootstrap выполнен успешно")
            self.result.setPlainText(value.summary)

    @Slot(object)
    def _on_error(self, error):
        self.current_preview = None
        self.status.setText("Ошибка")
        details = [f"stage: {error.stage}", error.message]
        if error.field:
            details.append(f"field: {error.field}")
            if error.field in self.error_labels:
                label = self.error_labels[error.field]
                label.setText(error.message)
                label.setVisible(True)
                self._error_field = error.field
        if error.path:
            details.append(f"path: {error.path}")
        if error.stage == "apply":
            details.append("Возможны частичные изменения. Проверьте файлы проекта. "
                           "Перед повторным запуском требуется новый предпросмотр.")
        self.result.setPlainText("\n".join(details))

    @Slot()
    def _on_finished(self):
        worker = self.worker
        self.worker = None
        worker.deleteLater()
        for widget in (*self._fields, self.preview_button):
            widget.setEnabled(True)
        self.apply_button.setEnabled(bool(self.current_preview and self.current_preview.operations))
        if self._close_pending:
            self.close()
        elif self._error_field:
            getattr(self, self._error_field).setFocus()

    def closeEvent(self, event: QCloseEvent):
        if self.worker is not None:
            self._close_pending = True
            event.ignore()
        else:
            event.accept()


def main():
    app = QApplication(sys.argv)
    window = BootstrapWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
