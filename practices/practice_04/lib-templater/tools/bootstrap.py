#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

TEMPLATE_PROJECT_NAME = "__PROJECT_NAME__"
TEMPLATE_NAMESPACE = "__PROJECT_NAMESPACE__"

TEXT_FILE_EXTENSIONS = {
    ".txt",
    ".md",
    ".cmake",
    ".cpp",
    ".cxx",
    ".cc",
    ".c",
    ".hpp",
    ".hxx",
    ".hh",
    ".h",
    ".ipp",
    ".inl",
    ".ixx",
    ".py",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".gitignore",
}

SKIP_DIRS = {
    ".git",
    ".idea",
    ".vs",
    ".vscode",
    "build",
    "cmake-build-debug",
    "cmake-build-release",
    "cmake-build-relwithdebinfo",
    "cmake-build-minsizerel",
    "out",
    "dist",
    "__pycache__",
}

CLANG_FORMAT_PRESETS = {
    "google": {
        "BasedOnStyle": "Google",
        "IndentWidth": 2,
        "TabWidth": 2,
        "UseTab": "Never",
        "ColumnLimit": 80,
        "DerivePointerAlignment": False,
        "PointerAlignment": "Left",
        "SortIncludes": True,
        "IncludeBlocks": "Regroup",
        "AllowShortFunctionsOnASingleLine": "Empty",
        "SpacesInParentheses": False,
        "SpaceBeforeParens": "ControlStatements",
        "BreakConstructorInitializersBeforeComma": True,
    },
    "llvm": {
        "BasedOnStyle": "LLVM",
        "IndentWidth": 2,
        "TabWidth": 2,
        "UseTab": "Never",
        "ColumnLimit": 80,
        "DerivePointerAlignment": False,
        "PointerAlignment": "Left",
        "SortIncludes": True,
        "IncludeBlocks": "Regroup",
    },
    "chromium": {
        "BasedOnStyle": "Chromium",
        "IndentWidth": 2,
        "TabWidth": 2,
        "UseTab": "Never",
        "ColumnLimit": 80,
        "SortIncludes": True,
        "IncludeBlocks": "Regroup",
    },
    "mozilla": {
        "BasedOnStyle": "Mozilla",
        "IndentWidth": 2,
        "TabWidth": 2,
        "UseTab": "Never",
        "ColumnLimit": 80,
        "SortIncludes": True,
        "IncludeBlocks": "Regroup",
    },
    "webkit": {
        "BasedOnStyle": "WebKit",
        "IndentWidth": 4,
        "TabWidth": 4,
        "UseTab": "Never",
        "ColumnLimit": 100,
        "SortIncludes": True,
        "IncludeBlocks": "Regroup",
    },
    "microsoft": {
        "BasedOnStyle": "Microsoft",
        "IndentWidth": 4,
        "TabWidth": 4,
        "UseTab": "Never",
        "ColumnLimit": 120,
        "SortIncludes": True,
        "IncludeBlocks": "Regroup",
    },
}

EDITORCONFIG_PRESETS = {
    "google": {
        "default": {
            "indent_style": "space",
            "indent_size": 2,
            "tab_width": 2,
            "charset": "utf-8",
            "trim_trailing_whitespace": True,
            "insert_final_newline": True,
        },
        "cpp": {
            "indent_style": "space",
            "indent_size": 2,
            "tab_width": 2,
            "charset": "utf-8",
            "trim_trailing_whitespace": True,
            "insert_final_newline": True,
        },
    },
    "llvm": {
        "default": {
            "indent_style": "space",
            "indent_size": 2,
            "tab_width": 2,
            "charset": "utf-8",
            "trim_trailing_whitespace": True,
            "insert_final_newline": True,
        },
        "cpp": {
            "indent_style": "space",
            "indent_size": 2,
            "tab_width": 2,
            "charset": "utf-8",
            "trim_trailing_whitespace": True,
            "insert_final_newline": True,
        },
    },
    "chromium": {
        "default": {
            "indent_style": "space",
            "indent_size": 2,
            "tab_width": 2,
            "charset": "utf-8",
            "trim_trailing_whitespace": True,
            "insert_final_newline": True,
        },
        "cpp": {
            "indent_style": "space",
            "indent_size": 2,
            "tab_width": 2,
            "charset": "utf-8",
            "trim_trailing_whitespace": True,
            "insert_final_newline": True,
        },
    },
    "mozilla": {
        "default": {
            "indent_style": "space",
            "indent_size": 2,
            "tab_width": 2,
            "charset": "utf-8",
            "trim_trailing_whitespace": True,
            "insert_final_newline": True,
        },
        "cpp": {
            "indent_style": "space",
            "indent_size": 2,
            "tab_width": 2,
            "charset": "utf-8",
            "trim_trailing_whitespace": True,
            "insert_final_newline": True,
        },
    },
    "webkit": {
        "default": {
            "indent_style": "space",
            "indent_size": 4,
            "tab_width": 4,
            "charset": "utf-8",
            "trim_trailing_whitespace": True,
            "insert_final_newline": True,
        },
        "cpp": {
            "indent_style": "space",
            "indent_size": 4,
            "tab_width": 4,
            "charset": "utf-8",
            "trim_trailing_whitespace": True,
            "insert_final_newline": True,
        },
    },
    "microsoft": {
        "default": {
            "indent_style": "space",
            "indent_size": 4,
            "tab_width": 4,
            "charset": "utf-8",
            "trim_trailing_whitespace": True,
            "insert_final_newline": True,
        },
        "cpp": {
            "indent_style": "space",
            "indent_size": 4,
            "tab_width": 4,
            "charset": "utf-8",
            "trim_trailing_whitespace": True,
            "insert_final_newline": True,
        },
    },
}


