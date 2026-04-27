from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_external_baseline_observations import (  # noqa: E402
    DEFAULT_BATCHES_DIR,
    DEFAULT_OBSERVATIONS_DIR,
    PENDING_STATUS,
    validate_external_baseline_observations,
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Report manual external baseline observation coverage. This script "
            "does not query external systems."
        )
    )
    parser.add_argument(
        "--observations-dir",
        default=str(DEFAULT_OBSERVATIONS_DIR),
        help="Directory of observation JSON files.",
    )
    parser.add_argument(
        "--batches-dir",
        default=str(DEFAULT_BATCHES_DIR),
        help="Directory of manual observation batch directories.",
    )
    parser.add_argument("--batch", help="Report one manual observation batch.")
    parser.add_argument(
        "--next-pending",
        action="store_true",
        help="Include pending slots that are ready for manual observation.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    validation = validate_external_baseline_observations(
        observations_dir=Path(args.observations_dir),
        batches_dir=Path(args.batches_dir),
    )
    global_pending = sum(
        counts.get(PENDING_STATUS, 0)
        for counts in validation["status_counts_by_system"].values()
    )
    global_observed = sum(
        counts.get("observed", 0)
        for counts in validation["status_counts_by_system"].values()
    )
    batches = validation.get("batches", {})
    errors = list(validation["errors"])
    if args.batch and args.batch not in batches:
        errors.append(f"Unknown batch id '{args.batch}'.")
    selected_batches = (
        {args.batch: batches[args.batch]}
        if args.batch and args.batch in batches
        else batches
    )
    next_pending_slots = []
    if args.next_pending:
        for batch_report in selected_batches.values():
            if not isinstance(batch_report, dict):
                continue
            next_pending_slots.extend(
                slot
                for slot in batch_report.get("next_pending_slots", [])
                if isinstance(slot, dict)
            )

    report = {
        "status": "ready" if validation["status"] == "valid" and not errors else "invalid",
        "created_by": "manual_external_baseline_status_report_v0",
        "validation_status": validation["status"],
        "query_count": validation["query_count"],
        "systems": validation["systems"],
        "selected_batch": args.batch,
        "global_slot_counts": {
            "pending_manual_observation": global_pending,
            "observed": global_observed,
        },
        "status_counts_by_system": validation["status_counts_by_system"],
        "query_coverage": validation["query_coverage"],
        "batches": selected_batches,
        "next_pending_slots": next_pending_slots,
        "observed_query_ids": {
            system_id: coverage["observed_query_count"]
            for system_id, coverage in validation["query_coverage"].items()
        },
        "missing_observation_slots": {
            system_id: max(
                0,
                coverage["expected_query_count"]
                - coverage["observed_query_count"],
            )
            for system_id, coverage in validation["query_coverage"].items()
        },
        "limitations": [
            "Pending slots are not observed baselines.",
            "This report performs no external querying or scraping.",
            "Future observed records are manual, time-sensitive, and not global truth.",
        ],
        "errors": errors,
    }
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain_report(report))
    return 0 if report["status"] == "ready" else 1


def _format_plain_report(report: dict[str, object]) -> str:
    global_slot_counts = report["global_slot_counts"]
    assert isinstance(global_slot_counts, dict)
    lines = [
        "External baseline observation status",
        f"status: {report['status']}",
        f"query_count: {report['query_count']}",
        f"global_pending_slots: {global_slot_counts['pending_manual_observation']}",
        f"global_observed_slots: {global_slot_counts['observed']}",
    ]
    if report.get("selected_batch"):
        lines.append(f"selected_batch: {report['selected_batch']}")
    lines.extend(["", "Systems"])
    counts_by_system = report["status_counts_by_system"]
    coverage_by_system = report["query_coverage"]
    assert isinstance(counts_by_system, dict)
    assert isinstance(coverage_by_system, dict)
    for system_id in report["systems"]:  # type: ignore[assignment]
        counts = counts_by_system[system_id]
        coverage = coverage_by_system[system_id]
        lines.append(
            "- "
            f"{system_id}: pending={counts.get(PENDING_STATUS, 0)}, "
            f"observed={counts.get('observed', 0)}, "
            f"expected_queries={coverage['expected_query_count']}"
        )
    batches = report.get("batches", {})
    if isinstance(batches, dict) and batches:
        lines.append("")
        lines.append("Batches")
        for batch_id, batch in sorted(batches.items()):
            if not isinstance(batch, dict):
                continue
            lines.append(
                "- "
                f"{batch_id}: pending={batch.get('pending_observation_count', 0)}, "
                f"observed={batch.get('observed_observation_count', 0)}, "
                f"expected={batch.get('expected_observation_count', 0)}, "
                f"completion={batch.get('completion_percent', 0)}%"
            )
    next_pending = report.get("next_pending_slots", [])
    if isinstance(next_pending, list) and next_pending:
        lines.append("")
        lines.append("Next Pending Slots")
        for slot in next_pending:
            if not isinstance(slot, dict):
                continue
            lines.append(
                "- "
                f"{slot.get('batch_id', '')} / {slot.get('query_id', '')} / "
                f"{slot.get('system_id', '')}"
            )
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])  # type: ignore[union-attr]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
