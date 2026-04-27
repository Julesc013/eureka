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
    PENDING_STATUS,
    validate_external_baseline_observations,
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Create one fillable manual external-baseline observation file from "
            "a pending batch slot. This helper performs no external queries."
        )
    )
    parser.add_argument("--batch", required=True, help="Batch id, for example batch_0.")
    parser.add_argument("--query-id", required=True, help="Selected query id.")
    parser.add_argument("--system-id", required=True, help="Selected external system id.")
    parser.add_argument("--operator", help="Optional human operator name to prefill.")
    parser.add_argument("--output", help="Optional output path for the fillable JSON file.")
    parser.add_argument("--stdout", action="store_true", help="Print the JSON instead of writing.")
    parser.add_argument("--force", action="store_true", help="Overwrite --output if it exists.")
    parser.add_argument(
        "--observations-dir",
        default=str(DEFAULT_OBSERVATIONS_DIR),
        help="Directory of global observation JSON files for validation context.",
    )
    parser.add_argument(
        "--batches-dir",
        default=str(DEFAULT_BATCHES_DIR),
        help="Directory of manual observation batch directories.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    result = create_observation_record(
        batch=args.batch,
        query_id=args.query_id,
        system_id=args.system_id,
        operator=args.operator,
        observations_dir=Path(args.observations_dir),
        batches_dir=Path(args.batches_dir),
    )
    output = stdout or sys.stdout
    if result["status"] != "ready":
        output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return 1

    record = result["observation"]
    rendered = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.stdout:
        output.write(rendered)
        return 0

    output_path = (
        Path(args.output)
        if args.output
        else _default_output_path(Path(args.batches_dir), args.batch, args.query_id, args.system_id)
    )
    if output_path.exists() and not args.force:
        output.write(f"{output_path}: output file exists; use --force to overwrite.\n")
        return 1
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    output.write(f"Created pending manual observation file: {output_path}\n")
    output.write("Status remains pending_manual_observation until a human fills it.\n")
    return 0


def create_observation_record(
    *,
    batch: str,
    query_id: str,
    system_id: str,
    operator: str | None = None,
    observations_dir: Path = DEFAULT_OBSERVATIONS_DIR,
    batches_dir: Path = DEFAULT_BATCHES_DIR,
) -> dict[str, Any]:
    validation = validate_external_baseline_observations(
        observations_dir=observations_dir,
        batches_dir=batches_dir,
    )
    errors = list(validation.get("errors", []))
    batch_report = validation.get("batches", {}).get(batch)
    if not isinstance(batch_report, Mapping):
        errors.append(f"Unknown batch id '{batch}'.")
        return _invalid(errors)
    if validation["status"] != "valid":
        return _invalid(errors)

    matching_slot: Mapping[str, Any] | None = None
    for slot in batch_report.get("observation_slots", []):
        if not isinstance(slot, Mapping):
            continue
        if slot.get("query_id") == query_id and slot.get("system_id") == system_id:
            matching_slot = slot
            break
    if matching_slot is None:
        return _invalid([f"No pending slot for {batch}/{query_id}/{system_id}."])
    if matching_slot.get("observation_status") != PENDING_STATUS:
        return _invalid([f"Slot {batch}/{query_id}/{system_id} is not pending."])

    record = {
        "observation_id": f"manual_entry::{batch}::{query_id}::{system_id}",
        "query_id": query_id,
        "query_text": str(matching_slot.get("query_text") or ""),
        "system_id": system_id,
        "observation_status": PENDING_STATUS,
        "operator": operator,
        "observed_at": None,
        "browser_or_tool": None,
        "location_context_optional": None,
        "exact_query_submitted": None,
        "filters_or_scope": None,
        "result_count_visible_optional": None,
        "collection_method": PENDING_STATUS,
        "top_results": [],
        "first_useful_result_rank": None,
        "first_useful_result_reason": None,
        "usefulness_scores": None,
        "failure_modes": ["external_baseline_pending"],
        "comparison_notes": [],
        "next_eureka_work": [],
        "evidence_limitations": [
            "Generated pending entry only; human observation is required before observed status."
        ],
        "staleness_notes": [
            "No observation time recorded; external results remain time-sensitive."
        ],
        "notes": [
            "Created by Manual Observation Entry Helper v0 for later human editing.",
            "Do not mark observed until manual top results and required metadata are entered.",
        ],
        "created_by": "manual_observation_entry_helper_v0",
        "schema_version": "manual_external_baseline_observation.v0",
    }
    return {
        "status": "ready",
        "created_by": "manual_observation_entry_helper_v0",
        "observation": record,
        "errors": [],
    }


def _default_output_path(batches_dir: Path, batch: str, query_id: str, system_id: str) -> Path:
    filename = f"observed__{_safe_filename(query_id)}__{_safe_filename(system_id)}.json"
    return batches_dir / batch / "observations" / filename


def _safe_filename(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in value)


def _invalid(errors: list[str]) -> dict[str, Any]:
    return {
        "status": "invalid",
        "created_by": "manual_observation_entry_helper_v0",
        "errors": errors,
    }


if __name__ == "__main__":
    raise SystemExit(main())
