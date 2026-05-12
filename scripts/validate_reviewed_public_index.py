#!/usr/bin/env python3
"""Validate the local reviewed public index seam."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_index import PublicIndexRecord, PublicIndexStore
from runtime.public_index.rebuild import rebuild_reviewed_public_index
from runtime.public_index.validation import validate_no_public_truth_fields, validate_no_task_vocabulary
from scripts.demo_review_queue_store import run_demo as run_review_queue_demo
from scripts.demo_reviewed_public_index import run_demo as run_public_index_demo
from runtime.review_queue import ReviewDecisionKind


CONTRACT_PATHS = (
    "contracts/stores/public_index_store.v0.json",
    "contracts/stores/public_index_record.v0.json",
    "contracts/stores/public_index_rebuild.v0.json",
    "contracts/stores/public_index_search_result.v0.json",
    "contracts/stores/public_index_absence_report.v0.json",
    "contracts/stores/public_index_migration.v0.json",
)

FORBIDDEN_IMPORTS = {
    "requests",
    "httpx",
    "aiohttp",
    "urllib.request",
    "subprocess",
    "socket",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    checks.append(_check_contracts())
    checks.append(_check_runtime_vocabulary())
    checks.append(_check_runtime_imports())
    checks.append(_check_in_memory_store())
    checks.append(_check_file_backed_rebuild())
    checks.append(_check_exclusions())
    checks.append(_check_blockers())
    status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    return {
        "schema_version": "reviewed_public_index_validation.v0",
        "status": status,
        "checks": checks,
        "network_dependencies": 0,
        "h_series_dependencies": 0,
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
    }


def _check_contracts() -> dict[str, Any]:
    errors: list[str] = []
    for rel in CONTRACT_PATHS:
        path = REPO_ROOT / rel
        if not path.exists():
            errors.append(f"missing contract: {rel}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid json {rel}: {exc}")
            continue
        text = json.dumps(data, sort_keys=True)
        errors.extend(f"{rel}: {error}" for error in validate_no_task_vocabulary(text))
        errors.extend(f"{rel}: {error}" for error in validate_no_public_truth_fields(text))
    return {"name": "contracts", "status": "pass" if not errors else "fail", "errors": errors}


def _check_runtime_vocabulary() -> dict[str, Any]:
    errors: list[str] = []
    for path in (REPO_ROOT / "runtime" / "public_index").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        errors.extend(f"{path.name}: {error}" for error in validate_no_task_vocabulary(text))
        if "truth_boundary" in text or "product_boundary" in text:
            errors.append(f"{path.name}: reserved boundary phrase found")
    return {"name": "runtime_vocabulary", "status": "pass" if not errors else "fail", "errors": errors}


def _check_runtime_imports() -> dict[str, Any]:
    errors: list[str] = []
    for path in (REPO_ROOT / "runtime" / "public_index").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                if name in FORBIDDEN_IMPORTS or name.startswith("runtime.connectors") or name.startswith("runtime.local_foundry"):
                    errors.append(f"{path.name}: forbidden import {name}")
    return {"name": "runtime_imports", "status": "pass" if not errors else "fail", "errors": errors}


def _check_in_memory_store() -> dict[str, Any]:
    with PublicIndexStore.open(":memory:") as store:
        store.init()
        record = PublicIndexRecord(
            record_id="pir_test",
            source_id="demo.source",
            source_cache_entry_id="sce_test",
            evidence_id="ev_test",
            review_item_id="rvi_test",
            review_decision_id="rvd_test",
            title="Demo Project",
            description="A locally reviewed demo record",
            normalized_fields={"name": "Demo Project"},
            searchable_text="demo project locally reviewed",
            source_family="synthetic",
            trust_lane="local",
        )
        store.write_record(record)
        fetched = store.get_record(record.record_id)
        search_results = store.search("demo")
        absence = store.absence_report("missing query")
        integrity = store.check_integrity()
    ok = fetched is not None and len(search_results) == 1 and absence.result_count == 0 and integrity["status"] == "pass"
    return {"name": "in_memory_store", "status": "pass" if ok else "fail", "errors": [] if ok else ["in-memory store failed"]}


def _check_file_backed_rebuild() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        source_db = root / "source_cache.sqlite"
        evidence_db = root / "evidence.sqlite"
        review_db = root / "review.sqlite"
        public_db = root / "public.sqlite"
        run_public_index_demo(source_db, evidence_db, review_db, public_db)
        before = [_digest(source_db), _digest(evidence_db), _digest(review_db)]
        report = rebuild_reviewed_public_index(source_db, evidence_db, review_db, public_db, dry_run=True)
        after = [_digest(source_db), _digest(evidence_db), _digest(review_db)]
        with PublicIndexStore.open(public_db) as store:
            store.init()
            records = store.list_records()
            results = store.search("demo project")
            absence = store.absence_report("not-present-query")
        ok = (
            report["included_count"] >= 1
            and before == after
            and len(records) >= 1
            and len(results) >= 1
            and absence.result_count == 0
        )
    return {
        "name": "file_backed_rebuild",
        "status": "pass" if ok else "fail",
        "errors": [] if ok else ["file-backed rebuild did not preserve expected behavior"],
    }


def _check_exclusions() -> dict[str, Any]:
    errors: list[str] = []
    for kind in (
        ReviewDecisionKind.REJECT,
        ReviewDecisionKind.BLOCK,
        ReviewDecisionKind.SUPERSEDE,
        ReviewDecisionKind.REQUEST_MORE_EVIDENCE,
        ReviewDecisionKind.NOTE_ONLY,
    ):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_db = root / "source_cache.sqlite"
            evidence_db = root / "evidence.sqlite"
            review_db = root / "review.sqlite"
            public_db = root / "public.sqlite"
            run_review_queue_demo(source_db, evidence_db, review_db, decision_kind=kind)
            report = rebuild_reviewed_public_index(source_db, evidence_db, review_db, public_db, dry_run=True)
            if report["included_count"] != 0:
                errors.append(f"{kind.value} decision was included")
    return {"name": "decision_exclusions", "status": "pass" if not errors else "fail", "errors": errors}


def _check_blockers() -> dict[str, Any]:
    return {
        "name": "blockers",
        "status": "pass",
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
    }


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
