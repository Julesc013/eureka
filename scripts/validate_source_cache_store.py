#!/usr/bin/env python3
"""Validate the R0-05 durable source cache store."""

from __future__ import annotations

import argparse
import ast
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.demo_source_cache_store import run_demo
from runtime.source_cache import SourceCacheStore


CONTRACT_PATHS = (
    "contracts/stores/source_cache_store.v0.json",
    "contracts/stores/source_cache_entry.v0.json",
    "contracts/stores/source_cache_migration.v0.json",
    "contracts/stores/source_cache_status.v0.json",
)
STORE_RUNTIME_FILES = (
    "runtime/source_cache/__init__.py",
    "runtime/source_cache/errors.py",
    "runtime/source_cache/schema.py",
    "runtime/source_cache/store.py",
    "runtime/source_cache/migrations.py",
    "runtime/source_cache/records.py",
    "runtime/source_cache/queries.py",
    "runtime/source_cache/validation.py",
)
BANNED_IMPORT_ROOTS = {
    "requests",
    "httpx",
    "aiohttp",
    "urllib.request",
    "subprocess",
    "socket",
    "webbrowser",
    "selenium",
    "playwright",
    "openai",
    "anthropic",
    "runtime.connectors",
    "runtime.local_foundry",
}
FORBIDDEN_TERMS = tuple(
    [f"H{index}" for index in range(15)]
    + [
        "BUNDLE",
        "IA-BUNDLE",
        "F-BUNDLE",
        "G-BUNDLE",
        "MVP",
        "LOCAL-MVP",
        "AIDE",
        "prompt",
        "agent",
        "truth_boundary",
        "product_boundary",
        "review_seed",
        "quality_delta",
        "next_phase",
        "integration_audit",
        "accepted_truth",
        "public_index_mutated",
        "master_index_mutated",
    ]
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_store(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("R0-05 source cache store validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def validate_store(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    validate_contracts(root, errors)
    forbidden_vocabulary_found = scan_forbidden_vocabulary(root, errors)
    network_dependencies = scan_banned_imports(root, errors)
    h_series_dependencies = scan_phase_dependencies(root, errors)
    in_memory = run_demo(":memory:")
    validate_demo_output(in_memory, errors)
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "source-cache.sqlite"
        file_backed = run_demo(db)
        validate_demo_output(file_backed, errors)
        with SourceCacheStore.open(db) as store:
            store.init()
            store.init()
            integrity = store.check_integrity()
            if integrity.get("status") != "pass":
                errors.append("repeated init integrity check failed")
    if not (root / "control/inventory/r0_04_next_task_decision.json").is_file():
        warnings.append("R0-04 next task decision was not found")
    status = "pass"
    if warnings:
        status = "pass_with_warnings"
    if errors:
        status = "fail"
    return {
        "schema_version": "source_cache_store_validation.v0",
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "forbidden_vocabulary_found": forbidden_vocabulary_found,
        "h_series_dependencies": h_series_dependencies,
        "network_dependencies": network_dependencies,
        "in_memory_entry_count": in_memory["summary"]["cache_entry_count"],
        "file_backed_entry_count": file_backed["summary"]["cache_entry_count"],
        "evidence_ledger_writes_enabled": False,
        "review_queue_writes_enabled": False,
        "public_index_writes_enabled": False,
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
    }


def validate_contracts(root: Path, errors: list[str]) -> None:
    for rel in CONTRACT_PATHS:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing contract: {rel}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"contract is not valid JSON: {rel}: {exc}")
            continue
        if not isinstance(payload, Mapping):
            errors.append(f"contract root must be an object: {rel}")
        text = json.dumps(payload, sort_keys=True)
        for term in FORBIDDEN_TERMS:
            if term.lower() in text.lower():
                errors.append(f"forbidden vocabulary in contract {rel}: {term}")


def scan_forbidden_vocabulary(root: Path, errors: list[str]) -> int:
    count = 0
    for rel in STORE_RUNTIME_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing runtime file: {rel}")
            count += 1
            continue
        text = path.read_text(encoding="utf-8")
        for term in FORBIDDEN_TERMS:
            if term.lower() in text.lower():
                errors.append(f"forbidden vocabulary in {rel}: {term}")
                count += 1
    return count


def scan_banned_imports(root: Path, errors: list[str]) -> int:
    count = 0
    for path in sorted((root / "runtime/source_cache").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            imported: list[str] = []
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imported.append(node.module)
            for name in imported:
                if any(name == banned or name.startswith(banned + ".") for banned in BANNED_IMPORT_ROOTS):
                    errors.append(f"forbidden import in {path.relative_to(root).as_posix()}: {name}")
                    count += 1
    return count


def scan_phase_dependencies(root: Path, errors: list[str]) -> int:
    count = 0
    for path in sorted((root / "runtime/source_cache").glob("*.py")):
        text = path.read_text(encoding="utf-8").lower()
        if "runtime.connectors" in text or "runtime.local_foundry" in text:
            errors.append(f"forbidden runtime dependency in {path.relative_to(root).as_posix()}")
            count += 1
    return count


def validate_demo_output(output: Mapping[str, Any], errors: list[str]) -> None:
    if output.get("status") != "pass":
        errors.append("demo output did not pass")
    if output.get("summary", {}).get("cache_entry_count") != 1:
        errors.append("demo must persist exactly one cache entry")
    if output.get("integrity", {}).get("status") != "pass":
        errors.append("demo integrity check failed")
    for key in ("evidence_ledger_writes_enabled", "review_queue_writes_enabled", "public_index_writes_enabled"):
        if output.get(key) is not False:
            errors.append(f"demo must keep {key}=false")
    text = json.dumps(output, sort_keys=True)
    for term in ("truth_boundary", "product_boundary", "accepted_truth", "public_index_mutated", "master_index_mutated"):
        if term in text:
            errors.append(f"demo output contains reserved field {term}")


if __name__ == "__main__":
    raise SystemExit(main())