BIN_CMAKELISTS_TEMPLATE = """add_executable(__PROJECT_NAME__BIN__
    main.cpp
)

target_link_libraries(__PROJECT_NAME__BIN__
    PRIVATE
        __PROJECT_NAME__::__PROJECT_NAME__
)

set_target_properties(__PROJECT_NAME__BIN__ PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    OUTPUT_NAME "main"
)
"""

BIN_MAIN_TEMPLATE = """#include <iostream>

int main() {
    std::cout << "Kittens!";
    return 0;
}
"""

EXAMPLES_CMAKELISTS_TEMPLATE = """add_executable(__PROJECT_NAME__EXAMPLE__
    basic_usage.cpp
)

target_link_libraries(__PROJECT_NAME__EXAMPLE__
    PRIVATE
        __PROJECT_NAME__::__PROJECT_NAME__
)

set_target_properties(__PROJECT_NAME__EXAMPLE__ PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/examples"
    OUTPUT_NAME "basic_usage"
)
"""

EXAMPLES_MAIN_TEMPLATE = """#include <iostream>

int main() {
    std::cout << "Kittens!";
    return 0;
}
"""


@dataclass(frozen=True)
class Options:
    project_name: str
    namespace: str
    codestyle: str
    editorconfig: str
    keep_bin: bool
    keep_examples: bool
    dry_run: bool


class BootstrapError(RuntimeError):
    pass


def detect_project_root() -> Path:
    script_dir = Path(__file__).resolve().parent
    candidates = [script_dir, script_dir.parent]
    for candidate in candidates:
        if (candidate / "CMakeLists.txt").exists() and (candidate / "src").exists():
            return candidate
    return script_dir


ROOT = detect_project_root()
SKIP_FILES = {Path(__file__).name}


