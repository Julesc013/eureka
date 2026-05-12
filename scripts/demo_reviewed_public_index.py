#!/usr/bin/env python3
"""Demonstrate the local reviewed public index rebuild with synthetic stores."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_index import PublicIndexStore, rebuild_reviewed_public_index
from runtime.public_index.validation import validate_public_index_path
from scripts.demo_review_queue_store import run_demo as run_review_queue_demo


FORBIDDEN_OUTPUT_ROOTS = {
    "runtime",
    "contracts",
    "surfaces",
    "site",
    "native",
    "crates",
    "examples",
    ".git",
    ".env",
    "secrets",
    ".aide.local",
    ".local",
    ".cache",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--source-cache-db", required=True)
    parser.add_argument("--evidence-db", required=True)
    parser.add_argument("--review-db", required=True)
    parser.add_argument("--public-index-db", required=True)
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    errors = validate_public_index_path(args.public_index_db)
    if errors:
        print(json.dumps({"status": "fail", "errors": list(errors)}, indent=2, sort_keys=True), file=stderr)
        return 2
    output = resolve_output_path(root, args.output) if args.output else None
    if output and is_forbidden_output(root, output):
        print(f"refusing forbidden output root: {output}", file=stderr)
        return 2

    result = run_demo(args.source_cache_db, args.evidence_db, args.review_db, args.public_index_db)
    text = json.dumps(result, indent=2, sort_keys=True)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(text, file=stdout)
    else:
        print("reviewed public index demo", file=stdout)
        print(f"record_count: {result['public_index_summary']['record_count']}", file=stdout)
        print(f"search_count: {len(result['search_results'])}", file=stdout)
    return 0


def run_demo(
    source_cache_db: str | Path,
    evidence_db: str | Path,
    review_db: str | Path,
    public_index_db: str | Path,
) -> dict[str, Any]:
    review_demo = run_review_queue_demo(source_cache_db, evidence_db, review_db)
    rebuild = rebuild_reviewed_public_index(source_cache_db, evidence_db, review_db, public_index_db, dry_run=False)
    with PublicIndexStore.open(public_index_db) as store:
        store.init()
        records = store.list_records()
        search_results = store.search("demo project", limit=10)
        absence_report = store.absence_report("not-present-query")
        summary = store.summarize()
        integrity = store.check_integrity()
    review_decisions = review_demo.get("review_decisions", [])
    review_items = review_demo.get("review_items", [])
    return {
        "schema_version": "reviewed_public_index_demo_output.v0",
        "status": "pass",
        "source_cache_entry": {
            "entry_id": review_demo.get("source_cache_entry", {}).get("entry_id"),
            "source_id": review_demo.get("source_cache_entry", {}).get("source_id"),
            "status": review_demo.get("source_cache_entry", {}).get("status"),
        },
        "evidence_candidate_record": {
            "evidence_id": review_demo.get("evidence_candidate_record", {}).get("evidence_id"),
            "source_cache_entry_id": review_demo.get("evidence_candidate_record", {}).get("source_cache_entry_id"),
            "status": review_demo.get("evidence_candidate_record", {}).get("status"),
        },
        "review_item": {
            "review_item_id": review_items[0].get("review_item_id") if review_items else None,
            "queue_status": review_items[0].get("queue_status") if review_items else None,
            "evidence_id": review_items[0].get("evidence_id") if review_items else None,
            "source_cache_entry_id": review_items[0].get("source_cache_entry_id") if review_items else None,
        },
        "review_decision": {
            "decision_id": review_decisions[-1].get("decision_id") if review_decisions else None,
            "decision_kind": review_decisions[-1].get("decision_kind") if review_decisions else None,
            "decision_status": review_decisions[-1].get("decision_status") if review_decisions else None,
        },
        "rebuild_report": rebuild,
        "public_index_records": [record.to_dict() for record in records],
        "search_results": [result.to_dict() for result in search_results],
        "absence_report": absence_report.to_dict(),
        "public_index_summary": summary.to_dict(),
        "integrity": integrity,
        "input_stores_mutated": False,
        "site_dist_mutated": False,
        "master_index_mutated": False,
    }


def resolve_output_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def is_forbidden_output(root: Path, output: Path) -> bool:
    try:
        rel = output.relative_to(root).as_posix()
    except ValueError:
        return False
    return any(rel == item or rel.startswith(item.rstrip("/") + "/") for item in FORBIDDEN_OUTPUT_ROOTS)


if __name__ == "__main__":
    raise SystemExit(main())
