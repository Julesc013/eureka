from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_ROOTS = ("runtime", "surfaces", "site", "native")
ARCHIVE_MODULE_PREFIXES = ("archive.prototypes",)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ensure archived Python is not imported as active runtime or surface code."
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to scan.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_archive_import_guard(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_archive_import_guard(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    checked_files = 0

    for path in _iter_active_python_files(root):
        checked_files += 1
        rel = path.relative_to(root).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        except SyntaxError as exc:
            errors.append(f"{rel}:{exc.lineno or 1}: syntax error while checking archive imports: {exc.msg}.")
            continue
        for module, line in _iter_imports(tree):
            if any(module == prefix or module.startswith(f"{prefix}.") for prefix in ARCHIVE_MODULE_PREFIXES):
                errors.append(f"{rel}:{line}: active code must not import archived module {module!r}.")
        for value, line in _iter_string_constants(tree):
            if any(value == prefix or value.startswith(f"{prefix}.") for prefix in ARCHIVE_MODULE_PREFIXES):
                errors.append(f"{rel}:{line}: active code must not dynamically import archived module {value!r}.")

    return {
        "schema_version": "archive_import_guard.v0",
        "status": "valid" if not errors else "invalid",
        "checked_active_roots": list(ACTIVE_ROOTS),
        "checked_python_files": checked_files,
        "archive_root": "archive/prototypes/legacy_runtime",
        "allowed_importers": ["archive/**", "tools/**", "tests/**"],
        "errors": errors,
        "product_behavior_changed": False,
    }


def _iter_active_python_files(root: Path) -> Iterable[Path]:
    for active_root in ACTIVE_ROOTS:
        search_root = root / active_root
        if not search_root.exists():
            continue
        for path in sorted(search_root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            yield path


def _iter_imports(tree: ast.AST) -> Iterable[tuple[str, int]]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, node.lineno
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield node.module, node.lineno


def _iter_string_constants(tree: ast.AST) -> Iterable[tuple[str, int]]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.value, getattr(node, "lineno", 1)


def _format_plain(report: dict[str, Any]) -> str:
    lines = [
        f"Archive import guard: {report['status']}",
        f"checked_python_files: {report['checked_python_files']}",
    ]
    for error in report["errors"]:
        lines.append(f"- {error}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
