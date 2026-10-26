"""Regression coverage for the original bootstrap command line interface."""

import json
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]


def add_service_files(root):
    """Service fixtures deliberately contain tokens that bootstrap would replace."""
    paths = (
        "specs/002-bootstrap-logic/spec.md", ".specify/memory/constitution.md",
        ".agents/skills/example/SKILL.md", "tests/bootstrap_guard_test.py",
        ".venv/Lib/module.py", ".venv-gui/Lib/module.py", "venv/Lib/module.py",
        "environments/custom/pyvenv.cfg", "environments/custom/Lib/module.py",
    )
    for name in paths:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("__PROJECT_NAME__ __PROJECT_NAMESPACE__\n", encoding="utf-8")
    return paths


def copy_template(root):
    for name in ("src", "cmake", "include"):
        shutil.copytree(ROOT / name, root / name)
    (root / "tools").mkdir()
    shutil.copy2(ROOT / "tools/bootstrap.py", root / "tools/bootstrap.py")
    (root / "tests").mkdir()
    for name in ("CMakeLists.txt", "foo_ut.cpp"):
        shutil.copy2(ROOT / "tests" / name, root / "tests" / name)
    for name in ("CMakeLists.txt", ".clang-format", ".editorconfig", ".gitignore"):
        shutil.copy2(ROOT / name, root / name)


def snapshot(root):
    return {
        path.relative_to(root).as_posix(): None if path.is_dir() else path.read_bytes()
        for path in root.rglob("*")
    }


class BootstrapCliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        copy_template(self.root)

    def run_cli(self, args=(), stdin="", config=None):
        if config is not None:
            (self.root / "config.json").write_text(json.dumps(config), encoding="utf-8")
            args = ["--config", "config.json", *args]
        return subprocess.run(
            [sys.executable, str(self.root / "tools/bootstrap.py"), *args],
            cwd=self.root, input=stdin, text=True, capture_output=True, timeout=15,
        )

    def full_args(self):
        return ["demo_lib", "--namespace", "demo::lib", "--codestyle", "google",
                "--editorconfig", "match-codestyle", "--no-bin", "--no-examples"]

    def test_baseline_available(self):
        result = subprocess.run(
            ["git", "ls-files", "--full-name", "tools/bootstrap.py"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        self.assertEqual(result.stdout.strip(), "practices/practice_05/lib-templater/tools/bootstrap.py")
        baseline = subprocess.run(
            ["git", "show", "b768cd8:" + result.stdout.strip()],
            cwd=ROOT, capture_output=True, check=True,
        )
        self.assertIn(b"def resolve_options(", baseline.stdout)

    def test_config_errors_are_structured_before_writes(self):
        sys.path.insert(0, str(ROOT))
        from tools import bootstrap
        config_path = self.root / "config.json"
        for content, field in (("{", None), ("[]", None),
                               (json.dumps({"project_name": "9demo"}), "project_name"),
                               (json.dumps({"project_name": "demo", "namespace": ""}), "namespace"),
                               (json.dumps({"project_name": "demo", "namespace": "demo", "codestyle": "bad"}), "codestyle"),
                               (json.dumps({"project_name": "demo", "namespace": "demo", "codestyle": "google",
                                            "editorconfig": "bad"}), "editorconfig")):
            with self.subTest(content=content):
                config_path.write_text(content, encoding="utf-8")
                before = snapshot(self.root)
                args = bootstrap.build_parser().parse_args(["--config", str(config_path)])
                with patch("builtins.input", side_effect=AssertionError("unexpected prompt")):
                    with self.assertRaises(bootstrap.BootstrapError) as caught:
                        bootstrap.resolve_options(args)
                self.assertEqual(caught.exception.stage, "validation")
                self.assertEqual(caught.exception.field, field)
                self.assertEqual(caught.exception.path, str(config_path))
                self.assertEqual(snapshot(self.root), before)

    def test_flags_apply_without_confirmation(self):
        result = self.run_cli(self.full_args())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertTrue(result.stdout.startswith("Bootstrap completed.\n\nOptions:\n"))
        self.assertIn("namespace     : demo::lib", result.stdout)
        self.assertIn("Applied actions:", result.stdout)
        self.assertTrue((self.root / "include/demo_lib/foo.h").is_file())

    def test_interactive_defaults(self):
        result = self.run_cli(stdin="demo_lib\n\n\n\n\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        for prompt in ("Project name: ", "Namespace [demo_lib]: ", "Choose codestyle:",
                       "Keep bin target? [Y/n]", "Keep examples target? [y/N]"):
            self.assertIn(prompt, result.stdout)
        for value in ("namespace     : demo_lib", "codestyle     : google",
                      "keep bin      : True", "keep examples : False"):
            self.assertIn(value, result.stdout)

    def test_interactive_choices(self):
        result = self.run_cli(["demo_lib", "--namespace", "demo_lib"], "6\nn\ny\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("codestyle     : webkit", result.stdout)
        self.assertIn("keep bin      : False", result.stdout)
        self.assertIn("keep examples : True", result.stdout)

    def test_json_priority(self):
        result = self.run_cli(self.full_args(), config={
            "project_name": "other", "namespace": "other", "codestyle": "llvm",
            "editorconfig": "invalid", "keep_bin": True, "keep_examples": True,
        })
        self.assertEqual(result.returncode, 0, result.stderr)
        for value in ("project name  : demo_lib", "namespace     : demo::lib",
                      "codestyle     : google", "keep bin      : False", "keep examples : False"):
            self.assertIn(value, result.stdout)

    def test_json_coercion_unknown_keys_and_dry_run_ignored(self):
        result = self.run_cli(config={
            "project_name": "demo_lib", "namespace": 123, "codestyle": "google",
            "keep_bin": "false", "keep_examples": [], "unknown": 7, "dry_run": True,
        })
        # str(123) is still rejected by the legacy namespace validator.
        self.assertNotEqual(result.returncode, 0)
        result = self.run_cli(config={
            "project_name": True, "namespace": True, "codestyle": "google",
            "keep_bin": "false", "keep_examples": [], "unknown": 7, "dry_run": True,
        })
        self.assertEqual(result.returncode, 0, result.stderr)
        for value in ("project name  : True", "namespace     : True", "keep bin      : True",
                      "keep examples : False", "Bootstrap completed."):
            self.assertIn(value, result.stdout)
        self.assertTrue((self.root / "include/True/foo.h").exists())

    def test_json_missing_namespace_prompts(self):
        result = self.run_cli(stdin="\n", config={
            "project_name": "demo_lib", "codestyle": "google",
            "keep_bin": False, "keep_examples": False,
        })
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Namespace [demo_lib]: ", result.stdout)

    def test_json_empty_namespace_is_error_without_writes(self):
        (self.root / "config.json").write_text(json.dumps({"namespace": ""}), encoding="utf-8")
        before = snapshot(self.root)
        result = self.run_cli(["demo_lib", "--config", "config.json"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Namespace must be", result.stderr)
        self.assertEqual(snapshot(self.root), before)

    def test_conflicting_flags(self):
        for flags in (("--keep-bin", "--no-bin"), ("--keep-examples", "--no-examples")):
            with self.subTest(flags=flags):
                before = snapshot(self.root)
                result = self.run_cli([*self.full_args(), *flags])
                self.assertEqual(result.returncode, 1)
                self.assertIn("Error: Use either", result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertEqual(snapshot(self.root), before)

    def test_bad_configs(self):
        for text, message in ((None, "Config file not found:"), ("{", "Config file is not valid JSON:"),
                              ("[]", "Config file root must be a JSON object.")):
            with self.subTest(text=text):
                name = "missing.json" if text is None else "bad.json"
                if text is not None:
                    (self.root / name).write_text(text, encoding="utf-8")
                before = snapshot(self.root)
                result = self.run_cli(["--config", name])
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertIn("Error: " + message, result.stderr)
                self.assertEqual(snapshot(self.root), before)

    def test_argparse_error_and_help(self):
        result = self.run_cli(["9demo"])
        self.assertEqual(result.returncode, 2)
        self.assertIn("Project name must", result.stderr)
        result = self.run_cli(["--help"])
        self.assertEqual(result.returncode, 0)
        for flag in ("--config", "--dry-run", "--keep-bin", "--no-examples", "--editorconfig"):
            self.assertIn(flag, result.stdout)

    def test_dry_run_without_writes(self):
        before = snapshot(self.root)
        result = self.run_cli([*self.full_args(), "--dry-run"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("Dry run completed."))
        self.assertIn("rename", result.stdout)
        self.assertEqual(result.stderr, "")
        self.assertEqual(snapshot(self.root), before)

    def test_cli_still_transforms_service_files_and_fixes_cmake(self):
        paths = add_service_files(self.root)
        result = self.run_cli(self.full_args())
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in paths:
            self.assertEqual((self.root / name).read_text(encoding="utf-8"), "demo_lib demo::lib\n")
        cmake = (self.root / "tests/CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("demo_lib::demo_lib", cmake)
        self.assertNotIn("__PROJECT_NAME__::__PROJECT_NAME__", cmake)

    def test_api_and_cli_match_baseline_except_cmake_fix(self):
        sys.path.insert(0, str(ROOT))
        from tools import bootstrap
        git_path = subprocess.run(
            ["git", "ls-files", "--full-name", "tools/bootstrap.py"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        original_script = subprocess.run(
            ["git", "show", "b768cd8:" + git_path], cwd=ROOT, capture_output=True, check=True,
        ).stdout
        for keep_bin in (False, True):
            for keep_examples in (False, True):
                with self.subTest(bin=keep_bin, examples=keep_examples), TemporaryDirectory() as tmp:
                    baseline = Path(tmp) / "baseline"
                    actual = Path(tmp) / "actual"
                    cli = Path(tmp) / "cli"
                    baseline.mkdir()
                    actual.mkdir()
                    cli.mkdir()
                    for root in (baseline, actual, cli):
                        copy_template(root)
                        for name in ("bin", "examples"):
                            (root / name).mkdir()
                            (root / name / "old.cpp").write_text("__PROJECT_NAME__", encoding="utf-8")
                    (baseline / "tools/bootstrap.py").write_bytes(original_script)
                    flags = ["demo_lib", "--namespace", "demo::lib", "--codestyle", "google",
                             "--editorconfig", "match-codestyle",
                             "--keep-bin" if keep_bin else "--no-bin",
                             "--keep-examples" if keep_examples else "--no-examples"]
                    dry_runs = [subprocess.run(
                        [sys.executable, "-B", str(root / "tools/bootstrap.py"), *flags, "--dry-run"],
                        cwd=root, input="", text=True, capture_output=True, timeout=15,
                    ) for root in (baseline, actual)]
                    self.assertEqual([(p.returncode, p.stdout, p.stderr) for p in dry_runs][0],
                                     [(p.returncode, p.stdout, p.stderr) for p in dry_runs][1])
                    result = subprocess.run(
                        [sys.executable, "-B", str(baseline / "tools/bootstrap.py"), *flags],
                        cwd=baseline, input="", text=True, capture_output=True, timeout=15,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    selected = bootstrap.preview(actual, bootstrap.Settings(
                        "demo_lib", "demo::lib", "google", keep_bin, keep_examples))
                    bootstrap.apply(selected)
                    cli_result = subprocess.run(
                        [sys.executable, "-B", str(cli / "tools/bootstrap.py"), *flags],
                        cwd=cli, input="", text=True, capture_output=True, timeout=15,
                    )
                    self.assertEqual((cli_result.returncode, cli_result.stdout, cli_result.stderr),
                                     (result.returncode, result.stdout, result.stderr))
                    expected = snapshot(baseline)
                    del expected["tools/bootstrap.py"]
                    old_target = b"__PROJECT_NAME__::__PROJECT_NAME__"
                    self.assertEqual(expected["tests/CMakeLists.txt"].count(old_target), 1)
                    expected["tests/CMakeLists.txt"] = expected["tests/CMakeLists.txt"].replace(
                        old_target, b"demo_lib::demo_lib", 1)
                    for root in (actual, cli):
                        observed = snapshot(root)
                        del observed["tools/bootstrap.py"]
                        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
