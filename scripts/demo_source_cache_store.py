#!/usr/bin/env python3
"""Demonstrate the durable source cache store with synthetic data."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.source_cache import SourceCacheStatus, SourceCacheStore, build_cache_entry
from runtime.source_cache.validation import validate_cache_path
from runtime.source_observation import (
    MetadataRequest,
    MetadataResponse,
    SourceCapability,
    SourceId,
    SourceLocator,
    SourcePolicy,
    SourceRecord,
    build_source_observation,
    normalize_metadata_response,
)


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
    parser.add_argument("--db")
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    db_value = args.db or ":memory:"
    db_errors = list(validate_cache_path(db_value))
    if db_errors:
        print(json.dumps({"status": "fail", "errors": db_errors}, indent=2, sort_keys=True), file=stderr)
        return 2
    if args.output:
        output = resolve_output_path(root, args.output)
        if is_forbidden_output(root, output):
            print(f"refusing forbidden output root: {output}", file=stderr)
            return 2
    else:
        output = None

    result = run_demo(db_value)
    text = json.dumps(result, indent=2, sort_keys=True)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(text, file=stdout)
    else:
        print("source cache store demo", file=stdout)
        print(f"entry_id: {result['source_cache_entry']['entry_id']}", file=stdout)
        print(f"entry_count: {result['summary']['cache_entry_count']}", file=stdout)
    return 0


def run_demo(db_path: str | Path = ":memory:") -> dict[str, Any]:
    source_record, response, source_observation, normalized_observation = build_demo_objects()
    with SourceCacheStore.open(db_path) as store:
        store.init()
        store.write_source_record(source_record)
        store.write_metadata_response(response)
        store.write_source_observation(source_observation)
        store.write_normalized_observation(normalized_observation)
        entry = build_cache_entry(
            source_record,
            response,
            source_observation,
            normalized_observation,
            status=SourceCacheStatus.CACHED,
        )
        store.write_cache_entry(entry)
        fetched = store.get_cache_entry(entry.entry_id)
        entries = store.list_cache_entries(source_id=str(source_record.source_id))
        summary = store.summarize()
        integrity = store.check_integrity()
    return {
        "schema_version": "source_cache_demo_output.v0",
        "status": "pass",
        "source_cache_entry": fetched.to_dict() if fetched else {},
        "source_cache_list": [item.to_dict() for item in entries],
        "summary": summary.to_dict(),
        "integrity": integrity,
        "evidence_ledger_writes_enabled": False,
        "review_queue_writes_enabled": False,
        "public_index_writes_enabled": False,
        "master_index_writes_enabled": False,
    }


def build_demo_objects():
    source_record = SourceRecord(
        source_id=SourceId("source.example.metadata"),
        source_family="package_registry",
        trust_lane="synthetic",
        label="Synthetic package metadata source",
        locators=(SourceLocator(kind="synthetic", value="package/demo-project", label="demo-project"),),
        capabilities=(
            SourceCapability(
                name="metadata_observation",
                operations=("metadata_observation",),
                limitations=("synthetic payload only",),
            ),
        ),
        limitations=("no durable evidence write", "no live request"),
        metadata={"owner": "repo"},
    )
    policy = SourcePolicy(
        allowed_operations=("metadata_observation",),
        limitations=("metadata remains a cached candidate",),
    )
    request = MetadataRequest.build(
        source_id=source_record.source_id,
        request_kind="package_metadata",
        target="demo-project",
        parameters={"name": "demo-project"},
        created_at="2026-05-12T00:00:00Z",
    )
    response = MetadataResponse.build(
        request_id=request.request_id,
        source_id=source_record.source_id,
        status="observed",
        payload={
            "name": "demo-project",
            "version": "1.0.0",
            "summary": "Synthetic metadata for source cache validation",
        },
        observed_at="2026-05-12T00:00:01Z",
        limitations=("synthetic payload only",),
    )
    normalized_observation = normalize_metadata_response(response, source_record, policy=policy)
    source_observation = build_source_observation(
        response,
        source_record,
        policy=policy,
        observed_fields=normalized_observation.normalized_fields,
    )
    return source_record, response, source_observation, normalized_observation


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
