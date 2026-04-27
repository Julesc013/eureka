from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_external_baseline_observations import (  # noqa: E402
    DEFAULT_BATCHES_DIR,
    DEFAULT_OBSERVATIONS_DIR,
    VALID_STATUSES,
    validate_external_baseline_observations,
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "List manual external-baseline observation slots. This helper reads "
            "local pending/observed files only and performs no external queries."
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
    parser.add_argument("--batch", help="Filter to one batch id, for example batch_0.")
    parser.add_argument("--query-id", help="Filter to one search-usefulness query id.")
    parser.add_argument("--system-id", help="Filter to one external baseline system id.")
    parser.add_argument(
        "--status",
        choices=sorted(VALID_STATUSES),
        help="Filter by observation status.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = build_listing(
        observations_dir=Path(args.observations_dir),
        batches_dir=Path(args.batches_dir),
        batch=args.batch,
        query_id=args.query_id,
        system_id=args.system_id,
        status=args.status,
    )
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain_listing(report))
    return 0 if report["status"] == "ready" else 1


def build_listing(
    *,
    observations_dir: Path = DEFAULT_OBSERVATIONS_DIR,
    batches_dir: Path = DEFAULT_BATCHES_DIR,
    batch: str | None = None,
    query_id: str | None = None,
    system_id: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    validation = validate_external_baseline_observations(
        observations_dir=observations_dir,
        batches_dir=batches_dir,
    )
    slots: list[dict[str, Any]] = []
    for batch_id, batch_report in validation.get("batches", {}).items():
        if batch and batch_id != batch:
            continue
        if not isinstance(batch_report, Mapping):
            continue
        for slot in batch_report.get("observation_slots", []):
            if not isinstance(slot, Mapping):
                continue
            slot_batch = str(slot.get("batch_id") or batch_id)
            slot_query = str(slot.get("query_id") or "")
            slot_system = str(slot.get("system_id") or "")
            slot_status = str(slot.get("observation_status") or "")
            if query_id and slot_query != query_id:
                continue
            if system_id and slot_system != system_id:
                continue
            if status and slot_status != status:
                continue
            slots.append(
                {
                    "batch_id": slot_batch,
                    "observation_id": str(slot.get("observation_id") or ""),
                    "query_id": slot_query,
                    "query_text": str(slot.get("query_text") or ""),
                    "system_id": slot_system,
                    "observation_status": slot_status,
                }
            )
    errors = list(validation.get("errors", []))
    if batch and batch not in validation.get("batches", {}):
        errors.append(f"Unknown batch id '{batch}'.")
    return {
        "status": "ready" if validation["status"] == "valid" and not errors else "invalid",
        "created_by": "manual_observation_entry_helper_v0",
        "filters": {
            "batch": batch,
            "query_id": query_id,
            "system_id": system_id,
            "status": status,
        },
        "slot_count": len(slots),
        "slots": slots,
        "errors": errors,
    }


def _format_plain_listing(report: Mapping[str, Any]) -> str:
    lines = [
        "Manual external baseline observation slots",
        f"status: {report['status']}",
        f"slot_count: {report['slot_count']}",
    ]
    slots = report.get("slots", [])
    if isinstance(slots, list):
        for slot in slots:
            if not isinstance(slot, Mapping):
                continue
            lines.append(
                " / ".join(
                    [
                        str(slot.get("batch_id", "")),
                        str(slot.get("query_id", "")),
                        str(slot.get("system_id", "")),
                        str(slot.get("observation_status", "")),
                    ]
                )
            )
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