class Bootstrapper:
    def __init__(self, root: Path, options: Options) -> None:
        self.root = root
        self.options = options
        self.actions: list[str] = []

    def run(self) -> None:
        self._validate_layout()
        self._write_clang_format()
        self._write_editorconfig()
        self._update_gitignore()
        self._replace_in_text_files()
        self._fix_tests_cmakelists()
        self._rename_paths()
        self._configure_bin()
        self._configure_examples()
        self._print_summary()

    def _validate_layout(self) -> None:
        required = [
            self.root / "CMakeLists.txt",
            self.root / "src" / "CMakeLists.txt",
            self.root / "tests" / "CMakeLists.txt",
            self.root / "cmake" / f"{TEMPLATE_PROJECT_NAME}Config.cmake.in",
        ]
        missing = [str(path.relative_to(self.root)) for path in required if not path.exists()]
        if missing:
            raise BootstrapError(
                "Repository layout does not match the current template. Missing: " + ", ".join(missing)
            )

    def _write_clang_format(self) -> None:
        preset = CLANG_FORMAT_PRESETS[self.options.codestyle]
        lines = []
        for key, value in preset.items():
            rendered = str(value).lower() if isinstance(value, bool) else str(value)
            lines.append(f"{key}: {rendered}")
        content = "\n".join(lines) + "\n"
        self._write_text(self.root / ".clang-format", content, "write .clang-format")

    def _write_editorconfig(self) -> None:
        preset = EDITORCONFIG_PRESETS[self.options.codestyle]
        lines = ["root = true", "", "[*]"]
        lines.extend(self._render_editorconfig_section(preset["default"]))
        lines.extend(["", "[*.{h,hpp,hh,hxx,c,cc,cpp,cxx,ixx,ipp,inl}]"])
        lines.extend(self._render_editorconfig_section(preset["cpp"]))
        content = "\n".join(lines) + "\n"
        self._write_text(self.root / ".editorconfig", content, "write .editorconfig")

    @staticmethod
    def _render_editorconfig_section(values: dict[str, object]) -> list[str]:
        result: list[str] = []
        for key, value in values.items():
            if isinstance(value, bool):
                value = str(value).lower()
            result.append(f"{key} = {value}")
        return result

    def _update_gitignore(self) -> None:
        path = self.root / ".gitignore"
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        required_lines = [".vscode/", ".idea/"]
        missing = [line for line in required_lines if line not in existing.splitlines()]
        if not missing:
            return
        suffix = ("\n" if existing and not existing.endswith("\n") else "") + "\n".join(missing) + "\n"
        self._write_text(path, existing + suffix, "update .gitignore")

    def _replace_in_text_files(self) -> None:
        replacements = self._build_replacements()
        for path in self._iter_text_files():
            original = path.read_text(encoding="utf-8")
            updated = self._apply_replacements(original, replacements)
            if updated != original:
                self._write_text(path, updated, f"replace placeholders in {path.relative_to(self.root)}")

    def _fix_tests_cmakelists(self) -> None:
        path = self.root / "tests" / "CMakeLists.txt"
        if not path.exists():
            return

        content = path.read_text(encoding="utf-8")
        content = re.sub(
            r"target_link_libraries\(__PROJECT_NAME_TESTS__\s+PRIVATE\s+[A-Za-z_][A-Za-z0-9_]*::[A-Za-z_][A-Za-z0-9_]*",
            f"target_link_libraries(__PROJECT_NAME_TESTS__\n    PRIVATE\n        __PROJECT_NAME__::__PROJECT_NAME__",
            content,
            flags=re.MULTILINE,
        )
        self._write_text(path, content, "fix tests/CMakeLists.txt target link")

    def _build_replacements(self) -> list[tuple[re.Pattern[str], str]]:
        project = self.options.project_name
        namespace = self.options.namespace
        replacements: list[tuple[re.Pattern[str], str]] = [
            (re.compile(rf"\b{re.escape(TEMPLATE_PROJECT_NAME)}Config\.cmake\.in\b"), f"{project}Config.cmake.in"),
            (re.compile(rf"\b{re.escape(TEMPLATE_PROJECT_NAME)}ConfigVersion\.cmake\b"), f"{project}ConfigVersion.cmake"),
            (re.compile(rf"\b{re.escape(TEMPLATE_PROJECT_NAME)}Targets\.cmake\b"), f"{project}Targets.cmake"),
            (re.compile(rf"\b{re.escape(TEMPLATE_PROJECT_NAME)}Targets\b"), f"{project}Targets"),
            (re.compile(rf"\b{re.escape(TEMPLATE_PROJECT_NAME)}::({re.escape(TEMPLATE_PROJECT_NAME)})\b"), f"{project}::{project}"),
            (re.compile(rf"\b{re.escape(TEMPLATE_PROJECT_NAME)}::{re.escape(TEMPLATE_PROJECT_NAME)}\b"), f"{project}::{project}"),
            (re.compile(rf"\b{re.escape(TEMPLATE_PROJECT_NAME)}\b"), project),
            (re.compile(rf"\b{re.escape(TEMPLATE_NAMESPACE)}\b"), namespace),
        ]
        return replacements

    @staticmethod
    def _apply_replacements(text: str, replacements: list[tuple[re.Pattern[str], str]]) -> str:
        result = text
        for pattern, replacement in replacements:
            result = pattern.sub(replacement, result)
        return result

    def _rename_paths(self) -> None:
        rename_pairs = [
            (
                self.root / "cmake" / f"{TEMPLATE_PROJECT_NAME}Config.cmake.in",
                self.root / "cmake" / f"{self.options.project_name}Config.cmake.in",
            ),
            (
                self.root / "include" / TEMPLATE_PROJECT_NAME,
                self.root / "include" / self.options.project_name,
            ),
        ]
        for old_path, new_path in rename_pairs:
            if old_path.exists() and old_path != new_path:
                self._rename_path(old_path, new_path)

    def _configure_bin(self) -> None:
        bin_dir = self.root / "bin"
        if self.options.keep_bin:
            self._write_text(
                bin_dir / "CMakeLists.txt",
                BIN_CMAKELISTS_TEMPLATE,
                "write bin/CMakeLists.txt",
            )
            self._write_text(
                bin_dir / "main.cpp",
                BIN_MAIN_TEMPLATE,
                "write bin/main.cpp",
            )
            self._ensure_subdirectory_block(
                option_name="BUILD_BIN",
                option_doc="Build binary targets",
                subdir_name="bin",
            )
        else:
            self._remove_path(bin_dir)
            self._remove_subdirectory_block("BUILD_BIN", "bin")

    def _configure_examples(self) -> None:
        examples_dir = self.root / "examples"
        if self.options.keep_examples:
            self._write_text(
                examples_dir / "CMakeLists.txt",
                EXAMPLES_CMAKELISTS_TEMPLATE,
                "write examples/CMakeLists.txt",
            )
            self._write_text(
                examples_dir / "basic_usage.cpp",
                EXAMPLES_MAIN_TEMPLATE,
                "write examples/basic_usage.cpp",
            )
            self._ensure_subdirectory_block(
                option_name="BUILD_EXAMPLES",
                option_doc="Build examples",
                subdir_name="examples",
            )
        else:
            self._remove_path(examples_dir)
            self._remove_subdirectory_block("BUILD_EXAMPLES", "examples")

    def _ensure_subdirectory_block(self, option_name: str, option_doc: str, subdir_name: str) -> None:
        root_cmake = self.root / "CMakeLists.txt"
        if not root_cmake.exists():
            return

        content = root_cmake.read_text(encoding="utf-8")
        block = f'option({option_name} "{option_doc}" ON)\nif({option_name})\n    add_subdirectory({subdir_name})\nendif()\n'

        if f"add_subdirectory({subdir_name})" in content:
            return

        option_pattern = re.compile(rf'option\({re.escape(option_name)}[^\n]*\)\n?', re.MULTILINE)
        if option_pattern.search(content):
            updated = option_pattern.sub(lambda m: m.group(0) + f'if({option_name})\n    add_subdirectory({subdir_name})\nendif()\n', content, count=1)
            self._write_text(root_cmake, updated, f"enable {subdir_name} in root CMakeLists.txt")
            return

        updated = content.rstrip() + "\n\n" + block
        self._write_text(root_cmake, updated, f"append {subdir_name} block to root CMakeLists.txt")

    def _remove_subdirectory_block(self, option_name: str, subdir_name: str) -> None:
        root_cmake = self.root / "CMakeLists.txt"
        if not root_cmake.exists():
            return
        content = root_cmake.read_text(encoding="utf-8")
        updated = re.sub(
            rf'\n*if\({re.escape(option_name)}\)\n\s*add_subdirectory\({re.escape(subdir_name)}\)\nendif\(\)\n?',
            '\n',
            content,
            flags=re.MULTILINE,
        )
        if updated != content:
            self._write_text(root_cmake, updated.rstrip() + "\n", f"remove {subdir_name} block from root CMakeLists.txt")

    def _iter_text_files(self) -> Iterable[Path]:
        for path in self.root.rglob("*"):
            if path.is_dir():
                continue
            if path.name in SKIP_FILES:
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if self._is_probably_text_file(path):
                yield path

    def _is_probably_text_file(self, path: Path) -> bool:
        if path.suffix.lower() in TEXT_FILE_EXTENSIONS:
            return True
        return path.name in {"CMakeLists.txt", ".clang-format", ".editorconfig", ".gitignore"}

    def _write_text(self, path: Path, content: str, action: str) -> None:
        self.actions.append(action)
        if self.options.dry_run:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _rename_path(self, old_path: Path, new_path: Path) -> None:
        self.actions.append(f"rename {old_path.relative_to(self.root)} -> {new_path.relative_to(self.root)}")
        if self.options.dry_run:
            return
        new_path.parent.mkdir(parents=True, exist_ok=True)
        old_path.rename(new_path)

    def _remove_path(self, path: Path) -> None:
        if not path.exists():
            return
        self.actions.append(f"remove {path.relative_to(self.root)}")
        if self.options.dry_run:
            return
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def _print_summary(self) -> None:
        print("Bootstrap completed." if not self.options.dry_run else "Dry run completed.")
        print()
        print("Options:")
        print(f"  project name  : {self.options.project_name}")
        print(f"  namespace     : {self.options.namespace}")
        print(f"  codestyle     : {self.options.codestyle}")
        print(f"  editorconfig  : {self.options.editorconfig}")
        print(f"  keep bin      : {self.options.keep_bin}")
        print(f"  keep examples : {self.options.keep_examples}")
        print()
        print("Applied actions:")
        for action in self.actions:
            print(f"  - {action}")


