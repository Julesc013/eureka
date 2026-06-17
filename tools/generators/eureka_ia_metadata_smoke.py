#!/usr/bin/env python3
"""Run a bounded IA metadata provider smoke over the governed local pipeline."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.search.hunt.ia_bridge import (  # noqa: E402
    build_ia_hunt_boundary_report,
    plan_ia_hunt_pipeline,
    run_ia_hunt_pipeline_dry_run,
)
from runtime.source.observation.internet_archive_fixture_replay import (  # noqa: E402
    replay_fixture_directory_report,
)
from runtime.source.observation.internet_archive_live_probe import (  # noqa: E402
    load_live_probe_policy,
    run_live_metadata_probe,
)


TASK_ID = "IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00"
DEFAULT_OUT_DIR = Path(".eureka/source-wave/ia-metadata/latest")
DEFAULT_AUDIT_DIR = Path("control/audits/source_wave/ia_metadata_provider_wiring_and_smoke_v0")
REPORT_NAME = "ia_metadata_provider_smoke_report.json"
SUMMARY_NAME = "SMOKE_RESULTS.md"
DEFAULT_USER_AGENT = "EurekaLocalIAMetadataSmoke/0.1 (metadata-only; contact: local-operator)"
DEFAULT_CONTACT = "local-operator"
SMOKE_QUERIES = (
    "manual for Sound Blaster CT1740",
    "old blue FTP client for XP",
    "latest Firefox before XP support ended",
    "driver for ThinkPad T42 Wi-Fi Windows 2000",
    "article about ray tracing in a 1994 magazine",
    "StyleWriter 2500 Mac OS 8 driver",
    "DirectX SDK June 2010 offline installer",
)
UNSAFE_FLAGS = (
    "public_fanout",
    "downloads",
    "file_fetching",
    "wayback_replay",
    "public_mutation",
    "public_workbench",
    "live_public_metadata",
    "reviewed_index_mutated",
    "master_index_mutated",
    "rights_safety_claims",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("fixture", "live", "fixture-and-live"), default="fixture")
    parser.add_argument("--allow-live-metadata", action="store_true", help="Permit the optional bounded local IA live metadata probe.")
    parser.add_argument("--budget", choices=("small",), default="small")
    parser.add_argument("--out", default=str(DEFAULT_OUT_DIR), help="Ignored/local output directory for generated smoke artifacts.")
    parser.add_argument("--audit-dir", default="", help="Optional tracked audit directory for closeout reports.")
    parser.add_argument("--query", action="append", dest="queries", help="Override the default smoke query set.")
    parser.add_argument("--live-query-limit", type=int, default=1, help="Maximum live metadata queries for small-budget live mode.")
    parser.add_argument("--rows", type=int, default=1, help="Live metadata search rows, capped by policy.")
    parser.add_argument("--max-requests", type=int, default=2, help="Live metadata request cap, capped by policy.")
    parser.add_argument("--timeout-seconds", type=int, default=10, help="Recorded live timeout bound; transport enforces policy.")
    parser.add_argument("--contact", default=DEFAULT_CONTACT)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("--json", action="store_true", help="Print the full JSON report.")
    args = parser.parse_args(argv)

    queries = tuple(args.queries or SMOKE_QUERIES)
    if args.live_query_limit < 0:
        print("error: --live-query-limit must be non-negative", file=stderr)
        return 2
    if args.rows < 0:
        print("error: --rows must be non-negative", file=stderr)
        return 2
    if args.max_requests < 1:
        print("error: --max-requests must be positive", file=stderr)
        return 2

    try:
        report = build_smoke_report(
            mode=args.mode,
            queries=queries,
            allow_live_metadata=bool(args.allow_live_metadata),
            live_query_limit=args.live_query_limit,
            rows=args.rows,
            max_requests=args.max_requests,
            timeout_seconds=args.timeout_seconds,
            contact=args.contact,
            user_agent=args.user_agent,
        )
        out_dir = Path(args.out)
        written = _write_report_pair(out_dir, report)
        if args.audit_dir:
            written.update(_write_report_pair(Path(args.audit_dir), report))
        report["output_files"] = {key: _repo_relative(value) for key, value in sorted(written.items())}
        _rewrite_report_files(written, report)
    except Exception as exc:
        print(f"error: {_redact_error(exc)}", file=stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"{TASK_ID} smoke", file=stdout)
        print(f"status: {report['status']}", file=stdout)
        print(f"fixture status: {report['fixture_smoke']['status']}", file=stdout)
        print(f"live status: {report['live_smoke']['status']}", file=stdout)
        print(f"source observations: {report['totals']['source_observations_created']}", file=stdout)
        print(f"candidates: {report['totals']['candidates_created']}", file=stdout)
        print(f"review previews: {report['totals']['review_previews_created']}", file=stdout)
    return 1 if report["status"] == "FAIL" else 0


def build_smoke_report(
    *,
    mode: str,
    queries: Sequence[str],
    allow_live_metadata: bool,
    live_query_limit: int,
    rows: int,
    max_requests: int,
    timeout_seconds: int,
    contact: str,
    user_agent: str,
) -> dict[str, Any]:
    fixture = _run_fixture_smoke(queries) if mode in {"fixture", "fixture-and-live"} else _fixture_not_requested()
    live = _run_live_smoke(
        queries,
        requested=mode in {"live", "fixture-and-live"},
        allow_live_metadata=allow_live_metadata,
        live_query_limit=live_query_limit,
        rows=rows,
        max_requests=max_requests,
        timeout_seconds=timeout_seconds,
        contact=contact,
        user_agent=user_agent,
    )
    safety = _safety_summary(fixture, live)
    status = _overall_status(fixture, live, safety)
    totals = _totals(fixture, live)
    return {
        "schema_version": "ia_metadata_provider_wiring_and_smoke_report.v0",
        "task_id": TASK_ID,
        "status": status,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mode": mode,
        "budget": "small",
        "query_count": len([item for item in queries if str(item).strip()]),
        "queries": [str(item) for item in queries],
        "request_plan": {
            "local_operator_invocation_required": True,
            "fixture_mode_uses_committed_fixtures": True,
            "live_mode_requires_allow_live_metadata": True,
            "live_query_limit": live_query_limit,
            "live_rows_requested": rows,
            "live_max_requests_requested": max_requests,
            "timeout_seconds": timeout_seconds,
            "no_payload_file_fetch": True,
            "no_download": True,
            "no_wayback_replay": True,
            "cache_write_scope": "dry_run_no_instance_mutation",
            "candidate_index_scope": "dry_run_no_instance_mutation",
            "review_queue_scope": "dry_run_no_instance_mutation",
            "redacted_errors": True,
        },
        "fixture_smoke": fixture,
        "live_smoke": live,
        "totals": totals,
        "candidate_index_delta": {
            "status": "dry_run",
            "candidate_index_mutated": False,
            "write_scope": "dry_run_no_instance_mutation",
            "candidate_count": totals["candidates_created"],
            "review_required": True,
        },
        "review_queue_preview": {
            "status": "dry_run",
            "review_queue_mutated": False,
            "review_preview_count": totals["review_previews_created"],
            "accepted_truth_created": False,
        },
        "public_alpha_posture": {
            "public_alpha_launched": False,
            "public_exposure_enabled": False,
            "public_mutation_enabled": False,
            "public_workbench_enabled": False,
            "live_source_fanout_enabled": False,
            "downloads_uploads_enabled": False,
            "production_readiness_claimed": False,
        },
        "license_posture": {
            "source_available": True,
            "restricted": True,
            "non_open_source": True,
            "non_commercial": True,
            "public_service_hosting_authorized": False,
            "personal_local_evaluation_only": True,
            "license_posture_unchanged": True,
        },
        "safety": safety,
        "validation_notes": {
            "full_discovery_claimed": False,
            "aide_invoked_by_smoke": False,
            "aide_note": "The smoke command does not invoke AIDE or mutate the queue; repo commit hooks may run AIDE Lite commit checks separately.",
        },
    }


def _run_fixture_smoke(queries: Sequence[str]) -> dict[str, Any]:
    fixture_report = replay_fixture_directory_report()
    per_query: list[dict[str, Any]] = []
    violations: list[str] = []
    for query in queries:
        query_text = str(query).strip()
        if not query_text:
            continue
        plan = plan_ia_hunt_pipeline(query_text)
        outputs = run_ia_hunt_pipeline_dry_run(plan)
        boundary = build_ia_hunt_boundary_report(outputs)
        if boundary.get("violations"):
            violations.extend(str(item) for item in boundary.get("violations", []))
        per_query.append(_query_summary(query_text, plan, outputs, boundary))
    aggregate = _aggregate_query_counts(per_query)
    return {
        "schema_version": "ia_metadata_fixture_smoke.v0",
        "status": "PASS" if not violations else "FAIL",
        "fixture_replay_status": "PASS" if fixture_report.get("all_fixtures_replay") else "FAIL",
        "fixture_count": int(fixture_report.get("fixture_count", 0) or 0),
        "fixture_ids": list(fixture_report.get("fixture_ids", []) or []),
        "forbidden_network_imports_detected": bool(fixture_report.get("forbidden_network_imports_detected", False)),
        "query_count": len(per_query),
        "per_query": per_query,
        "aggregate": aggregate,
        "violations": sorted(set(violations)),
        "source_observation_creation_scope": "generated_report_only_dry_run_no_store_write",
        "reviewed_master_index_mutation": False,
        "public_fanout": False,
        "downloads": False,
        "file_fetching": False,
        "wayback_replay": False,
        "rights_safety_claims": False,
    }


def _query_summary(query: str, plan: Mapping[str, Any], outputs: Mapping[str, Any], boundary: Mapping[str, Any]) -> dict[str, Any]:
    source_cache_records = list(outputs.get("source_cache_records", []) or [])
    evidence_candidates = list(outputs.get("evidence_candidates", []) or [])
    candidate_records = list(outputs.get("candidate_records", []) or [])
    review_items = list(outputs.get("review_items", []) or [])
    candidate_report = dict(outputs.get("candidate_report", {}) or {})
    return {
        "schema_version": "ia_metadata_smoke_query_result.v0",
        "query": query,
        "workunit_count": int(plan.get("workunit_count", 0) or 0),
        "source_observations_created": len(source_cache_records),
        "evidence_summaries_created": len(evidence_candidates),
        "candidates_created": len(candidate_records),
        "review_previews_created": len(review_items),
        "candidate_index_dry_run_status": str(candidate_report.get("status", "")),
        "candidate_index_mutated": bool(boundary.get("candidate_index_mutated", False)),
        "review_queue_mutated": bool(boundary.get("review_queue_mutated", False)),
        "reviewed_index_mutated": bool(boundary.get("reviewed_index_mutated", False)),
        "master_index_mutated": bool(boundary.get("master_index_mutated", False)),
        "public_fanout": bool(boundary.get("public_fanout_enabled", False)),
        "downloads": bool(boundary.get("download_performed", False)),
        "file_fetching": False,
        "wayback_replay": False,
        "rights_safety_claims": False,
        "boundary_passed": bool(boundary.get("passed", False)),
        "violations": list(boundary.get("violations", []) or []),
    }


def _run_live_smoke(
    queries: Sequence[str],
    *,
    requested: bool,
    allow_live_metadata: bool,
    live_query_limit: int,
    rows: int,
    max_requests: int,
    timeout_seconds: int,
    contact: str,
    user_agent: str,
) -> dict[str, Any]:
    if not requested:
        return {
            "schema_version": "ia_metadata_live_smoke.v0",
            "status": "not_requested",
            "allow_live_metadata": allow_live_metadata,
            "query_count": 0,
            "live_metadata_request_performed": False,
            "total_http_requests": 0,
            "redacted_errors": [],
            "per_query": [],
        }
    if not allow_live_metadata:
        return {
            "schema_version": "ia_metadata_live_smoke.v0",
            "status": "operator_blocked",
            "allow_live_metadata": False,
            "query_count": 0,
            "live_metadata_request_performed": False,
            "total_http_requests": 0,
            "redacted_errors": ["--allow-live-metadata was not supplied; no live request was performed."],
            "per_query": [],
        }

    policy = load_live_probe_policy()
    max_policy_rows = int(policy.get("metadata_search_rows_max", 1))
    max_policy_requests = int(policy.get("total_http_requests_max", 2))
    bounded_rows = min(rows, max_policy_rows)
    bounded_requests = min(max_requests, max_policy_requests)
    selected = [str(item).strip() for item in queries if str(item).strip()][:live_query_limit]
    per_query: list[dict[str, Any]] = []
    redacted_errors: list[str] = []
    for query in selected:
        try:
            probe = run_live_metadata_probe(
                policy,
                approve_live=True,
                dry_run=False,
                query=query,
                rows=bounded_rows,
                max_requests=bounded_requests,
                client_label=user_agent,
                contact=contact,
                kill_switch_enabled=True,
            )
            summary = dict(probe.get("redacted_summary", {}) or {})
            boundary = dict(probe.get("boundary_report", {}) or {})
            per_query.append(
                {
                    "schema_version": "ia_metadata_live_smoke_query_result.v0",
                    "query": query,
                    "probe_status": str(summary.get("probe_status", "")),
                    "failure_reason": str(summary.get("failure_reason", "")),
                    "total_http_requests": int(summary.get("total_http_requests", 0) or 0),
                    "normalized_preview_count": int(summary.get("normalized_preview_count", 0) or 0),
                    "source_observations_created": 0,
                    "evidence_summaries_created": 0,
                    "candidates_created": 0,
                    "review_previews_created": 0,
                    "live_source_call_performed": bool(boundary.get("live_source_call_performed", False)),
                    "raw_response_committed": bool(boundary.get("raw_response_committed", False)),
                    "boundary_passed": bool(boundary.get("passed", False)),
                    "downloads": bool(boundary.get("download_performed", False)),
                    "file_fetching": False,
                    "wayback_replay": False,
                    "candidate_index_mutated": bool(boundary.get("candidate_index_mutated", False)),
                    "reviewed_index_mutated": bool(boundary.get("reviewed_index_mutated", False)),
                    "master_index_mutated": bool(boundary.get("master_index_mutated", False)),
                }
            )
        except Exception as exc:
            redacted_errors.append(_redact_error(exc))
            per_query.append(
                {
                    "schema_version": "ia_metadata_live_smoke_query_result.v0",
                    "query": query,
                    "probe_status": "unavailable",
                    "failure_reason": _redact_error(exc),
                    "total_http_requests": 0,
                    "normalized_preview_count": 0,
                    "source_observations_created": 0,
                    "evidence_summaries_created": 0,
                    "candidates_created": 0,
                    "review_previews_created": 0,
                    "live_source_call_performed": False,
                    "raw_response_committed": False,
                    "boundary_passed": True,
                    "downloads": False,
                    "file_fetching": False,
                    "wayback_replay": False,
                    "candidate_index_mutated": False,
                    "reviewed_index_mutated": False,
                    "master_index_mutated": False,
                }
            )
    live_performed = any(item.get("live_source_call_performed") for item in per_query)
    total_requests = sum(int(item.get("total_http_requests", 0) or 0) for item in per_query)
    failing = [
        item
        for item in per_query
        if str(item.get("probe_status", "")) not in {"succeeded", "zero_results", "rate_limited"}
    ]
    status = "PASS" if per_query and not failing else "PASS_WITH_WARNINGS"
    return {
        "schema_version": "ia_metadata_live_smoke.v0",
        "status": status,
        "allow_live_metadata": True,
        "query_count": len(per_query),
        "live_metadata_request_performed": live_performed,
        "total_http_requests": total_requests,
        "rows": bounded_rows,
        "max_requests": bounded_requests,
        "redacted_errors": redacted_errors,
        "per_query": per_query,
        "source_observation_creation_scope": "redacted_probe_preview_only_no_store_write",
    }


def _fixture_not_requested() -> dict[str, Any]:
    return {
        "schema_version": "ia_metadata_fixture_smoke.v0",
        "status": "not_requested",
        "query_count": 0,
        "per_query": [],
        "aggregate": _empty_counts(),
        "violations": [],
    }


def _aggregate_query_counts(items: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    aggregate = _empty_counts()
    for item in items:
        for key in aggregate:
            aggregate[key] += int(item.get(key, 0) or 0)
    return aggregate


def _empty_counts() -> dict[str, int]:
    return {
        "source_observations_created": 0,
        "evidence_summaries_created": 0,
        "candidates_created": 0,
        "review_previews_created": 0,
    }


def _totals(fixture: Mapping[str, Any], live: Mapping[str, Any]) -> dict[str, int]:
    totals = _empty_counts()
    fixture_aggregate = dict(fixture.get("aggregate", {}) or {})
    for key in totals:
        totals[key] += int(fixture_aggregate.get(key, 0) or 0)
    for item in live.get("per_query", []) or []:
        if isinstance(item, Mapping):
            for key in totals:
                totals[key] += int(item.get(key, 0) or 0)
    return totals


def _safety_summary(fixture: Mapping[str, Any], live: Mapping[str, Any]) -> dict[str, Any]:
    live_items = [dict(item) for item in live.get("per_query", []) or [] if isinstance(item, Mapping)]
    unsafe = {
        "public_fanout": False,
        "downloads": bool(fixture.get("downloads", False)) or any(bool(item.get("downloads", False)) for item in live_items),
        "file_fetching": False,
        "wayback_replay": False,
        "public_mutation": False,
        "public_workbench": False,
        "live_public_metadata": False,
        "reviewed_index_mutated": any(bool(item.get("reviewed_index_mutated", False)) for item in live_items),
        "master_index_mutated": any(bool(item.get("master_index_mutated", False)) for item in live_items),
        "rights_safety_claims": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    violations = [key for key in UNSAFE_FLAGS if unsafe.get(key)]
    return {
        "schema_version": "ia_metadata_smoke_safety_summary.v0",
        **unsafe,
        "reviewed_master_index_mutation": bool(unsafe["reviewed_index_mutated"] or unsafe["master_index_mutated"]),
        "local_live_metadata_probe_performed": bool(live.get("live_metadata_request_performed", False)),
        "live_source_http_requests": int(live.get("total_http_requests", 0) or 0),
        "violations": violations,
        "passed": not violations and not bool(fixture.get("violations")),
    }


def _overall_status(fixture: Mapping[str, Any], live: Mapping[str, Any], safety: Mapping[str, Any]) -> str:
    if not safety.get("passed", False) or fixture.get("status") == "FAIL":
        return "FAIL"
    if live.get("status") in {"operator_blocked", "PASS_WITH_WARNINGS"}:
        return "PASS_WITH_WARNINGS"
    if fixture.get("status") == "not_requested" and live.get("status") == "not_requested":
        return "FAIL"
    return "PASS"


def _write_report_pair(directory: Path, report: Mapping[str, Any]) -> dict[str, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    report_path = directory / REPORT_NAME
    summary_path = directory / SUMMARY_NAME
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary_path.write_text(_markdown_summary(report), encoding="utf-8")
    label = _label_for_directory(directory)
    return {f"{label}_json": report_path, f"{label}_markdown": summary_path}


def _rewrite_report_files(paths: Mapping[str, Path], report: Mapping[str, Any]) -> None:
    for name, path in paths.items():
        if name.endswith("_json"):
            path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        elif name.endswith("_markdown"):
            path.write_text(_markdown_summary(report), encoding="utf-8")


def _label_for_directory(directory: Path) -> str:
    normalized = directory.as_posix()
    if normalized.startswith("control/audits/") or "control/audits/" in normalized:
        return "audit"
    return "out"


def _markdown_summary(report: Mapping[str, Any]) -> str:
    totals = dict(report.get("totals", {}) or {})
    fixture = dict(report.get("fixture_smoke", {}) or {})
    live = dict(report.get("live_smoke", {}) or {})
    safety = dict(report.get("safety", {}) or {})
    return (
        "# IA Metadata Provider Wiring And Smoke v0\n\n"
        f"- task: {report.get('task_id')}\n"
        f"- status: {report.get('status')}\n"
        f"- mode: {report.get('mode')}\n"
        f"- query count: {report.get('query_count')}\n"
        f"- fixture status: {fixture.get('status')}\n"
        f"- live status: {live.get('status')}\n"
        f"- source observations created: {totals.get('source_observations_created', 0)}\n"
        f"- evidence summaries created: {totals.get('evidence_summaries_created', 0)}\n"
        f"- provisional candidates created: {totals.get('candidates_created', 0)}\n"
        f"- review previews created: {totals.get('review_previews_created', 0)}\n"
        f"- candidate-index delta: {dict(report.get('candidate_index_delta', {}) or {}).get('status')}\n"
        f"- reviewed/master-index mutation: {str(safety.get('reviewed_master_index_mutation', False)).lower()}\n"
        f"- public fanout: {str(safety.get('public_fanout', False)).lower()}\n"
        f"- downloads: {str(safety.get('downloads', False)).lower()}\n"
        f"- file fetching: {str(safety.get('file_fetching', False)).lower()}\n"
        f"- Wayback replay: {str(safety.get('wayback_replay', False)).lower()}\n"
        f"- rights/safety claims: {str(safety.get('rights_safety_claims', False)).lower()}\n"
        f"- public-alpha posture unchanged: true\n"
        f"- license posture unchanged: true\n"
        f"- full discovery claimed: false\n\n"
        "## Query Set\n\n"
        + "".join(f"- {query}\n" for query in report.get("queries", []) or [])
    )


def _redact_error(exc: BaseException) -> str:
    text = str(exc)
    lowered = text.lower()
    if "certificate_verify_failed" in lowered or "certificate verify failed" in lowered:
        return "ssl_certificate_verify_failed"
    if "timed out" in lowered or "timeout" in lowered:
        return "timeout"
    if "metadata search row cap exceeded" in lowered:
        return "metadata search row cap exceeded"
    if "total_http_requests_max exceeded" in lowered:
        return "total_http_requests_max exceeded"
    if "url" in lowered or "http" in lowered:
        return "transport_or_policy_error"
    return text[:160] if text else exc.__class__.__name__


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
