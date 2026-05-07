"""Prepare Batch 0 manual observation execution state without observing it.

This script only reads existing Batch 0 files and writes explicit manifests
when requested. It does not open browsers, fetch URLs, call APIs, or convert a
pending slot into observed evidence.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_ROOT = "evals/search_usefulness/external_baselines/batches/batch_0"
BATCH_MANIFEST = f"{BATCH_ROOT}/batch_manifest.json"
BATCH_PENDING = f"{BATCH_ROOT}/observations/pending_batch_0_observations.json"
OBSERVED_FILE_PREFIXES = ("observed_", "completed_")

PRODUCT_BOUNDARY = {
    "performed_observations": False,
    "automated_external_search": False,
    "scraped_external_systems": False,
    "crawled_external_systems": False,
    "called_external_apis": False,
    "opened_browsers": False,
    "fabricated_results": False,
    "marked_pending_as_observed": False,
    "changed_product_behavior": False,
    "changed_public_routes": False,
    "changed_generated_site_artifacts": False,
    "enabled_hosting": False,
    "enabled_live_probes": False,
    "enabled_source_sync": False,
    "enabled_source_connectors": False,
    "enabled_downloads": False,
    "enabled_uploads": False,
    "enabled_accounts": False,
    "enabled_telemetry": False,
    "mutated_master_index": False,
}

REQUIRED_FIELDS_ON_COMPLETION = [
    "operator",
    "observed_at",
    "browser_or_tool",
    "exact_query_submitted",
    "filters_or_scope",
    "top_results",
    "first_useful_result_rank",
    "usefulness_scores",
    "evidence_limitations",
    "staleness_notes",
]

ALLOWED_MANUAL_ACTIONS = [
    "select_pending_slot",
    "manually_open_named_external_system",
    "manually_enter_query",
    "manually_record_timestamp",
    "manually_copy_visible_title",
    "manually_copy_visible_locator",
    "manually_record_short_public_safe_snippet_or_summary",
    "manually_record_rank",
    "manually_record_no_result_outcome",
    "manually_record_near_match",
    "manually_classify_failure",
    "run_local_validation",
]

FORBIDDEN_AUTOMATION = [
    "browser_opening_by_script",
    "browser_automation",
    "automated_external_search",
    "scraping",
    "crawling",
    "url_fetching_by_script",
    "external_api_call",
    "model_or_provider_call",
    "source_connector_runtime",
    "live_probe_runtime",
]

COMPLETION_STATES = [
    "pending_manual_observation",
    "pending_stub",
    "observed",
    "blocked",
    "not_applicable",
]


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare Manual Observation Batch 0 execution manifests without observing slots."
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--batch-root", default=BATCH_ROOT, help="Batch root path relative to repo root.")
    parser.add_argument("--json-output", help="Explicit path for the generated slot manifest JSON.")
    parser.add_argument("--markdown-output", help="Explicit path for a readiness Markdown summary.")
    parser.add_argument("--check", action="store_true", help="Fail if Batch 0 is not execution-ready.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    repo_root = Path(args.repo_root).resolve()
    manifest = build_slot_manifest(repo_root=repo_root, batch_root=args.batch_root)
    output = stdout or sys.stdout

    if args.json_output:
        _write_json(repo_root / args.json_output, manifest)
    if args.markdown_output:
        _write_text(repo_root / args.markdown_output, format_readiness_markdown(manifest))

    output.write(format_summary(manifest))
    return 0 if not args.check or manifest["validation_status"] == "ready_for_manual_execution" else 1


def build_slot_manifest(*, repo_root: Path = REPO_ROOT, batch_root: str = BATCH_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    batch_root_path = root / batch_root
    manifest_path = batch_root_path / "batch_manifest.json"
    pending_path = batch_root_path / "observations" / "pending_batch_0_observations.json"

    errors: list[str] = []
    batch_manifest = _load_json(manifest_path, errors)
    pending_payload = _load_json(pending_path, errors)

    manifest_data = _mapping(batch_manifest)
    pending_data = _mapping(pending_payload)
    batch_id = _string(manifest_data.get("batch_id")) or "batch_0"
    selected_query_ids = _string_list(manifest_data.get("selected_query_ids"))
    selected_system_ids = _string_list(manifest_data.get("selected_system_ids"))
    expected_count = manifest_data.get("expected_observation_count")
    expected_from_grid = len(selected_query_ids) * len(selected_system_ids)
    if expected_count != expected_from_grid:
        errors.append(f"{_rel(manifest_path, root)}: expected_observation_count does not match query/system grid")

    records = pending_data.get("observations")
    if not isinstance(records, list):
        records = []
        errors.append(f"{_rel(pending_path, root)}: observations must be a list")

    by_slot: dict[tuple[str, str], Mapping[str, Any]] = {}
    duplicate_keys: list[str] = []
    for record in records:
        item = _mapping(record)
        key = (_string(item.get("query_id")), _string(item.get("system_id")))
        if key in by_slot:
            duplicate_keys.append("::".join(key))
        by_slot[key] = item
    if duplicate_keys:
        errors.append(f"{_rel(pending_path, root)}: duplicate slots {sorted(duplicate_keys)}")

    observed_file_index = _observed_file_index(batch_root_path)
    slots: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    priority = 1
    for query_id in selected_query_ids:
        for system_id in selected_system_ids:
            record = by_slot.get((query_id, system_id), {})
            status = _string(record.get("observation_status")) or "missing_pending_slot"
            status_counts[status] += 1
            if status != "pending_manual_observation":
                errors.append(f"{query_id}::{system_id}: slot must remain pending for OBS0-02")
            if record.get("top_results") not in ([], None):
                errors.append(f"{query_id}::{system_id}: pending slot must not contain top_results")
            if record.get("observed_at") is not None:
                errors.append(f"{query_id}::{system_id}: pending slot observed_at must remain null")
            observed_path = observed_file_index.get((_string(record.get("query_id")), _string(record.get("system_id"))))
            slots.append(
                {
                    "slot_id": _string(record.get("observation_id")) or f"{batch_id}::{query_id}::{system_id}",
                    "query_id": query_id,
                    "system_id": system_id,
                    "query_text": _string(record.get("query_text")),
                    "slot_status": status,
                    "pending_file_path": _rel(pending_path, root),
                    "observed_file_path_if_any": observed_path,
                    "required_fields_status": "pending_observation_fields_not_collected",
                    "required_fields_on_completion": list(REQUIRED_FIELDS_ON_COMPLETION),
                    "assigned_to": None,
                    "priority": priority,
                    "notes": [
                        "Pending manual observation.",
                        "Do not mark observed unless the human observation was actually performed.",
                    ],
                }
            )
            priority += 1

    discovered_count = len(slots)
    if discovered_count != expected_from_grid:
        errors.append(f"{batch_id}: discovered {discovered_count} slots, expected {expected_from_grid}")

    validation_status = "ready_for_manual_execution" if not errors and status_counts == Counter({"pending_manual_observation": expected_from_grid}) else "not_ready"
    return {
        "schema_version": "manual_observation_batch_0_slot_manifest.v0",
        "manifest_id": "manual_observation_batch_0_slot_manifest_v0",
        "batch_id": batch_id,
        "source_batch_root": batch_root,
        "generated_from": [
            _rel(manifest_path, root),
            _rel(pending_path, root),
        ],
        "slot_count": discovered_count,
        "slots": slots,
        "status_counts": dict(sorted(status_counts.items())),
        "systems": list(selected_system_ids),
        "query_ids": list(selected_query_ids),
        "validation_status": validation_status,
        "errors": sorted(errors),
        "product_boundary": dict(PRODUCT_BOUNDARY),
        "notes": [
            "This manifest prepares human execution only.",
            "It does not create observed result files.",
            "It does not perform external observations.",
        ],
    }


def format_summary(manifest: Mapping[str, Any]) -> str:
    lines = [
        "prepare_manual_observation_batch0_execution:",
        f"- batch_id: {manifest.get('batch_id')}",
        f"- slot_count: {manifest.get('slot_count')}",
        f"- validation_status: {manifest.get('validation_status')}",
        f"- status_counts: {json.dumps(manifest.get('status_counts', {}), sort_keys=True)}",
    ]
    if manifest.get("errors"):
        lines.append("- errors:")
        lines.extend(f"  - {error}" for error in manifest["errors"])
    return "\n".join(lines) + "\n"


def format_readiness_markdown(manifest: Mapping[str, Any]) -> str:
    status_counts = _mapping(manifest.get("status_counts"))
    lines = [
        "# Batch 0 Execution Readiness",
        "",
        f"- Batch: `{manifest.get('batch_id')}`",
        f"- Readiness: `{manifest.get('validation_status')}`",
        f"- Slots: `{manifest.get('slot_count')}`",
        f"- Pending slots: `{status_counts.get('pending_manual_observation', 0)}`",
        "- Observed slots created by this task: `0`",
        "",
        "Human next step: choose one pending slot, perform the observation manually, and record the required fields.",
        "",
        "Do not mark observed unless the human observation was actually performed.",
        "Do not use browser automation, API calls, scraping, crawling, model summaries, or memory as observation evidence.",
        "",
        "Validation commands:",
        "",
        "```powershell",
        "python scripts/prepare_manual_observation_batch0_execution.py --check",
        "python scripts/validate_manual_observation_batch0_execution.py",
        "python scripts/validate_manual_observation_protocol.py",
        "```",
    ]
    return "\n".join(lines) + "\n"


def _observed_file_index(batch_root_path: Path) -> dict[tuple[str, str], str]:
    index: dict[tuple[str, str], str] = {}
    observations_dir = batch_root_path / "observations"
    if not observations_dir.is_dir():
        return index
    for path in sorted(observations_dir.glob("*.json")):
        if path.name.startswith("pending_"):
            continue
        if not path.name.startswith(OBSERVED_FILE_PREFIXES):
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        records = payload.get("observations", [payload]) if isinstance(payload, Mapping) else []
        if not isinstance(records, list):
            continue
        for record in records:
            item = _mapping(record)
            if item.get("observation_status") == "observed":
                key = (_string(item.get("query_id")), _string(item.get("system_id")))
                index[key] = _rel(path, REPO_ROOT)
    return index


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, REPO_ROOT)}: missing JSON file")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path, REPO_ROOT)}: invalid JSON at line {exc.lineno}: {exc.msg}")
    return None


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
