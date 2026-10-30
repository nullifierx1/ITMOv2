"""Real QApplication/QtTest integration checks; PySide6 is required."""

import sys
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from PySide6.QtCore import QEventLoop, QTimer, Qt
from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from bootstrap_cli_test import add_service_files, copy_template, snapshot

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import bootstrap, bootstrap_gui


class BootstrapGuiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)

    def wait_until(self, predicate, timeout=5000):
        if predicate():
            return
        loop = QEventLoop()
        poll = QTimer()
        poll.setInterval(1)
        poll.timeout.connect(lambda: loop.quit() if predicate() else None)
        deadline = QTimer()
        deadline.setSingleShot(True)
        deadline.timeout.connect(loop.quit)
        poll.start()
        deadline.start(timeout)
        loop.exec()
        poll.stop()
        deadline.stop()
        self.assertTrue(predicate(), "Timed out waiting for GUI state")

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        copy_template(self.root)
        self.window = bootstrap_gui.BootstrapWindow(self.root)
        self.addCleanup(self.close_window)
        self.window.show()
        self.window.activateWindow()

    def close_window(self):
        self.wait_until(lambda: self.window.worker is None)
        self.window.close()
        self.app.processEvents()

    def make_preview(self):
        self.window.project_name.setText("demo_lib")
        QTest.mouseClick(self.window.preview_button, Qt.LeftButton)
        self.wait_until(lambda: self.window.worker is None)
        self.assertIsNotNone(self.window.current_preview, self.window.result.toPlainText())
        return self.window.current_preview

    def confirm(self, response):
        seen = []
        timer = QTimer()
        timer.setInterval(1)

        def answer():
            dialog = self.app.activeModalWidget()
            if not isinstance(dialog, QMessageBox):
                return
            seen.append((dialog.text(), dialog.defaultButton() == dialog.button(QMessageBox.Cancel)))
            timer.stop()
            if response == "close":
                dialog.close()
            else:
                QTest.mouseClick(dialog.button(response), Qt.LeftButton)

        timer.timeout.connect(answer)
        timer.start()
        try:
            QTest.mouseClick(self.window.apply_button, Qt.LeftButton)
        finally:
            timer.stop()
        self.assertTrue(seen, "Confirmation dialog was not shown")
        self.assertIn(str(self.root), seen[0][0])
        self.assertIn("удален", seen[0][0].lower())
        self.assertTrue(seen[0][1], "Cancel must be the default")

    def test_confirmation_cancel_and_close_do_not_apply(self):
        for name in ("bin", "examples"):
            (self.root / name).mkdir()
            (self.root / name / "old.txt").write_text("keep", encoding="utf-8")
        self.window.keep_bin.setChecked(False)
        preview = self.make_preview()
        self.assertTrue(any(op.kind == "delete" for op in preview.operations))
        before = snapshot(self.root)
        for response in (QMessageBox.Cancel, "close"):
            with self.subTest(response=response), \
                 patch.object(bootstrap, "apply", wraps=bootstrap.apply) as apply, \
                 patch.object(Path, "write_text", side_effect=AssertionError("write attempted")) as write:
                self.confirm(response)
                self.assertEqual(apply.call_count, 0)
                write.assert_not_called()
                self.assertIs(self.window.current_preview, preview)
                self.assertEqual(self.window.project_name.text(), "demo_lib")
                self.assertTrue(self.window.apply_button.isEnabled())
                self.assertEqual(snapshot(self.root), before)

    def test_confirmation_applies_same_preview_once_and_returns_summary(self):
        (self.root / "examples").mkdir()
        (self.root / "examples/old.txt").write_text("old", encoding="utf-8")
        before = snapshot(self.root)
        preview = self.make_preview()
        self.assertEqual(snapshot(self.root), before)
        with patch.object(bootstrap, "apply", wraps=bootstrap.apply) as apply:
            self.confirm(QMessageBox.Apply)
            self.assertIsNone(self.window.current_preview)
            self.assertFalse(self.window.apply_button.isEnabled())
            self.wait_until(lambda: self.window.worker is None)
            self.assertEqual(apply.call_count, 1)
            self.assertIs(apply.call_args.args[0], preview)
            QTest.mouseClick(self.window.apply_button, Qt.LeftButton)
            self.assertEqual(apply.call_count, 1)
        self.assertIn("успешно", self.window.status.text())
        self.assertTrue(self.window.result.toPlainText())
        self.assertTrue((self.root / "include/demo_lib/foo.h").is_file())
        self.assertFalse((self.root / "include/foo.h").exists())
        self.assertFalse((self.root / "examples").exists())

    def test_gui_apply_preserves_service_files(self):
        paths = add_service_files(self.root)
        before = snapshot(self.root)
        selected = self.make_preview()
        self.assertTrue(set(paths).isdisjoint(op.path for op in selected.operations))
        self.assertEqual(snapshot(self.root), before)
        self.confirm(QMessageBox.Apply)
        self.wait_until(lambda: self.window.worker is None)
        self.assertIn("успешно", self.window.status.text())
        after = snapshot(self.root)
        for name in paths:
            self.assertEqual(after[name], before[name])
        self.assertTrue((self.root / "include/demo_lib/foo.h").is_file())

    def test_validation_focus_preserved_input_and_recovery(self):
        before = snapshot(self.root)
        for name, namespace, field in (("", "demo::lib", "project_name"),
                                        (" ", "demo::lib", "project_name"),
                                        (" demo_lib", "demo::lib", "project_name"),
                                        ("demo_lib ", "demo::lib", "project_name"),
                                        ("123-lib", "demo::lib", "project_name"),
                                        ("demo_lib", "demo::", "namespace")):
            with self.subTest(name=name, namespace=namespace):
                self.window.project_name.setText(name)
                self.window.namespace.setText(namespace)
                self.window.codestyle.setCurrentText("llvm")
                QTest.mouseClick(self.window.preview_button, Qt.LeftButton)
                self.wait_until(lambda: self.window.worker is None)
                self.assertTrue(self.window.error_labels[field].text())
                self.assertTrue(getattr(self.window, field).hasFocus())
                self.assertEqual(self.window.project_name.text(), name)
                self.assertEqual(self.window.namespace.text(), namespace)
                self.assertEqual(self.window.codestyle.currentText(), "llvm")
                self.assertFalse(self.window.apply_button.isEnabled())
                self.assertEqual(snapshot(self.root), before)
        self.window.namespace.setText("demo::lib")
        self.make_preview()
        self.assertTrue(all(not label.text() for label in self.window.error_labels.values()))
        self.assertEqual(snapshot(self.root), before)

    def test_tab_order_and_enter_in_field_do_not_apply(self):
        self.make_preview()
        before = snapshot(self.root)
        self.window.project_name.setFocus()
        QTest.keyClick(self.window.project_name, Qt.Key_Tab)
        self.assertTrue(self.window.namespace.hasFocus())
        QTest.keyClick(self.window.namespace, Qt.Key_Tab)
        self.assertTrue(self.window.codestyle.hasFocus())
        for first, second in ((self.window.codestyle, self.window.keep_bin),
                              (self.window.keep_bin, self.window.keep_examples),
                              (self.window.keep_examples, self.window.preview_button),
                              (self.window.preview_button, self.window.apply_button)):
            QTest.keyClick(first, Qt.Key_Tab)
            self.assertTrue(second.hasFocus())
        with patch.object(bootstrap, "apply", wraps=bootstrap.apply) as apply:
            self.window.namespace.setFocus()
            QTest.keyClick(self.window.namespace, Qt.Key_Return)
            self.app.processEvents()
            self.assertEqual(apply.call_count, 0)
            self.assertEqual(snapshot(self.root), before)

    def test_each_field_change_and_return_invalidates_preview(self):
        for field, changed in (("project_name", "other"), ("namespace", "other"),
                               ("codestyle", "llvm"), ("keep_bin", False), ("keep_examples", True)):
            with self.subTest(field=field):
                self.make_preview()
                widget = getattr(self.window, field)
                if field == "codestyle":
                    original = widget.currentText()
                    widget.setCurrentText(changed)
                    widget.setCurrentText(original)
                elif field.startswith("keep_"):
                    original = widget.isChecked()
                    widget.setChecked(changed)
                    widget.setChecked(original)
                else:
                    original = widget.text()
                    widget.setText(changed)
                    widget.setText(original)
                self.assertIsNone(self.window.current_preview)
                self.assertFalse(self.window.apply_button.isEnabled())
                self.assertFalse(self.window.operations.toPlainText())

    def test_empty_preview_cannot_apply(self):
        empty = bootstrap.Preview(self.root, bootstrap.Settings("demo_lib", "demo_lib"), ())
        with patch.object(bootstrap, "preview", return_value=empty):
            self.make_preview()
        self.assertEqual(self.window.status.text(), "Нет изменений")
        self.assertFalse(self.window.apply_button.isEnabled())

    def test_operation_order_long_paths_and_scrollbars(self):
        directory = self.root / "src" / ("long_" + "x" * 65)
        directory.mkdir()
        (directory / ("y" * 65 + ".cpp")).write_text("__PROJECT_NAMESPACE__", encoding="utf-8")
        before = snapshot(self.root)
        selected = self.make_preview()
        lines = self.window.operations.toPlainText().splitlines()
        self.assertEqual(len(lines), len(selected.operations))
        for line, operation in zip(lines, selected.operations):
            self.assertIn(operation.kind, line)
            self.assertIn(operation.target_kind, line)
            self.assertIn(operation.path, line)
            if operation.new_path:
                self.assertIn(operation.new_path, line)
        self.wait_until(lambda: self.window.operations.horizontalScrollBar().maximum() > 0)
        self.assertEqual(snapshot(self.root), before)

    def test_preview_worker_responsive_and_close_deferred_until_finished(self):
        entered, release = threading.Event(), threading.Event()
        threads = []
        original = bootstrap.preview

        def delayed(*args):
            threads.append(threading.get_ident())
            entered.set()
            if not release.wait(5):
                raise RuntimeError("Test did not release worker")
            return original(*args)

        self.window.project_name.setText("demo_lib")
        before = snapshot(self.root)
        with patch.object(bootstrap, "preview", side_effect=delayed):
            try:
                QTest.mouseClick(self.window.preview_button, Qt.LeftButton)
                self.wait_until(entered.is_set)
                worker = self.window.worker
                finished = QSignalSpy(worker.finished)
                self.assertEqual(self.window.status.text(), "Подготовка")
                for widget in (*self.window._fields, self.window.preview_button, self.window.apply_button):
                    self.assertFalse(widget.isEnabled())
                ticks = []
                QTimer.singleShot(0, lambda: ticks.append(True))
                self.wait_until(lambda: bool(ticks))
                self.assertNotEqual(threads[0], threading.get_ident())
                self.window.close()
                self.assertTrue(self.window.isVisible())
                self.assertIs(self.window.worker, worker)
                self.assertEqual(finished.count(), 0)
            finally:
                release.set()
                self.wait_until(lambda: self.window.worker is None)
        self.assertEqual(finished.count(), 1)
        self.assertFalse(self.window.isVisible())
        self.assertEqual(snapshot(self.root), before)

    def test_apply_worker_responsive_and_close_deferred(self):
        selected = self.make_preview()
        entered, release = threading.Event(), threading.Event()
        original = bootstrap.apply
        received = []

        def delayed(value):
            received.append(value)
            entered.set()
            if not release.wait(5):
                raise RuntimeError("Test did not release worker")
            return original(value)

        with patch.object(bootstrap, "apply", side_effect=delayed) as apply:
            try:
                self.confirm(QMessageBox.Apply)
                self.wait_until(entered.is_set)
                self.assertIs(received[0], selected)
                self.assertIsNone(self.window.current_preview)
                self.assertEqual(self.window.status.text(), "Выполняется")
                for widget in (*self.window._fields, self.window.preview_button, self.window.apply_button):
                    self.assertFalse(widget.isEnabled())
                QTest.mouseClick(self.window.apply_button, Qt.LeftButton)
                ticks = []
                QTimer.singleShot(0, lambda: ticks.append(True))
                self.wait_until(lambda: bool(ticks))
                self.assertEqual(apply.call_count, 1)
                self.window.close()
                self.assertTrue(self.window.isVisible())
            finally:
                release.set()
                self.wait_until(lambda: self.window.worker is None)
        self.assertFalse(self.window.isVisible())
        self.assertTrue((self.root / "include/demo_lib/foo.h").is_file())

    def test_apply_error_warns_partial_changes_without_success(self):
        self.make_preview()
        error = bootstrap.BootstrapError("write denied", stage="apply", path=".editorconfig")
        with patch.object(bootstrap, "apply", side_effect=error) as apply:
            self.confirm(QMessageBox.Apply)
            self.wait_until(lambda: self.window.worker is None)
        self.assertEqual(apply.call_count, 1)
        self.assertEqual(self.window.status.text(), "Ошибка")
        text = self.window.result.toPlainText()
        for message in ("apply", "write denied", ".editorconfig", "частичные изменения", "Проверьте файлы"):
            self.assertIn(message, text)
        self.assertNotIn("успешно", text)
        self.assertIsNone(self.window.current_preview)
        self.assertFalse(self.window.apply_button.isEnabled())
        self.assertTrue(self.window.project_name.isEnabled())

    def test_real_preview_structure_read_errors_and_recovery(self):
        required = self.root / "src/CMakeLists.txt"
        saved = required.read_bytes()
        required.unlink()
        before = snapshot(self.root)
        self.window.project_name.setText("demo_lib")
        QTest.mouseClick(self.window.preview_button, Qt.LeftButton)
        self.wait_until(lambda: self.window.worker is None)
        self.assertIn("src/CMakeLists.txt", self.window.result.toPlainText())
        self.assertIn("preview", self.window.result.toPlainText())
        self.assertTrue(self.window.preview_button.isEnabled())
        self.assertEqual(snapshot(self.root), before)
        required.write_bytes(saved)
        before = snapshot(self.root)
        with patch.object(Path, "read_text", side_effect=PermissionError("read denied")):
            QTest.mouseClick(self.window.preview_button, Qt.LeftButton)
            self.wait_until(lambda: self.window.worker is None)
        self.assertIn("read denied", self.window.result.toPlainText())
        self.assertIn("path:", self.window.result.toPlainText())
        self.assertFalse(self.window.apply_button.isEnabled())
        self.assertEqual(snapshot(self.root), before)
        self.make_preview()
        self.assertFalse(self.window.result.toPlainText())
        self.assertEqual(snapshot(self.root), before)

    def test_defaults_and_real_preview_without_writes(self):
        window = self.window
        self.assertEqual(window.project_name.text(), "")
        self.assertEqual(window.namespace.text(), "")
        self.assertEqual(window.codestyle.currentText(), "google")
        self.assertEqual([window.codestyle.itemText(i) for i in range(window.codestyle.count())],
                         sorted(bootstrap.CLANG_FORMAT_PRESETS))
        self.assertTrue(window.keep_bin.isChecked())
        self.assertFalse(window.keep_examples.isChecked())
        self.assertTrue(window.root_display.isReadOnly())
        self.assertEqual(Path(window.root_display.text()), self.root)
        self.assertFalse(window.apply_button.isEnabled())
        self.assertIn("Предпросмотр ещё не выполнен", window.status.text())
        before = snapshot(self.root)
        preview = self.make_preview()
        self.assertEqual(preview.settings.namespace, "demo_lib")
        self.assertTrue(window.apply_button.isEnabled())
        for op in preview.operations:
            self.assertIn(op.path, window.operations.toPlainText())
            if op.new_path:
                self.assertIn(op.new_path, window.operations.toPlainText())
        self.assertEqual(snapshot(self.root), before)


if __name__ == "__main__":
    unittest.main()
