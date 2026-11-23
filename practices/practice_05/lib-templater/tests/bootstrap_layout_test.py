#!/usr/bin/env python3
"""
Bootstrap layout test for Feature B.

Requirements after bootstrap (project_name=demo_lib):
- include/demo_lib/foo.h exists
- include/foo.h does not exist

Runs bootstrap in a TemporaryDirectory, copying the minimal template
files needed for tools/bootstrap.py to operate.
Uses only Python standard library.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def copy_minimal_template(src_root: Path, dst_root: Path) -> None:
    # Minimal set required by bootstrap.validate_layout()
    required_dirs = [
        (src_root / "tools", dst_root / "tools"),
        (src_root / "src", dst_root / "src"),
        (src_root / "tests", dst_root / "tests"),
        (src_root / "cmake", dst_root / "cmake"),
        (src_root / "include", dst_root / "include"),
    ]
    for src, dst in required_dirs:
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)

    # Root CMakeLists.txt
    shutil.copy2(src_root / "CMakeLists.txt", dst_root / "CMakeLists.txt")


def run_bootstrap(root: Path) -> subprocess.CompletedProcess:
    cmd = [
        sys.executable,
        str(root / "tools" / "bootstrap.py"),
        "demo_lib",
        "--namespace",
        "demo_lib",
        "--codestyle",
        "google",
        "--editorconfig",
        "match-codestyle",
        "--no-bin",
        "--no-examples",
    ]
    return subprocess.run(
        cmd,
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    template_root = repo_root

    with TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        copy_minimal_template(template_root, tmp_root)

        proc = run_bootstrap(tmp_root)
        if proc.returncode != 0:
            sys.stderr.write("bootstrap failed.\n")
            sys.stderr.write(proc.stderr)
            return 1

        want = tmp_root / "include" / "demo_lib" / "foo.h"
        not_want = tmp_root / "include" / "foo.h"

        if not want.exists():
            sys.stderr.write(
                f"FAIL: expected path missing: {want.as_posix()}\n"
            )
            return 1

        if not_want.exists():
            sys.stderr.write(
                f"FAIL: unexpected path present: {not_want.as_posix()}\n"
            )
            return 1

        print("PASS: bootstrap layout")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
