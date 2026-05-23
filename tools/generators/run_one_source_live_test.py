#!/usr/bin/env python3
"""Run the one-source PyPI metadata pipeline through local stores."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.evidence.ledger import EvidenceCandidateRecord, EvidenceLedgerStore
from runtime.index.public import PublicIndexStore, rebuild_reviewed_public_index
from runtime.index.public.validation import validate_public_index_path
from runtime.review.queue import ReviewDecision, ReviewDecisionKind, ReviewItemRecord, ReviewQueueStore
from runtime.review.queue.validation import validate_review_queue_path
from runtime.source.cache import SourceCacheStatus, SourceCacheStore, build_cache_entry
from runtime.source.cache.validation import validate_cache_path
from runtime.evidence.ledger.validation import validate_evidence_ledger_path
from runtime.source.observation import SourcePolicy, build_evidence_candidate, build_source_observation, evaluate_source_policy
from runtime.source.observation.sources.pypi_json_metadata import (
    OPERATION_SCOPE,
    SOURCE_ID,
    build_default_source_record,
    build_pypi_metadata_request,
    fetch_pypi_metadata,
    normalize_pypi_metadata_response,
    parse_pypi_metadata_response,
    validate_pypi_package_name,
)


AUDIT_GENERATED_DIR = Path("control/audits/r0-09-one-source-live-test-v0/generated")
DEFAULT_USER_AGENT = "Eureka-one-source-live-test/0.1 (contact: local-test@example.invalid)"
DEFAULT_SEARCH_QUERY = "sampleproject"
DEFAULT_ABSENCE_QUERY = "definitely-not-sampleproject-r0-missing-query"

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
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--package-name", default="sampleproject")
    parser.add_argument("--source-cache-db", required=True)
    parser.add_argument("--evidence-db", required=True)
    parser.add_argument("--review-db", required=True)
    parser.add_argument("--public-index-db", required=True)
    parser.add_argument("--output")
    parser.add_argument("--decision", choices=[item.value for item in ReviewDecisionKind], default=ReviewDecisionKind.ACCEPT.value)
    parser.add_argument("--search-query", default=DEFAULT_SEARCH_QUERY)
    parser.add_argument("--absence-query", default=DEFAULT_ABSENCE_QUERY)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("--timeout-seconds", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    output = resolve_output_path(root, args.output) if args.output else None
    errors = validate_paths(
        root,
        output,
        args.source_cache_db,
        args.evidence_db,
        args.review_db,
        args.public_index_db,
    )
    if errors:
        print(json.dumps({"schema_version": "one_source_live_test_output.v0", "status": "fail", "errors": errors}, indent=2), file=stderr)
        return 2

    result = run_one_source_live_test(
        package_name=args.package_name,
        source_cache_db=args.source_cache_db,
        evidence_db=args.evidence_db,
        review_db=args.review_db,
        public_index_db=args.public_index_db,
        live=args.live,
        decision_kind=ReviewDecisionKind(args.decision),
        search_query=args.search_query,
        absence_query=args.absence_query,
        user_agent=args.user_agent,
        timeout_seconds=args.timeout_seconds,
    )
    text = json.dumps(result, indent=2, sort_keys=True)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
        write_generated_artifacts(output.parent, result)
    if args.json:
        print(text, file=stdout)
    else:
        print("one-source metadata pipeline", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"network_used: {str(result['network_used']).lower()}", file=stdout)
        print(f"request_count: {result['request_count']}", file=stdout)
        print(f"search_hit_count: {result['search_hit_count']}", file=stdout)
    return 0


def run_one_source_live_test(
    *,
    package_name: str,
    source_cache_db: str | Path,
    evidence_db: str | Path,
    review_db: str | Path,
    public_index_db: str | Path,
    live: bool = False,
    decision_kind: ReviewDecisionKind = ReviewDecisionKind.ACCEPT,
    search_query: str = DEFAULT_SEARCH_QUERY,
    absence_query: str = DEFAULT_ABSENCE_QUERY,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout_seconds: int = 10,
) -> dict[str, Any]:
    package_errors = validate_pypi_package_name(package_name)
    if package_errors:
        return _blocked_result(package_name, "; ".join(package_errors), live_requested=live)

    source_record = build_default_source_record()
    source_policy = SourcePolicy(
        allowed_operations=("metadata_observation", OPERATION_SCOPE),
        limitations=("one-source metadata policy",),
    )
    policy_decision = evaluate_source_policy(source_record, OPERATION_SCOPE, {"policy": source_policy})
    if policy_decision.status.value != "allowed":
        return _blocked_result(package_name, policy_decision.reason, live_requested=live)

    request = build_pypi_metadata_request(package_name, source_record=source_record)
    request_count = 1 if live else 0
    try:
        response = fetch_pypi_metadata(request, client_contact=user_agent, timeout_seconds=timeout_seconds, live=live)
    except Exception as exc:
        return _blocked_result(
            package_name,
            f"metadata request unavailable: {exc}",
            live_requested=live,
            network_used=live,
            request_count=request_count,
        )

    parsed_fields = parse_pypi_metadata_response(response)
    source_observation = build_source_observation(response, source_record, policy=source_policy, observed_fields=parsed_fields)
    normalized_observation = normalize_pypi_metadata_response(response, source_record)
    with SourceCacheStore.open(source_cache_db) as cache_store:
        cache_store.init()
        cache_store.write_source_record(source_record)
        cache_store.write_metadata_response(response)
        cache_store.write_source_observation(source_observation)
        cache_store.write_normalized_observation(normalized_observation)
        cache_entry = build_cache_entry(
            source_record,
            response,
            source_observation,
            normalized_observation,
            SourceCacheStatus.CACHED,
        )
        cache_store.write_cache_entry(cache_entry)
        source_cache_summary = cache_store.summarize().to_dict()

    evidence_candidate = build_evidence_candidate(normalized_observation)
    evidence_record = EvidenceCandidateRecord.from_candidate(
        evidence_candidate,
        normalized_observation_id=normalized_observation.normalized_observation_id,
        source_cache_entry_id=cache_entry.entry_id,
    )
    with EvidenceLedgerStore.open(evidence_db) as ledger:
        ledger.init()
        ledger.write_evidence_candidate(evidence_record)
        ledger.link_source_cache_entry(evidence_record.evidence_id, cache_entry.entry_id)
        evidence_summary = ledger.summarize().to_dict()

    review_item = ReviewItemRecord.from_evidence(evidence_record, source_cache_entry_id=cache_entry.entry_id)
    decision_reason = None
    if decision_kind in {ReviewDecisionKind.REJECT, ReviewDecisionKind.BLOCK}:
        decision_reason = "local one-source review decision"
    review_decision = ReviewDecision(
        review_item_id=review_item.review_item_id,
        decision_kind=decision_kind,
        decision_actor="operator:local",
        reason=decision_reason,
        payload={"scope": "one_source_metadata_pipeline"},
        limitations=("local review state only",),
    )
    with ReviewQueueStore.open(review_db) as queue:
        queue.init()
        queue.enqueue_review_item(review_item)
        queue.link_evidence(review_item.review_item_id, evidence_record.evidence_id)
        queue.link_source_cache_entry(review_item.review_item_id, cache_entry.entry_id)
        queue.record_decision(review_item.review_item_id, review_decision)
        stored_review_item = queue.get_review_item(review_item.review_item_id) or review_item
        decisions = queue.list_decisions(review_item.review_item_id)
        stored_review_decision = decisions[-1] if decisions else review_decision
        review_summary = queue.summarize().to_dict()

    rebuild = rebuild_reviewed_public_index(source_cache_db, evidence_db, review_db, public_index_db, dry_run=False)
    with PublicIndexStore.open(public_index_db) as public_store:
        public_store.init()
        public_index_records = public_store.list_records()
        search_results = public_store.search(search_query, limit=10)
        absence_report = public_store.absence_report(absence_query)
        public_index_summary = public_store.summarize().to_dict()

    accepted = decision_kind == ReviewDecisionKind.ACCEPT
    public_record = public_index_records[-1].to_dict() if public_index_records else {}
    search_hit_count = len(search_results)
    absence_hit_count = absence_report.result_count
    status = "pass" if (not accepted or search_hit_count >= 1) and absence_hit_count == 0 else "fail"
    result = {
        "schema_version": "one_source_live_test_output.v0",
        "status": status,
        "source_id": SOURCE_ID,
        "package_name": package_name,
        "live_requested": live,
        "network_used": live,
        "request_count": request_count,
        "download_count": 0,
        "install_execution_count": 0,
        "source_sync_used": False,
        "policy_decision": policy_decision.to_dict(),
        "metadata_request": request.to_dict(),
        "metadata_response": response.to_dict(),
        "source_observation": source_observation.to_dict(),
        "normalized_observation": normalized_observation.to_dict(),
        "source_cache_entry": cache_entry.to_dict(),
        "evidence_candidate_record": evidence_record.to_dict(),
        "review_item_record": stored_review_item.to_dict(),
        "review_decision": stored_review_decision.to_dict(),
        "public_index_record": public_record,
        "search_results": [item.to_dict() for item in search_results],
        "absence_report": absence_report.to_dict(),
        "rebuild_report": rebuild,
        "source_cache_summary": source_cache_summary,
        "evidence_summary": evidence_summary,
        "review_summary": review_summary,
        "public_index_summary": public_index_summary,
        "source_cache_entry_created": True,
        "evidence_candidate_created": True,
        "review_item_created": True,
        "review_decision_recorded": True,
        "public_index_rebuilt": True,
        "search_hit_count": search_hit_count,
        "absence_hit_count": absence_hit_count,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "model_provider_used": False,
        "runtime_connectors_modified": False,
        "limitations": [
            "reviewed local record is not global source truth",
            "no package files were downloaded",
            "no install or execution was performed",
        ],
        "warnings": [] if live else ["dry-run response used; no live network request was made"],
    }
    result["db_manifest"] = build_db_manifest(source_cache_db, evidence_db, review_db, public_index_db)
    return result


def validate_paths(root: Path, output: Path | None, *db_paths: str | Path) -> list[str]:
    errors: list[str] = []
    if output and is_forbidden_output(root, output):
        errors.append(f"refusing forbidden output root: {output}")
    validators = (validate_cache_path, validate_evidence_ledger_path, validate_review_queue_path, validate_public_index_path)
    for db_path, validator in zip(db_paths, validators):
        path_errors = validator(db_path)
        errors.extend(path_errors)
        if "site" in Path(db_path).parts and "dist" in Path(db_path).parts:
            errors.append("database paths must not target generated site outputs")
    return errors


def write_generated_artifacts(output_dir: Path, result: Mapping[str, Any]) -> None:
    artifacts = {
        "live_metadata_response.json": result.get("metadata_response", {}),
        "source_observation.json": result.get("source_observation", {}),
        "normalized_observation.json": result.get("normalized_observation", {}),
        "source_cache_entry.json": result.get("source_cache_entry", {}),
        "evidence_candidate_record.json": result.get("evidence_candidate_record", {}),
        "review_item_record.json": result.get("review_item_record", {}),
        "review_decision.json": result.get("review_decision", {}),
        "public_index_record.json": result.get("public_index_record", {}),
        "search_result.json": (result.get("search_results") or [{}])[0],
        "absence_report.json": result.get("absence_report", {}),
        "live_test_demo.sqlite.manifest.json": result.get("db_manifest", {}),
    }
    for name, payload in artifacts.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "sample_summary.md").write_text(render_summary(result), encoding="utf-8")


def build_db_manifest(*paths: str | Path) -> dict[str, Any]:
    entries = []
    for path in paths:
        item = Path(path)
        entries.append(
            {
                "path": str(path),
                "exists": item.exists(),
                "size_bytes": item.stat().st_size if item.exists() else 0,
                "sha256": hashlib.sha256(item.read_bytes()).hexdigest() if item.exists() else "",
            }
        )
    return {
        "schema_version": "one_source_live_test_sqlite_manifest.v0",
        "databases": entries,
        "site_dist_mutated": False,
        "master_index_mutated": False,
    }


def render_summary(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# One Source Live Test Summary",
            "",
            f"- status: {result.get('status')}",
            f"- source_id: {result.get('source_id')}",
            f"- package_name: {result.get('package_name')}",
            f"- live_requested: {str(result.get('live_requested')).lower()}",
            f"- network_used: {str(result.get('network_used')).lower()}",
            f"- request_count: {result.get('request_count')}",
            f"- search_hit_count: {result.get('search_hit_count')}",
            f"- absence_hit_count: {result.get('absence_hit_count')}",
            "- downloads: 0",
            "- install/execution: 0",
            "- source sync: false",
            "",
        ]
    )


def resolve_output_path(root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def is_forbidden_output(root: Path, output: Path) -> bool:
    try:
        rel = output.relative_to(root).as_posix()
    except ValueError:
        return False
    if rel.startswith("site/dist/") or rel == "site/dist":
        return True
    return any(rel == item or rel.startswith(item.rstrip("/") + "/") for item in FORBIDDEN_OUTPUT_ROOTS)


def _blocked_result(
    package_name: str,
    reason: str,
    *,
    live_requested: bool,
    network_used: bool = False,
    request_count: int = 0,
) -> dict[str, Any]:
    return {
        "schema_version": "one_source_live_test_output.v0",
        "status": "blocked",
        "source_id": SOURCE_ID,
        "package_name": package_name,
        "live_requested": live_requested,
        "network_used": network_used,
        "request_count": request_count,
        "download_count": 0,
        "install_execution_count": 0,
        "source_sync_used": False,
        "reason": reason,
        "source_cache_entry_created": False,
        "evidence_candidate_created": False,
        "review_item_created": False,
        "review_decision_recorded": False,
        "public_index_rebuilt": False,
        "search_hit_count": 0,
        "absence_hit_count": 0,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "model_provider_used": False,
        "runtime_connectors_modified": False,
        "limitations": [reason],
        "warnings": [],
    }


if __name__ == "__main__":
    raise SystemExit(main())
