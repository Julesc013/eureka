#!/usr/bin/env python3
"""Build or check tiny safe F0 fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO
from zipfile import ZIP_DEFLATED, ZipFile

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction_safe_fixtures import build_container_descriptor_from_fixture, build_member_manifest  # noqa: E402


SAFE_ZIP = Path("examples/f0/safe_zip_basic.zip")
EXPECTED_MANIFEST = Path("examples/f0/safe_zip_expected_manifest.json")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-safe-fixtures", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    built: list[str] = []
    if args.build_safe_fixtures:
        built.extend(_build_safe_zip(root))
        expected = build_member_manifest(build_container_descriptor_from_fixture(root / SAFE_ZIP))
        (root / EXPECTED_MANIFEST).write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        built.append(EXPECTED_MANIFEST.as_posix())

    errors: list[str] = []
    if args.check or args.build_safe_fixtures:
        if not (root / SAFE_ZIP).is_file():
            errors.append(f"{SAFE_ZIP.as_posix()} is missing.")
        if not (root / EXPECTED_MANIFEST).is_file():
            errors.append(f"{EXPECTED_MANIFEST.as_posix()} is missing.")
        if (root / SAFE_ZIP).is_file() and (root / SAFE_ZIP).stat().st_size > 1048576:
            errors.append("safe ZIP fixture exceeds the F0 size limit.")
        if (root / SAFE_ZIP).is_file():
            manifest = build_member_manifest(build_container_descriptor_from_fixture(root / SAFE_ZIP))
            if manifest["risk_report"]["blocked_member_count"] != 0:
                errors.append("safe ZIP fixture unexpectedly contains blocked members.")

    result = {
        "schema_version": "f0_fixture_builder_result.v0",
        "status": "pass" if not errors else "fail",
        "built_files": built,
        "safe_zip": SAFE_ZIP.as_posix(),
        "expected_manifest": EXPECTED_MANIFEST.as_posix(),
        "unsafe_real_archives_built": False,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("F0 fixture builder", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in errors:
            print(f"ERROR: {error}", file=stdout)
    return 0 if not errors else 1


def _build_safe_zip(root: Path) -> list[str]:
    path = root / SAFE_ZIP
    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("README.txt", "F0 safe fixture: manifest-only enumeration sample.\n")
        archive.writestr("docs/notes.txt", "Nested directory member used for F0 path safety checks.\n")
    return [SAFE_ZIP.as_posix()]


if __name__ == "__main__":
    raise SystemExit(main())