def validate_project_name(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", value):
        raise argparse.ArgumentTypeError(
            "Project name must start with a letter and contain only letters, digits and underscores."
        )
    return value


def validate_namespace(value: str) -> str:
    pattern = r"[A-Za-z_][A-Za-z0-9_]*(::[A-Za-z_][A-Za-z0-9_]*)*"
    if not re.fullmatch(pattern, value):
        raise argparse.ArgumentTypeError("Namespace must be a valid C++ namespace, for example mylib or my::lib.")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap the C++ library template.")
    parser.add_argument("project_name", nargs="?", type=validate_project_name, help="New project name.")
    parser.add_argument("--namespace", type=validate_namespace, help="Main C++ namespace. Defaults to project name.")
    parser.add_argument("--codestyle", choices=sorted(CLANG_FORMAT_PRESETS.keys()), help="clang-format preset.")
    parser.add_argument("--editorconfig", choices=["match-codestyle"], help="EditorConfig mode.")
    parser.add_argument("--keep-bin", action="store_true", help="Create or keep bin/.")
    parser.add_argument("--no-bin", action="store_true", help="Remove bin/.")
    parser.add_argument("--keep-examples", action="store_true", help="Create or keep examples/.")
    parser.add_argument("--no-examples", action="store_true", help="Remove examples/.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without modifying files.")
    parser.add_argument("--config", type=Path, help="Optional JSON config file.")
    return parser


def prompt_choice(title: str, choices: list[str], default: str) -> str:
    print(title)
    for index, choice in enumerate(choices, start=1):
        marker = " (default)" if choice == default else ""
        print(f"  {index}. {choice}{marker}")
    raw = input("> ").strip()
    if not raw:
        return default
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(choices):
            return choices[idx]
    if raw in choices:
        return raw
    raise BootstrapError(f"Invalid choice: {raw}")


def prompt_bool(title: str, default: bool) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    raw = input(f"{title} {suffix} ").strip().lower()
    if not raw:
        return default
    if raw in {"y", "yes"}:
        return True
    if raw in {"n", "no"}:
        return False
    raise BootstrapError(f"Invalid yes/no answer: {raw}")


def load_json_config(path: Path | None) -> dict[str, object]:
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BootstrapError(f"Config file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BootstrapError(f"Config file is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise BootstrapError("Config file root must be a JSON object.")
    return data


def resolve_options(args: argparse.Namespace) -> Options:
    config = load_json_config(args.config)

    project_name = args.project_name or config.get("project_name")
    if not project_name:
        project_name = validate_project_name(input("Project name: ").strip())
    else:
        project_name = validate_project_name(str(project_name))

    namespace = args.namespace or config.get("namespace")
    if namespace is None:
        namespace = validate_namespace(input(f"Namespace [{project_name}]: ").strip() or project_name)
    else:
        namespace = validate_namespace(str(namespace))

    codestyle = args.codestyle or config.get("codestyle")
    if codestyle is None:
        codestyle = prompt_choice("Choose codestyle:", sorted(CLANG_FORMAT_PRESETS.keys()), "google")
    if codestyle not in CLANG_FORMAT_PRESETS:
        raise BootstrapError(f"Unsupported codestyle: {codestyle}")

    editorconfig = args.editorconfig or config.get("editorconfig") or "match-codestyle"
    if editorconfig != "match-codestyle":
        raise BootstrapError("Unsupported EditorConfig mode. Use match-codestyle.")

    if args.keep_bin and args.no_bin:
        raise BootstrapError("Use either --keep-bin or --no-bin, not both.")
    if args.keep_examples and args.no_examples:
        raise BootstrapError("Use either --keep-examples or --no-examples, not both.")

    if args.keep_bin:
        keep_bin = True
    elif args.no_bin:
        keep_bin = False
    elif "keep_bin" in config:
        keep_bin = bool(config["keep_bin"])
    else:
        keep_bin = prompt_bool("Keep bin target?", default=True)

    if args.keep_examples:
        keep_examples = True
    elif args.no_examples:
        keep_examples = False
    elif "keep_examples" in config:
        keep_examples = bool(config["keep_examples"])
    else:
        keep_examples = prompt_bool("Keep examples target?", default=False)

    return Options(
        project_name=project_name,
        namespace=namespace,
        codestyle=str(codestyle),
        editorconfig=str(editorconfig),
        keep_bin=keep_bin,
        keep_examples=keep_examples,
        dry_run=bool(args.dry_run),
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        options = resolve_options(args)
        bootstrapper = Bootstrapper(ROOT, options)
        bootstrapper.run()
    except BootstrapError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Cancelled.", file=sys.stderr)
        return 130

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
