#!/usr/bin/env python3
"""Report Manual Observation Batch 0 status without external calls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_external_baseline_observations import (  # noqa: E402
    DEFAULT_BATCHES_DIR,
    DEFAULT_OBSERVATIONS_DIR,
    PENDING_STATUS,
    validate_external_baseline_observations,
)


VALID_STATUS_VALUES = {
    "complete",
    "partial",
    "pending",
    "invalid",
    "missing",
    "not_applicable",
    "blocked",
    "ready_for_human_operation",
    "ready_for_comparison",
    "comparison_not_eligible",
}


def _batch_status(batch: Mapping[str, Any] | None, validation_status: str, errors: list[str]) -> str:
    if batch is None:
        return "missing"
    if validation_status != "valid" or errors:
        return "invalid"
    expected = _int(batch.get("expected_observation_count"))
    observed = _int(batch.get("observed_observation_count"))
    pending = _int(batch.get("pending_observation_count"))
    if expected > 0 and observed == expected and pending == 0:
        return "complete"
    if observed > 0 and pending > 0:
        return "partial"
    return "pending"


def _comparison_status(batch: Mapping[str, Any] | None, invalid_count: int) -> str:
    if batch is None:
        return "blocked"
    if invalid_count:
        return "blocked"
    observed = _int(batch.get("observed_observation_count"))
    pending = _int(batch.get("pending_observation_count"))
    expected = _int(batch.get("expected_observation_count"))
    if observed == 0:
        return "comparison_not_eligible"
    if expected > 0 and observed == expected and pending == 0:
        return "ready_for_comparison"
    return "partial"


def build_status(
    *,
    batch_id: str = "batch_0",
    observations_dir: Path = DEFAULT_OBSERVATIONS_DIR,
    batches_dir: Path = DEFAULT_BATCHES_DIR,
) -> dict[str, Any]:
    errors: list[str] = []
    try:
        validation = validate_external_baseline_observations(
            observations_dir=observations_dir,
            batches_dir=batches_dir,
        )
    except Exception as exc:  # pragma: no cover - defensive, still local-only.
        validation = {"status": "invalid", "batches": {}, "errors": [str(exc)]}

    errors.extend(str(error) for error in validation.get("errors", []))
    batches = validation.get("batches", {})
    batch = batches.get(batch_id) if isinstance(batches, Mapping) else None
    if batch is not None and not isinstance(batch, Mapping):
        errors.append(f"{batch_id}: batch report must be an object")
        batch = None

    validation_status = str(validation.get("status") or "invalid")
    observed_count = _int(batch.get("observed_observation_count")) if batch else 0
    pending_count = _int(batch.get("pending_observation_count")) if batch else 0
    expected_count = _int(batch.get("expected_observation_count")) if batch else 0
    invalid_count = 0 if validation_status == "valid" and not errors else len(errors) or 1
    valid_count = observed_count if invalid_count == 0 else 0
    batch_status = _batch_status(batch, validation_status, errors)
    comparison_status = _comparison_status(batch, invalid_count)
    human_status = "ready_for_human_operation" if batch is not None and invalid_count == 0 else "blocked"

    task_review = []
    if batch is not None:
        for slot in batch.get("observation_slots", []):
            if not isinstance(slot, Mapping):
                continue
            task_review.append(
                {
                    "task_id": str(slot.get("query_id") or ""),
                    "query_text": str(slot.get("query_text") or ""),
                    "external_source": str(slot.get("system_id") or ""),
                    "observation_status": str(slot.get("observation_status") or ""),
                    "validation_status": "valid_pending_slot"
                    if slot.get("observation_status") == PENDING_STATUS and invalid_count == 0
                    else "review_required",
                }
            )

    return {
        "status": "ready" if invalid_count == 0 else "invalid",
        "created_by": "manual_observation_batch_0_status_report_v0",
        "batch_id": batch_id,
        "batch_0_status": batch_status,
        "observation_schema_status": "complete"
        if (REPO_ROOT / "evals/search_usefulness/external_baselines/observation.schema.json").is_file()
        else "missing",
        "observation_validator_status": "complete"
        if (REPO_ROOT / "scripts/validate_external_baseline_observations.py").is_file()
        else "missing",
        "observation_record_status": "pending" if pending_count and observed_count == 0 else batch_status,
        "comparison_readiness_status": comparison_status,
        "human_work_status": human_status,
        "expected_observation_count": expected_count,
        "observed_count": observed_count,
        "pending_count": pending_count,
        "invalid_count": invalid_count,
        "valid_count": valid_count,
        "task_review_summary": task_review,
        "hard_booleans": {
            "follow_up_plan_only": True,
            "manual_observations_performed_by_codex": False,
            "external_calls_performed": False,
            "web_browsing_performed": False,
            "fabricated_observations": False,
            "fabricated_external_results": False,
            "comparison_claimed_complete": False,
            "public_index_mutated": False,
            "local_index_mutated": False,
            "master_index_mutated": False,
            "source_cache_mutated": False,
            "evidence_ledger_mutated": False,
            "candidate_index_mutated": False,
            "telemetry_enabled": False,
            "accounts_enabled": False,
            "uploads_enabled": False,
            "downloads_enabled": False,
        },
        "errors": errors,
        "notes": [
            "Read-only local report over existing external baseline files.",
            "No browser, network, external API, scraping, or observation execution is invoked.",
            "Pending slots are not observations.",
        ],
    }


def _int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Manual Observation Batch 0 status",
        f"status: {report['status']}",
        f"batch_id: {report['batch_id']}",
        f"batch_0_status: {report['batch_0_status']}",
        f"observed_count: {report['observed_count']}",
        f"pending_count: {report['pending_count']}",
        f"invalid_count: {report['invalid_count']}",
        f"comparison_readiness_status: {report['comparison_readiness_status']}",
    ]
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", default="batch_0", help="Manual observation batch id.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args(argv)
    report = build_status(batch_id=args.batch)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_format_plain(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

