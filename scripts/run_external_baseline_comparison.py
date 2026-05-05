#!/usr/bin/env python3
"""Run External Baseline Comparison Report v0 over committed manual records.

This script is intentionally local-only. It reads existing manual baseline
observation records and current Eureka local-index audit artifacts; it does not
query external search engines, source APIs, hosted backends, or model APIs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_external_baseline_observations import (  # noqa: E402
    DEFAULT_BATCHES_DIR,
    DEFAULT_OBSERVATIONS_DIR,
    PENDING_STATUS,
    validate_external_baseline_observations,
)


COMPARISON_LABELS = (
    "eureka_better",
    "baseline_better",
    "both_good",
    "both_partial",
    "eureka_only",
    "baseline_only",
    "neither",
    "not_comparable",
    "insufficient_data",
)
NO_FABRICATION_GUARANTEES = {
    "external_calls_performed": False,
    "live_source_calls_performed": False,
    "model_calls_performed": False,
    "fabricated_observations": False,
    "fabricated_comparisons": False,
    "production_claimed": False,
    "superiority_claimed": False,
}


def run_external_baseline_comparison(
    *,
    batch_id: str | None = "batch_0",
    all_batches: bool = False,
) -> dict[str, Any]:
    validation = validate_external_baseline_observations(
        observations_dir=DEFAULT_OBSERVATIONS_DIR,
        batches_dir=DEFAULT_BATCHES_DIR,
    )
    batches = validation.get("batches", {})
    errors = list(validation.get("errors", []))
    selected_batches = _select_batches(batches, batch_id=batch_id, all_batches=all_batches, errors=errors)

    observed_count = sum(_int(batch.get("observed_observation_count")) for batch in selected_batches.values())
    pending_count = sum(_int(batch.get("pending_observation_count")) for batch in selected_batches.values())
    invalid_count = len(errors)
    query_comparisons: list[dict[str, Any]] = []
    local_audit_summary: dict[str, Any] = {}
    local_audit_error: str | None = None

    eligibility = _eligibility(
        observed_count=observed_count,
        pending_count=pending_count,
        invalid_count=invalid_count,
        selected_batch_count=len(selected_batches),
    )

    if observed_count > 0 and invalid_count == 0:
        local_audit_summary, local_audit_error = _load_local_search_audit()
        if local_audit_error:
            eligibility = "local_search_unavailable"
        else:
            observed_records = _collect_observed_records(
                selected_batch_ids=set(selected_batches) if not all_batches else None
            )
            query_comparisons = _compare_records(observed_records, local_audit_summary)
            if query_comparisons:
                eligibility = "comparison_completed"

    aggregate_summary = _aggregate(query_comparisons)
    comparison_completed = bool(query_comparisons)
    hosted = _load_hosted_deployment_status()
    public_index = _load_public_index_summary()

    ok = invalid_count == 0 and local_audit_error is None
    if observed_count == 0 and invalid_count == 0:
        ok = True

    return {
        "ok": ok,
        "comparison_id": "external_baseline_comparison_v0",
        "batch_id": "all_batches" if all_batches else batch_id,
        "eligibility": eligibility,
        "comparison_completed": comparison_completed,
        "observed_count": observed_count,
        "pending_count": pending_count,
        "invalid_count": invalid_count,
        "compared_count": len(query_comparisons),
        "eureka_search_mode": public_index.get("search_mode", "local_index_only"),
        "hosted_backend_verified": hosted.get("backend_deployment_verified", False),
        "static_site_verified": hosted.get("static_deployment_verified", False),
        "external_sources_observed": _observed_sources(selected_batches),
        "query_comparisons": query_comparisons,
        "aggregate_summary": aggregate_summary,
        "gap_summary": _gap_summary(validation, selected_batches, local_audit_summary),
        "baseline_status": {
            "validation_status": validation.get("status"),
            "global_slot_counts": _global_slot_counts(validation),
            "selected_batches": _sanitize_batches(selected_batches),
            "errors": errors,
        },
        "hosted_deployment_status": hosted,
        "public_index_status": public_index,
        "local_search_audit_error": local_audit_error,
        "limitations": [
            "Manual external observations are required before a true comparison is eligible.",
            "Pending baseline slots are not external baseline observations.",
            "Eureka results are local_index_only and do not represent live web/source recall.",
            "This script performs no external calls, model calls, source calls, or index/cache/ledger mutation.",
        ],
        "no_fabrication_guarantees": dict(NO_FABRICATION_GUARANTEES),
        "external_calls_performed": False,
        "live_source_calls_performed": False,
        "model_calls_performed": False,
        "fabricated_observations": False,
        "fabricated_comparisons": False,
        "production_claimed": False,
        "superiority_claimed": False,
        "notes": _notes(observed_count, pending_count, invalid_count, local_audit_error),
    }


def _select_batches(
    batches: Any,
    *,
    batch_id: str | None,
    all_batches: bool,
    errors: list[str],
) -> dict[str, Mapping[str, Any]]:
    if not isinstance(batches, Mapping):
        errors.append("baseline validation did not return batch reports.")
        return {}
    if all_batches:
        return {
            str(key): value
            for key, value in batches.items()
            if isinstance(value, Mapping)
        }
    if not batch_id:
        errors.append("batch id is required unless --all-batches is used.")
        return {}
    selected = batches.get(batch_id)
    if not isinstance(selected, Mapping):
        errors.append(f"Unknown batch id '{batch_id}'.")
        return {}
    return {batch_id: selected}


def _eligibility(
    *,
    observed_count: int,
    pending_count: int,
    invalid_count: int,
    selected_batch_count: int,
) -> str:
    if selected_batch_count == 0:
        return "invalid_observations"
    if invalid_count:
        return "invalid_observations"
    if observed_count == 0:
        return "no_observations"
    if pending_count:
        return "partial_observations"
    return "eligible"


def _collect_observed_records(*, selected_batch_ids: set[str] | None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    roots = [DEFAULT_OBSERVATIONS_DIR]
    if selected_batch_ids is None:
        roots.extend(path / "observations" for path in DEFAULT_BATCHES_DIR.iterdir() if path.is_dir())
    else:
        roots.extend(DEFAULT_BATCHES_DIR / batch_id / "observations" for batch_id in selected_batch_ids)
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.glob("*.json")):
            payload = _load_json(path)
            if not isinstance(payload, Mapping) or "manifest_id" in payload:
                continue
            raw_records = payload.get("observations", [payload])
            if not isinstance(raw_records, list):
                continue
            for record in raw_records:
                if not isinstance(record, Mapping):
                    continue
                if record.get("observation_status") != "observed":
                    continue
                batch_id = str(record.get("batch_id") or _batch_id_from_path(path) or "")
                if selected_batch_ids is not None and batch_id not in selected_batch_ids:
                    continue
                records.append(dict(record))
    return records


def _load_local_search_audit() -> tuple[dict[str, Any], str | None]:
    command = [sys.executable, "scripts/run_search_usefulness_audit.py", "--json"]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return {}, completed.stderr.strip() or completed.stdout.strip() or "search usefulness audit failed"
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return {}, f"search usefulness audit JSON parse failed: {exc}"
    if not isinstance(payload, dict):
        return {}, "search usefulness audit output was not a JSON object"
    return payload, None


def _compare_records(records: list[Mapping[str, Any]], local_audit: Mapping[str, Any]) -> list[dict[str, Any]]:
    eureka_by_query = {
        str(item.get("query_id")): item
        for item in local_audit.get("queries", [])
        if isinstance(item, Mapping) and item.get("query_id")
    }
    comparisons: list[dict[str, Any]] = []
    for record in records:
        query_id = str(record.get("query_id") or "")
        eureka = eureka_by_query.get(query_id, {})
        external_count = len(record.get("top_results", [])) if isinstance(record.get("top_results"), list) else 0
        eureka_count = _int(eureka.get("search_result_count")) if isinstance(eureka, Mapping) else 0
        eureka_status = str(eureka.get("eureka_status") or "unknown") if isinstance(eureka, Mapping) else "unknown"
        label = _comparison_label(external_count, eureka_count, eureka_status)
        comparisons.append(
            {
                "query_id": query_id,
                "query_text": str(record.get("query_text") or eureka.get("query") or ""),
                "external_baseline_source": str(record.get("system_id") or ""),
                "external_baseline_observed_result_summary": _external_summary(record),
                "eureka_result_summary": _eureka_summary(eureka),
                "comparison_label": label,
                "reason": _comparison_reason(label, external_count, eureka_count, eureka_status),
                "source_capability_gap": sorted(set(eureka.get("failure_modes", []))) if isinstance(eureka, Mapping) else [],
                "limitations": [
                    "Comparison is scoped to one manual observation record and current local_index_only behavior.",
                    "No external re-query was performed.",
                ],
            }
        )
    return comparisons


def _comparison_label(external_count: int, eureka_count: int, eureka_status: str) -> str:
    if external_count and eureka_count:
        return "both_good" if eureka_status == "covered" else "both_partial"
    if eureka_count and not external_count:
        return "eureka_only"
    if external_count and not eureka_count:
        return "baseline_only"
    if not external_count and not eureka_count:
        return "neither"
    return "insufficient_data"


def _comparison_reason(label: str, external_count: int, eureka_count: int, eureka_status: str) -> str:
    return (
        f"{label}: manual baseline result count={external_count}, "
        f"Eureka local_index_only result count={eureka_count}, Eureka status={eureka_status}."
    )


def _external_summary(record: Mapping[str, Any]) -> str:
    top_results = record.get("top_results")
    if not isinstance(top_results, list) or not top_results:
        return "No manually recorded useful result in the observation record."
    first = top_results[0] if isinstance(top_results[0], Mapping) else {}
    title = str(first.get("title") or "manual result")
    rank = first.get("rank")
    return f"{len(top_results)} recorded result(s); first useful visible result: rank {rank}, {title}."


def _eureka_summary(eureka: Any) -> str:
    if not isinstance(eureka, Mapping) or not eureka:
        return "No local Eureka audit entry matched this query id."
    return (
        f"{eureka.get('eureka_status', 'unknown')} with "
        f"{eureka.get('search_result_count', 0)} local_index_only result(s)."
    )


def _aggregate(comparisons: list[Mapping[str, Any]]) -> dict[str, int]:
    counts = {f"{label}_count": 0 for label in COMPARISON_LABELS}
    for item in comparisons:
        label = str(item.get("comparison_label") or "insufficient_data")
        if label not in COMPARISON_LABELS:
            label = "insufficient_data"
        counts[f"{label}_count"] += 1
    counts["compared_count"] = len(comparisons)
    return counts


def _gap_summary(
    validation: Mapping[str, Any],
    selected_batches: Mapping[str, Mapping[str, Any]],
    local_audit: Mapping[str, Any],
) -> dict[str, Any]:
    failure_modes = local_audit.get("failure_mode_counts") if isinstance(local_audit, Mapping) else {}
    recommendations = local_audit.get("future_work_recommendations") if isinstance(local_audit, Mapping) else []
    return {
        "external_baseline_pending": sum(_int(batch.get("pending_observation_count")) for batch in selected_batches.values()),
        "external_baseline_global_pending": _global_slot_counts(validation).get(PENDING_STATUS, 0),
        "source_gap_count": _int((local_audit.get("eureka_status_counts") or {}).get("source_gap")) if isinstance(local_audit.get("eureka_status_counts"), Mapping) else None,
        "capability_gap_count": _int((local_audit.get("eureka_status_counts") or {}).get("capability_gap")) if isinstance(local_audit.get("eureka_status_counts"), Mapping) else None,
        "failure_mode_counts": failure_modes if isinstance(failure_modes, Mapping) else {},
        "future_work_recommendations": recommendations if isinstance(recommendations, list) else [],
        "live_connector_absence": True,
        "source_cache_runtime_absence": True,
        "evidence_ledger_runtime_absence": True,
    }


def _global_slot_counts(validation: Mapping[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {PENDING_STATUS: 0, "observed": 0}
    for status_counts in validation.get("status_counts_by_system", {}).values():
        if not isinstance(status_counts, Mapping):
            continue
        counts[PENDING_STATUS] += _int(status_counts.get(PENDING_STATUS))
        counts["observed"] += _int(status_counts.get("observed"))
    return counts


def _observed_sources(selected_batches: Mapping[str, Mapping[str, Any]]) -> list[str]:
    sources: set[str] = set()
    for batch in selected_batches.values():
        slots = batch.get("observation_slots", [])
        if not isinstance(slots, list):
            continue
        for slot in slots:
            if isinstance(slot, Mapping) and slot.get("observation_status") == "observed":
                system_id = str(slot.get("system_id") or "")
                if system_id:
                    sources.add(system_id)
    return sorted(sources)


def _sanitize_batches(selected_batches: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for batch_id, batch in selected_batches.items():
        sanitized[batch_id] = {
            "status": batch.get("status"),
            "selected_query_count": batch.get("selected_query_count"),
            "selected_system_count": batch.get("selected_system_count"),
            "expected_observation_count": batch.get("expected_observation_count"),
            "observation_count": batch.get("observation_count"),
            "pending_observation_count": batch.get("pending_observation_count"),
            "observed_observation_count": batch.get("observed_observation_count"),
            "completion_percent": batch.get("completion_percent"),
            "selected_query_ids": batch.get("selected_query_ids"),
            "selected_system_ids": batch.get("selected_system_ids"),
            "missing_observation_slots": batch.get("missing_observation_slots"),
            "observed_query_ids": batch.get("observed_query_ids"),
        }
    return sanitized


def _load_hosted_deployment_status() -> dict[str, Any]:
    path = REPO_ROOT / "control" / "audits" / "public-hosted-deployment-evidence-v0" / "public_hosted_deployment_evidence_report.json"
    payload = _load_json(path)
    if isinstance(payload, Mapping):
        return {
            "static_site_status": payload.get("static_site_status", "evidence_unavailable"),
            "hosted_backend_status": payload.get("hosted_backend_status", "evidence_unavailable"),
            "static_deployment_verified": payload.get("static_deployment_verified") is True,
            "backend_deployment_verified": payload.get("backend_deployment_verified") is True,
            "deployment_verified": payload.get("deployment_verified") is True,
        }
    return {
        "static_site_status": "evidence_unavailable",
        "hosted_backend_status": "evidence_unavailable",
        "static_deployment_verified": False,
        "backend_deployment_verified": False,
        "deployment_verified": False,
    }


def _load_public_index_summary() -> dict[str, Any]:
    for path in (
        REPO_ROOT / "data" / "public_index" / "public_index_summary.json",
        REPO_ROOT / "site" / "dist" / "data" / "public_index_summary.json",
    ):
        payload = _load_json(path)
        if isinstance(payload, Mapping):
            return {
                "path": str(path.relative_to(REPO_ROOT)),
                "document_count": payload.get("document_count"),
                "source_count": payload.get("source_count"),
                "contains_private_data": payload.get("contains_private_data"),
                "contains_live_data": payload.get("contains_live_data"),
                "local_index_only": payload.get("local_index_only"),
                "search_mode": "local_index_only" if payload.get("local_index_only") is True else "unknown",
            }
    return {
        "path": None,
        "document_count": None,
        "source_count": None,
        "contains_private_data": None,
        "contains_live_data": None,
        "local_index_only": None,
        "search_mode": "unknown",
    }


def _notes(
    observed_count: int,
    pending_count: int,
    invalid_count: int,
    local_audit_error: str | None,
) -> list[str]:
    notes = [
        "Fast learning, slow truth: this comparison uses only recorded evidence.",
        "No manual external baseline observation is created by this script.",
    ]
    if observed_count == 0:
        notes.append("No valid manual external baseline observations are present; comparison is not eligible.")
    if pending_count:
        notes.append(f"{pending_count} selected baseline observation slot(s) remain pending.")
    if invalid_count:
        notes.append(f"{invalid_count} baseline validation issue(s) block comparison.")
    if local_audit_error:
        notes.append(f"Local Eureka search audit unavailable: {local_audit_error}")
    return notes


def _batch_id_from_path(path: Path) -> str | None:
    parts = path.parts
    if "batches" not in parts:
        return None
    index = parts.index("batches")
    if index + 1 < len(parts):
        return parts[index + 1]
    return None


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "External Baseline Comparison Report v0",
        f"ok: {report.get('ok')}",
        f"batch_id: {report.get('batch_id')}",
        f"eligibility: {report.get('eligibility')}",
        f"observed_count: {report.get('observed_count')}",
        f"pending_count: {report.get('pending_count')}",
        f"invalid_count: {report.get('invalid_count')}",
        f"compared_count: {report.get('compared_count')}",
    ]
    notes = report.get("notes", [])
    if isinstance(notes, list):
        lines.append("notes:")
        lines.extend(f"- {note}" for note in notes)
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", default="batch_0", help="Manual baseline batch id to compare.")
    parser.add_argument("--all-batches", action="store_true", help="Use every manual baseline batch.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--strict", action="store_true", help="Return nonzero for invalid records or local comparison failures.")
    parser.add_argument("--output", help="Optional explicit JSON output path.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = run_external_baseline_comparison(
        batch_id=args.batch,
        all_batches=args.all_batches,
    )
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = REPO_ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))

    if args.strict and not report["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
