#!/usr/bin/env python3
"""Validate the R0-07 durable review queue store."""

from __future__ import annotations

import argparse
import ast
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.review.queue import ReviewQueueStore
from scripts.demo_review_queue_store import run_demo


CONTRACT_PATHS = (
    "contracts/stores/review_queue_store.v0.json",
    "contracts/stores/review_item_record.v0.json",
    "contracts/stores/review_decision.v0.json",
    "contracts/stores/review_event.v0.json",
    "contracts/stores/review_queue_status.v0.json",
    "contracts/stores/review_queue_migration.v0.json",
)
STORE_RUNTIME_FILES = (
    "runtime/review/queue/__init__.py",
    "runtime/review/queue/errors.py",
    "runtime/review/queue/schema.py",
    "runtime/review/queue/store.py",
    "runtime/review/queue/migrations.py",
    "runtime/review/queue/records.py",
    "runtime/review/queue/decisions.py",
    "runtime/review/queue/queries.py",
    "runtime/review/queue/validation.py",
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
        "public_truth",
        "accepted_truth",
        "source_truth",
        "evidence_truth",
        "public_index_mutated",
        "master_index_mutated",
        "production_ready",
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
        print("R0-07 review queue store validation", file=stdout)
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
    in_memory = run_demo(":memory:", ":memory:", ":memory:")
    validate_demo_output(in_memory, errors)
    with tempfile.TemporaryDirectory() as tmp:
        source_cache_db = Path(tmp) / "source-cache.sqlite"
        evidence_db = Path(tmp) / "evidence-ledger.sqlite"
        review_db = Path(tmp) / "review-queue.sqlite"
        file_backed = run_demo(source_cache_db, evidence_db, review_db)
        validate_demo_output(file_backed, errors)
        with ReviewQueueStore.open(review_db) as store:
            store.init()
            store.init()
            integrity = store.check_integrity()
            if integrity.get("status") != "pass":
                errors.append("repeated init integrity check failed")
    if not (root / "control/inventory/r0_06_next_task_decision.json").is_file():
        warnings.append("R0-06 next task decision was not found")
    status = "pass"
    if warnings:
        status = "pass_with_warnings"
    if errors:
        status = "fail"
    return {
        "schema_version": "review_queue_store_validation.v0",
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "forbidden_vocabulary_found": forbidden_vocabulary_found,
        "h_series_dependencies": h_series_dependencies,
        "network_dependencies": network_dependencies,
        "in_memory_review_item_count": in_memory["summary"]["review_item_count"],
        "file_backed_review_item_count": file_backed["summary"]["review_item_count"],
        "evidence_ledger_linking_enabled": True,
        "source_cache_linking_enabled": True,
        "explicit_review_decisions_enabled": True,
        "public_index_writes_enabled": False,
        "master_index_writes_enabled": False,
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
    for path in sorted((root / "runtime/review/queue").glob("*.py")):
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
    for path in sorted((root / "runtime/review/queue").glob("*.py")):
        text = path.read_text(encoding="utf-8").lower()
        if "runtime.connectors" in text or "runtime.local_foundry" in text:
            errors.append(f"forbidden runtime dependency in {path.relative_to(root).as_posix()}")
            count += 1
    return count


def validate_demo_output(output: Mapping[str, Any], errors: list[str]) -> None:
    if output.get("status") != "pass":
        errors.append("demo output did not pass")
    if output.get("summary", {}).get("review_item_count") != 1:
        errors.append("demo must persist exactly one review item")
    if output.get("summary", {}).get("evidence_link_count") != 1:
        errors.append("demo must persist exactly one evidence link")
    if output.get("summary", {}).get("source_cache_link_count") != 1:
        errors.append("demo must persist exactly one source cache link")
    if output.get("summary", {}).get("decision_count") != 1:
        errors.append("demo must persist exactly one decision")
    if output.get("summary", {}).get("review_event_count", 0) < 5:
        errors.append("demo must append review events")
    if output.get("integrity", {}).get("status") != "pass":
        errors.append("demo integrity check failed")
    for key in ("public_index_writes_enabled", "master_index_writes_enabled", "automatic_acceptance_enabled"):
        if output.get(key) is not False:
            errors.append(f"demo must keep {key}=false")
    text = json.dumps(output, sort_keys=True)
    for term in ("truth_boundary", "product_boundary", "public_truth", "accepted_truth", "public_index_mutated", "master_index_mutated"):
        if term in text:
            errors.append(f"demo output contains reserved field {term}")


if __name__ == "__main__":
    raise SystemExit(main())
