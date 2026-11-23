"""Preview contract checks, using isolated copies and no Qt dependency."""

import dataclasses
from contextlib import ExitStack
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from bootstrap_cli_test import add_service_files, copy_template, snapshot

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import bootstrap


class BootstrapLogicTest(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        copy_template(self.root)

    def settings(self, **changes):
        return bootstrap.Settings(**{"project_name": "demo_lib", **changes})

    def test_service_files_preserved_and_preview_matches_apply(self):
        paths = add_service_files(self.root)
        normal = self.root / "src/specs/ordinary.cpp"
        normal.parent.mkdir()
        normal.write_text("__PROJECT_NAME__", encoding="utf-8")
        (self.root / "examples").mkdir()
        (self.root / "examples/old.txt").write_text("__PROJECT_NAME__", encoding="utf-8")
        before = snapshot(self.root)
        selected = bootstrap.preview(self.root, self.settings())
        self.assertEqual(snapshot(self.root), before)
        self.assertTrue(set(paths).isdisjoint(op.path for op in selected.operations))
        self.assertIn("src/specs/ordinary.cpp", [op.path for op in selected.operations])
        actions = []
        original_write, original_mkdir, original_rename = Path.write_text, Path.mkdir, Path.rename
        original_remove = bootstrap.shutil.rmtree

        def write(path, text, *args, **kwargs):
            actions.append(bootstrap.Operation("update" if path.exists() else "create", "file",
                                                path.relative_to(self.root).as_posix()))
            return original_write(path, text, *args, **kwargs)

        def mkdir(path, *args, **kwargs):
            existed = path.exists()
            result = original_mkdir(path, *args, **kwargs)
            if not existed:
                actions.append(bootstrap.Operation("create", "directory", path.relative_to(self.root).as_posix()))
            return result

        def rename(path, destination):
            actions.append(bootstrap.Operation("rename", "directory" if path.is_dir() else "file",
                                                path.relative_to(self.root).as_posix(),
                                                destination.relative_to(self.root).as_posix()))
            return original_rename(path, destination)

        def remove(path, *args, **kwargs):
            actions.append(bootstrap.Operation("delete", "directory", path.relative_to(self.root).as_posix()))
            return original_remove(path, *args, **kwargs)

        with patch.object(Path, "write_text", write), patch.object(Path, "mkdir", mkdir), \
             patch.object(Path, "rename", rename), patch.object(bootstrap.shutil, "rmtree", remove):
            bootstrap.apply(selected)
        self.assertEqual(tuple(actions), selected.operations)
        after = snapshot(self.root)
        for name in paths:
            self.assertEqual(after[name], before[name])
        self.assertEqual(normal.read_text(encoding="utf-8"), "demo_lib")

    def test_excluded_files_are_not_read_even_with_invalid_utf8(self):
        paths = add_service_files(self.root)
        for name in paths:
            (self.root / name).write_bytes(b"\xff")
        before = snapshot(self.root)
        original = Path.read_text

        def read(path, *args, **kwargs):
            if path.relative_to(self.root).as_posix() in paths:
                raise PermissionError("Service file must not be read")
            return original(path, *args, **kwargs)

        with patch.object(Path, "read_text", read):
            selected = bootstrap.preview(self.root, self.settings(keep_bin=False))
            bootstrap.apply(selected)
        for name in paths:
            self.assertEqual((self.root / name).read_bytes(), before[name])

    def test_generated_tests_link_effective_project_target(self):
        selected = bootstrap.preview(self.root, self.settings(keep_bin=False))
        bootstrap.apply(selected)
        cmake = (self.root / "tests/CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("demo_lib::demo_lib", cmake)
        self.assertNotIn("__PROJECT_NAME__::__PROJECT_NAME__", cmake)

    def test_apply_uses_preview_and_returns_summary(self):
        result = bootstrap.preview(self.root, self.settings(keep_bin=False))
        with patch("builtins.input", side_effect=AssertionError("input")), \
             patch("builtins.print", side_effect=AssertionError("print")), \
             patch("sys.exit", side_effect=AssertionError("exit")):
            applied = bootstrap.apply(result)
        self.assertIsInstance(applied, bootstrap.ApplyResult)
        self.assertTrue(applied.summary)
        self.assertTrue((self.root / "include/demo_lib/foo.h").is_file())
        self.assertFalse((self.root / "include/foo.h").exists())
        with self.assertRaises(TypeError):
            bootstrap.apply(result, self.settings())

    def test_apply_first_write_failure_stops(self):
        result = bootstrap.preview(self.root, self.settings())
        before = snapshot(self.root)
        with patch.object(Path, "write_text", side_effect=PermissionError("write denied")) as write:
            with self.assertRaises(bootstrap.BootstrapError) as caught:
                bootstrap.apply(result)
        self.assertEqual(write.call_count, 1)
        self.assertEqual(caught.exception.stage, "apply")
        self.assertIn(".clang-format", caught.exception.path)
        self.assertIn("write denied", caught.exception.message)
        self.assertEqual(snapshot(self.root), before)

    def test_demo_lib_and_immutable_binding(self):
        settings = self.settings()
        self.assertEqual([f.name for f in dataclasses.fields(settings)],
                         ["project_name", "namespace", "codestyle", "keep_bin", "keep_examples"])
        self.assertEqual((settings.namespace, settings.codestyle, settings.keep_bin,
                          settings.keep_examples), ("", "google", True, False))
        before = snapshot(self.root)
        with patch("builtins.input", side_effect=AssertionError("input")), \
             patch("builtins.print", side_effect=AssertionError("print")), \
             patch("sys.exit", side_effect=AssertionError("exit")):
            result = bootstrap.preview(self.root, settings)
        self.assertEqual(result.root, self.root.resolve())
        self.assertEqual(result.settings.namespace, "demo_lib")
        self.assertEqual(settings.namespace, "")
        self.assertIsInstance(result.operations, tuple)
        self.assertTrue(result.operations)
        for obj, attr, value in ((settings, "project_name", "other"),
                                 (result, "operations", ()),
                                 (result.operations[0], "path", "other"),
                                 (bootstrap.ApplyResult("Done"), "summary", "other")):
            with self.assertRaises(dataclasses.FrozenInstanceError):
                setattr(obj, attr, value)
        for op in result.operations:
            self.assertIn(op.kind, ("create", "update", "rename", "delete"))
            self.assertIn(op.target_kind, ("file", "directory"))
            self.assertFalse(Path(op.path).is_absolute())
            self.assertEqual(op.new_path is not None, op.kind == "rename")
        self.assertIn(bootstrap.Operation("rename", "directory", "include/__PROJECT_NAME__",
                                          "include/demo_lib"), result.operations)
        self.assertEqual(snapshot(self.root), before)

    def test_styles_namespace_and_repeatability(self):
        before = snapshot(self.root)
        for style in ("chromium", "google", "llvm", "microsoft", "mozilla", "webkit"):
            with self.subTest(style=style):
                settings = self.settings(codestyle=style, namespace="demo::lib")
                first = bootstrap.preview(self.root, settings)
                self.assertEqual(first, bootstrap.preview(self.root, settings))
                self.assertEqual(first.settings, settings)
                self.assertEqual(snapshot(self.root), before)

    def test_invalid_fields_without_trim(self):
        before = snapshot(self.root)
        for field, values in {
            "project_name": ("", " ", "9demo", "123-lib", " demo", "demo "),
            "namespace": ("demo::", "demo:::lib", " demo", "demo "),
            "codestyle": ("unknown", "Google", " google"),
        }.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    with self.assertRaises(bootstrap.BootstrapError) as caught:
                        bootstrap.preview(self.root, self.settings(**{field: value}))
                    error = caught.exception
                    self.assertEqual((error.stage, error.field), ("validation", field))
                    self.assertTrue(error.message)
                    self.assertEqual(str(error), error.message)
                    self.assertEqual(snapshot(self.root), before)

    def test_missing_required_files_listed_without_changes(self):
        missing = ("CMakeLists.txt", "src/CMakeLists.txt", "tests/CMakeLists.txt",
                   "cmake/__PROJECT_NAME__Config.cmake.in")
        for name in missing:
            (self.root / name).unlink()
        before = snapshot(self.root)
        with self.assertRaises(bootstrap.BootstrapError) as caught:
            bootstrap.preview(self.root, self.settings())
        self.assertEqual(caught.exception.stage, "preview")
        for name in missing:
            self.assertIn(name, caught.exception.message)
        self.assertEqual(snapshot(self.root), before)

    def test_later_bin_stage_reads_prepared_cmake(self):
        path = self.root / "CMakeLists.txt"
        path.write_text(path.read_text(encoding="utf-8").replace(
            "add_subdirectory(bin)", "add_subdirectory(__PROJECT_NAME__)"), encoding="utf-8")
        before = snapshot(self.root)
        result = bootstrap.preview(self.root, self.settings(project_name="bin"))
        updates = [op for op in result.operations if op.path == "CMakeLists.txt"]
        self.assertEqual(updates, [bootstrap.Operation("update", "file", "CMakeLists.txt")])
        self.assertEqual(snapshot(self.root), before)

    def test_read_and_decode_errors_have_path_without_changes(self):
        path = self.root / "src/broken.cpp"
        path.write_bytes(b"\xff")
        before = snapshot(self.root)
        with self.assertRaises(bootstrap.BootstrapError) as caught:
            bootstrap.preview(self.root, self.settings())
        self.assertEqual(caught.exception.stage, "preview")
        self.assertIn("broken.cpp", caught.exception.path)
        self.assertTrue(caught.exception.message)
        self.assertEqual(snapshot(self.root), before)
        path.unlink()
        before = snapshot(self.root)
        with patch.object(Path, "read_text", side_effect=PermissionError("read denied")):
            with self.assertRaises(bootstrap.BootstrapError) as caught:
                bootstrap.preview(self.root, self.settings())
        self.assertEqual(caught.exception.stage, "preview")
        self.assertTrue(caught.exception.path)
        self.assertIn("read denied", caught.exception.message)
        self.assertEqual(snapshot(self.root), before)

    def test_preview_prepared_style_files_and_new_gitignore(self):
        for name in (".clang-format", ".editorconfig", ".gitignore"):
            (self.root / name).unlink()
        before = snapshot(self.root)
        with patch.dict(bootstrap.CLANG_FORMAT_PRESETS["google"], {"BasedOnStyle": "__PROJECT_NAME__"}), \
             patch.dict(bootstrap.EDITORCONFIG_PRESETS["google"]["default"], {"charset": "__PROJECT_NAMESPACE__"}):
            result = bootstrap.preview(self.root, self.settings())
        for name in (".clang-format", ".editorconfig"):
            self.assertEqual([op.kind for op in result.operations if op.path == name], ["create", "update"])
        self.assertEqual([op.kind for op in result.operations if op.path == ".gitignore"], ["create"])
        self.assertEqual(snapshot(self.root), before)

    def test_preview_repeated_gitignore_and_tests_updates(self):
        (self.root / ".gitignore").write_text("__PROJECT_NAME__\n", encoding="utf-8")
        before = snapshot(self.root)
        result = bootstrap.preview(self.root, self.settings())
        for name in (".gitignore", "tests/CMakeLists.txt"):
            self.assertEqual([op.kind for op in result.operations if op.path == name], ["update", "update"])
        self.assertEqual(snapshot(self.root), before)

    def test_preview_optional_directories_and_parent_order(self):
        for existing in (False, True):
            for keep_bin in (False, True):
                for keep_examples in (False, True):
                    with self.subTest(existing=existing, bin=keep_bin, examples=keep_examples), TemporaryDirectory() as tmp:
                        root = Path(tmp)
                        copy_template(root)
                        if existing:
                            for name in ("bin", "examples"):
                                (root / name).mkdir()
                                (root / name / "old.cpp").write_text("__PROJECT_NAME__", encoding="utf-8")
                        before = snapshot(root)
                        settings = self.settings(keep_bin=keep_bin, keep_examples=keep_examples)
                        result = bootstrap.preview(root, settings)
                        self.assertEqual(result, bootstrap.preview(root, settings))
                        self.assertEqual(snapshot(root), before)
                        for name, keep in (("bin", keep_bin), ("examples", keep_examples)):
                            if keep:
                                file_op = bootstrap.Operation("create", "file", name + "/CMakeLists.txt")
                                self.assertIn(file_op, result.operations)
                                if not existing:
                                    parent_op = bootstrap.Operation("create", "directory", name)
                                    self.assertLess(result.operations.index(parent_op), result.operations.index(file_op))
                            else:
                                deletes = [op for op in result.operations if op.kind == "delete" and op.path == name]
                                self.assertEqual(deletes, [bootstrap.Operation("delete", "directory", name)] if existing else [])

    def test_preview_never_calls_writers_even_on_read_failure(self):
        before = snapshot(self.root)
        for error in (None, PermissionError("read denied"), UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid")):
            with self.subTest(error=error), ExitStack() as stack:
                for name in ("write_text", "write_bytes", "mkdir", "rename", "unlink"):
                    stack.enter_context(patch.object(Path, name, side_effect=AssertionError("write attempted")))
                stack.enter_context(patch.object(bootstrap.shutil, "rmtree", side_effect=AssertionError("delete attempted")))
                if error:
                    stack.enter_context(patch.object(Path, "read_text", side_effect=error))
                    with self.assertRaises(bootstrap.BootstrapError):
                        bootstrap.preview(self.root, self.settings())
                else:
                    bootstrap.preview(self.root, self.settings())
            self.assertEqual(snapshot(self.root), before)

    def test_apply_read_decode_rename_and_delete_failures_stop(self):
        for failure in ("read", "decode", "rename", "delete", "write"):
            with self.subTest(failure=failure), TemporaryDirectory() as tmp:
                root = Path(tmp)
                copy_template(root)
                (root / "bin").mkdir()
                (root / "bin/old.txt").write_text("old", encoding="utf-8")
                (root / "examples").mkdir()
                (root / "examples/old.txt").write_text("old", encoding="utf-8")
                selected = bootstrap.preview(root, self.settings(keep_bin=False))
                original_write = Path.write_text
                writes = []

                def write(path, text, *args, **kwargs):
                    writes.append(path)
                    if failure == "write" and path.name == ".editorconfig":
                        raise PermissionError("injected write")
                    return original_write(path, text, *args, **kwargs)

                with ExitStack() as stack:
                    stack.enter_context(patch.object(Path, "write_text", write))
                    if failure in ("read", "decode"):
                        error = (PermissionError("injected read") if failure == "read" else
                                 UnicodeDecodeError("utf-8", b"\xff", 0, 1, "injected decode"))
                        stack.enter_context(patch.object(Path, "read_text", side_effect=error))
                    elif failure == "rename":
                        rename = stack.enter_context(patch.object(Path, "rename", side_effect=PermissionError("injected rename")))
                    elif failure == "delete":
                        delete = stack.enter_context(patch.object(bootstrap.shutil, "rmtree", side_effect=PermissionError("injected delete")))
                    with self.assertRaises(bootstrap.BootstrapError) as caught:
                        bootstrap.apply(selected)
                error = caught.exception
                self.assertEqual(error.stage, "apply")
                self.assertTrue(error.path)
                self.assertIn("injected", error.message)
                if failure in ("read", "decode"):
                    self.assertEqual([p.name for p in writes], [".clang-format", ".editorconfig"])
                if failure == "write":
                    self.assertEqual([p.name for p in writes], [".clang-format", ".editorconfig"])
                    self.assertIn(".editorconfig", error.path)
                if failure == "rename":
                    self.assertEqual(rename.call_count, 1)
                    self.assertIn("Config.cmake.in", error.path)
                    self.assertTrue((root / "include/__PROJECT_NAME__").is_dir())
                if failure == "delete":
                    self.assertEqual(delete.call_count, 1)
                    self.assertIn("bin", error.path)
                self.assertTrue((root / "examples/old.txt").is_file())
                self.assertTrue((root / "bin/old.txt").is_file())
                self.assertNotEqual((root / ".clang-format").read_bytes(),
                                    (Path(__file__).resolve().parents[1] / ".clang-format").read_bytes())


if __name__ == "__main__":
    unittest.main()
