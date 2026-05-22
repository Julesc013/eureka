"""Build a deterministic OBS human review packet.

The packet is a decision aid. It reads repo-local OBS artifacts and leaves every
human decision blank. It does not approve candidates, approve source access,
create runtime records, execute WorkUnits, or mutate Track B files.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]

PACKET_POLICY_PATH = "control/inventory/observations/obs_human_review_packet_policy.json"
TEMPLATE_POLICY_PATH = "control/inventory/observations/obs_review_decision_template_policy.json"
REVIEW_QUEUE_PATH = "control/inventory/observations/observation_candidate_review_queue.json"
SEARCH_NEED_MANIFEST_PATH = "control/inventory/observations/search_need_seed_manifest.json"
WORKUNIT_MANIFEST_PATH = "control/inventory/observations/workunit_seed_manifest.json"
SYNC_MATRIX_PATH = "control/inventory/observations/obs_track_b_sync_matrix.json"
READINESS_PATH = "control/inventory/observations/obs_track_b_handoff_readiness.json"

OBS_AUDIT_INPUTS = (
    "control/audits/obs-agent-01-local-eval-failure-mining-v0/local_eval_candidate_manifest.json",
    "control/audits/obs-agent-02-source-gap-candidate-generation-v0/source_gap_candidate_manifest.json",
    "control/audits/obs-agent-03-observation-candidate-review-queue-v0/observation_candidate_review_queue.json",
    "control/audits/obs-agent-04-candidate-to-search-need-seeds-v0/search_need_seed_manifest.json",
    "control/audits/obs-agent-05-candidate-to-workunit-seeds-v0/workunit_seed_manifest.json",
    "control/audits/obs-agent-06-obs-track-b-synchronization-v0/obs_track_b_sync_matrix.json",
)

PRIMARY_INPUT_PATHS = (
    PACKET_POLICY_PATH,
    TEMPLATE_POLICY_PATH,
    REVIEW_QUEUE_PATH,
    SEARCH_NEED_MANIFEST_PATH,
    WORKUNIT_MANIFEST_PATH,
    SYNC_MATRIX_PATH,
    READINESS_PATH,
    *OBS_AUDIT_INPUTS,
)

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
    "enabled_hosting": False,
    "enabled_live_probes": False,
    "enabled_source_sync": False,
    "enabled_source_connectors": False,
    "enabled_downloads": False,
    "enabled_uploads": False,
    "enabled_accounts": False,
    "enabled_telemetry": False,
    "mutated_master_index": False,
    "approved_source_access": False,
    "executed_workunits": False,
    "modified_track_b_files": False,
    "created_runtime_search_needs": False,
    "created_runtime_workunits": False,
}

PRIORITY_BAND_RANK = {
    "high": 0,
    "medium": 1,
    "low": 2,
    "blocked": 3,
    "insufficient_local_evidence": 4,
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build OBS human review packet without making decisions.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--list-inputs", action="store_true", help="List deterministic repo-local inputs and exit.")
    parser.add_argument("--check", action="store_true", help="Validate that the review packet can be safely built.")
    parser.add_argument("--json-output", help="Explicit path for generated packet JSON.")
    parser.add_argument("--markdown-output", help="Explicit path for generated packet Markdown.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    output = stdout or sys.stdout

    if args.list_inputs:
        for path in list_input_paths(root):
            output.write(f"{path}\n")
        return 0

    manifest = build_review_packet(root)
    errors = validate_built_packet(manifest)

    if args.check:
        if errors:
            output.write("build_obs_human_review_packet: fail\n")
            for error in errors:
                output.write(f"- {error}\n")
            return 1
        output.write("build_obs_human_review_packet: pass\n")
        output.write(f"review_item_count: {manifest['review_item_count']}\n")

    if args.json_output:
        _write_text(root, args.json_output, json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    if args.markdown_output:
        _write_text(root, args.markdown_output, format_markdown_packet(manifest))

    if not args.check and not args.json_output and not args.markdown_output:
        output.write(format_plain_summary(manifest))
    return 0 if not errors else 1


def list_input_paths(repo_root: Path = REPO_ROOT) -> list[str]:
    return sorted(path for path in PRIMARY_INPUT_PATHS if (repo_root / path).exists())


def build_review_packet(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    queue = _load_json(root / REVIEW_QUEUE_PATH)
    search_need_manifest = _load_json(root / SEARCH_NEED_MANIFEST_PATH)
    workunit_manifest = _load_json(root / WORKUNIT_MANIFEST_PATH)
    sync_matrix = _load_json(root / SYNC_MATRIX_PATH)
    readiness = _load_json(root / READINESS_PATH)

    review_items = []
    review_items.extend(_candidate_items(queue))
    review_items.extend(_search_need_items(search_need_manifest))
    review_items.extend(_workunit_items(workunit_manifest))
    review_items.extend(_source_policy_items(sync_matrix))
    review_items.extend(_track_b_dependency_items(sync_matrix))
    review_items = sorted(
        review_items,
        key=lambda item: (
            PRIORITY_BAND_RANK.get(str(item.get("priority_band")), 99),
            str(item.get("review_item_type")),
            str(item.get("review_item_id")),
        ),
    )

    decision_counts = Counter(str(item.get("recommended_decision")) for item in review_items)
    priority_counts = Counter(str(item.get("priority_band")) for item in review_items)

    return {
        "schema_version": "obs_human_review_packet_manifest.v0",
        "manifest_id": "obs_human_review_packet_manifest_v0",
        "label": "OBS human review packet manifest",
        "description": "Decision-pending packet for OBS candidates, SearchNeed seeds, WorkUnit seeds, source-policy items, and OBS/Track B synchronization state.",
        "generated_from": list_input_paths(root),
        "review_item_count": len(review_items),
        "review_items": review_items,
        "decision_option_counts": dict(sorted(decision_counts.items())),
        "priority_band_counts": dict(sorted(priority_counts.items())),
        "source_policy_item_count": sum(1 for item in review_items if item.get("review_item_type") == "source_policy_decision_preview"),
        "search_need_seed_item_count": sum(1 for item in review_items if item.get("review_item_type") == "search_need_seed_review"),
        "workunit_seed_item_count": sum(1 for item in review_items if item.get("review_item_type") == "workunit_seed_review"),
        "blocked_item_count": sum(1 for item in review_items if item.get("priority_band") == "blocked" or item.get("recommended_decision") == "mark_policy_blocked"),
        "track_b_dependency_item_count": sum(1 for item in review_items if item.get("review_item_type") == "track_b_dependency_review"),
        "decision_status": "decision_pending",
        "readiness": {
            "ready_for_parallel_continuation": readiness.get("ready_for_parallel_continuation"),
            "ready_for_runtime_consumption": readiness.get("ready_for_runtime_consumption"),
            "ready_for_source_policy_decision": readiness.get("ready_for_source_policy_decision"),
            "ready_for_workunit_runtime": readiness.get("ready_for_workunit_runtime"),
            "ready_for_public_index_effect": readiness.get("ready_for_public_index_effect"),
        },
        "truth_boundary": {
            "review_packet_makes_decisions": False,
            "human_decisions_prefilled": False,
            "review_items_are_observed_baselines": False,
            "review_items_are_evidence_truth": False,
            "review_items_create_runtime_search_needs": False,
            "review_items_create_runtime_workunits": False,
            "review_items_execute_workunits": False,
            "review_items_can_mutate_master_index": False,
            "source_access_approved": False,
            "human_review_required": True,
        },
        "product_boundary": dict(PRODUCT_BOUNDARY),
        "notes": [
            "This packet is a decision aid only.",
            "human_decision is null on every real review item.",
            "Approving an item does not create observed baseline evidence, evidence truth, source approval, runtime records, WorkUnit execution, public truth, or master-index mutation."
        ]
    }


def validate_built_packet(packet: Mapping[str, Any]) -> list[str]:
    errors = []
    items = [_mapping(item) for item in _sequence_items(packet.get("review_items"))]
    if packet.get("schema_version") != "obs_human_review_packet_manifest.v0":
        errors.append("schema_version must be obs_human_review_packet_manifest.v0")
    if packet.get("review_item_count") != len(items):
        errors.append("review_item_count must match review_items")
    for item in items:
        item_id = str(item.get("review_item_id", "<missing>"))
        if item.get("human_review_required") is not True:
            errors.append(f"{item_id}: human_review_required must be true")
        if item.get("human_decision") not in (None, ""):
            errors.append(f"{item_id}: human_decision must be blank")
        for field in ("source_access_approved", "accepted_as_observed_baseline", "accepted_as_evidence_truth", "runtime_activation_allowed_now", "master_index_mutation_allowed"):
            if item.get(field) is not False:
                errors.append(f"{item_id}: {field} must be false")
    return sorted(set(errors))


def format_plain_summary(packet: Mapping[str, Any]) -> str:
    lines = [
        "build_obs_human_review_packet:",
        f"- review_item_count: {packet.get('review_item_count')}",
        f"- decision_option_counts: {json.dumps(packet.get('decision_option_counts', {}), sort_keys=True)}",
        f"- priority_band_counts: {json.dumps(packet.get('priority_band_counts', {}), sort_keys=True)}",
    ]
    return "\n".join(lines) + "\n"


def format_markdown_packet(packet: Mapping[str, Any]) -> str:
    items = [_mapping(item) for item in _sequence_items(packet.get("review_items"))]
    lines = [
        "# OBS Human Review Packet",
        "",
        "Use this packet to decide what should happen next. It is not a decision record.",
        "",
        "Approving an item does not make it an observed baseline.",
        "Approving an item does not make it accepted evidence truth.",
        "Approving an item does not approve live source access.",
        "Approving an item does not create runtime SearchNeeds.",
        "Approving an item does not create executable WorkUnits.",
        "Approving an item does not mutate the master index.",
        "",
        "## Summary",
        "",
        f"- Review items: {packet.get('review_item_count')}",
        f"- Source policy items: {packet.get('source_policy_item_count')}",
        f"- SearchNeed seed items: {packet.get('search_need_seed_item_count')}",
        f"- WorkUnit seed items: {packet.get('workunit_seed_item_count')}",
        f"- Blocked items: {packet.get('blocked_item_count')}",
        f"- Track B dependency items: {packet.get('track_b_dependency_item_count')}",
        "",
        "## Decision Table",
        "",
        "| Priority | Item | Type | Recommended decision | Policy | Track B dependency | Human decision |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |  |".format(
                item.get("priority_band"),
                item.get("review_item_id"),
                item.get("review_item_type"),
                item.get("recommended_decision"),
                item.get("source_policy_status"),
                item.get("track_b_dependency"),
            )
        )
    lines.extend(
        [
            "",
            "## Next Safe Action",
            "",
            "- A human reviewer fills decision fields outside this generated packet.",
            "- Keep source-policy items blocked until explicit source policy review.",
            "- Keep SearchNeed and WorkUnit seeds draft-only until Track B accepts a future conversion path.",
            "",
        ]
    )
    return "\n".join(lines)


def _candidate_items(queue: Mapping[str, Any]) -> list[dict[str, Any]]:
    items = []
    for entry in _sequence_items(queue.get("queue_entries")):
        data = _mapping(entry)
        candidate_id = str(data.get("observation_candidate_id"))
        decision = _normalize_decision(data.get("recommended_review_action"))
        review_type = _candidate_review_type(data, decision)
        items.append(_review_item(
            review_item_id=f"review_item::{candidate_id}",
            review_item_type=review_type,
            source_family="observation_candidate",
            source_ref=str(data.get("candidate_file_path")),
            source_id=candidate_id,
            label=candidate_id,
            summary=f"{data.get('candidate_type')} from {data.get('candidate_origin')}",
            recommended_decision=decision,
            priority_band=str(data.get("priority_band", "medium")),
            source_policy_status=str(data.get("source_policy_status", "not_external")),
            track_b_dependency="human_review_queue",
            notes=_string_items(data.get("notes")),
        ))
    return items


def _search_need_items(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    items = []
    for record in _sequence_items(manifest.get("seed_records")):
        data = _mapping(record)
        seed_id = str(data.get("search_need_seed_id"))
        priority = _mapping(data.get("proposed_priority"))
        items.append(_review_item(
            review_item_id=f"review_item::{seed_id}",
            review_item_type="search_need_seed_review",
            source_family="search_need_seed",
            source_ref=str(data.get("seed_file_path")),
            source_id=seed_id,
            label=str(data.get("canonical_need_label", seed_id)),
            summary=f"{data.get('seed_type')} requires review before future Track B conversion.",
            recommended_decision=_normalize_decision(data.get("proposed_review_action")),
            priority_band=str(priority.get("band", "medium")),
            source_policy_status=str(data.get("source_policy_status", "not_external")),
            track_b_dependency="future_track_b_search_need_runtime",
            notes=_string_items(data.get("notes")),
        ))
    return items


def _workunit_items(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    items = []
    for record in _sequence_items(manifest.get("seed_records")):
        data = _mapping(record)
        seed_id = str(data.get("workunit_seed_id"))
        priority = _mapping(data.get("proposed_priority"))
        items.append(_review_item(
            review_item_id=f"review_item::{seed_id}",
            review_item_type="workunit_seed_review",
            source_family="workunit_seed",
            source_ref=str(data.get("seed_file_path")),
            source_id=seed_id,
            label=str(data.get("proposed_workunit_label", seed_id)),
            summary=f"{data.get('seed_type')} remains non-executable and review-gated.",
            recommended_decision=_normalize_decision(data.get("proposed_review_action")),
            priority_band=str(priority.get("band", "medium")),
            source_policy_status=str(data.get("source_policy_status", "not_external")),
            track_b_dependency="future_track_b_workunit_runtime",
            notes=_string_items(data.get("notes")),
        ))
    return items


def _source_policy_items(matrix: Mapping[str, Any]) -> list[dict[str, Any]]:
    mappings = [_mapping(item) for item in _sequence_items(matrix.get("mappings"))]
    source_policy_ids = set(_string_items(matrix.get("source_policy_items")))
    items = []
    for mapping in mappings:
        mapping_id = str(mapping.get("mapping_id"))
        if mapping_id not in source_policy_ids:
            continue
        decision = "mark_policy_blocked" if mapping.get("current_handoff_state") == "blocked_by_policy" else "request_more_evidence"
        items.append(_review_item(
            review_item_id=f"review_item::{mapping_id}",
            review_item_type="source_policy_decision_preview",
            source_family="source_policy_decision_item",
            source_ref=str(mapping.get("obs_artifact_ref")),
            source_id=mapping_id,
            label=mapping_id,
            summary=str(mapping.get("required_next_action")),
            recommended_decision=decision,
            priority_band="blocked",
            source_policy_status="source_policy_review_required",
            track_b_dependency=str(mapping.get("track_b_artifact_family")),
            notes=_string_items(mapping.get("notes")),
        ))
    return items


def _track_b_dependency_items(matrix: Mapping[str, Any]) -> list[dict[str, Any]]:
    items = []
    for mapping in _sequence_items(matrix.get("mappings")):
        data = _mapping(mapping)
        if data.get("source_policy_approval_required") is True:
            continue
        mapping_id = str(data.get("mapping_id"))
        items.append(_review_item(
            review_item_id=f"review_item::{mapping_id}",
            review_item_type="track_b_dependency_review",
            source_family="obs_track_b_sync_item",
            source_ref=str(data.get("obs_artifact_ref")),
            source_id=mapping_id,
            label=mapping_id,
            summary=str(data.get("required_next_action")),
            recommended_decision="no_action",
            priority_band="medium" if str(data.get("current_handoff_state", "")).startswith("ready_") else "blocked",
            source_policy_status="not_external",
            track_b_dependency=str(data.get("track_b_artifact_family")),
            notes=_string_items(data.get("notes")),
        ))
    return items


def _review_item(
    *,
    review_item_id: str,
    review_item_type: str,
    source_family: str,
    source_ref: str,
    source_id: str,
    label: str,
    summary: str,
    recommended_decision: str,
    priority_band: str,
    source_policy_status: str,
    track_b_dependency: str,
    notes: Sequence[str],
) -> dict[str, Any]:
    return {
        "review_item_id": review_item_id,
        "review_item_type": review_item_type,
        "source_artifact_family": source_family,
        "source_artifact_ref": source_ref,
        "source_candidate_or_seed_id": source_id,
        "label": label,
        "summary": summary,
        "recommended_decision": recommended_decision,
        "decision_status": "decision_pending",
        "priority_band": priority_band,
        "source_policy_status": source_policy_status,
        "track_b_dependency": track_b_dependency,
        "human_decision": None,
        "human_review_required": True,
        "source_access_approved": False,
        "accepted_as_observed_baseline": False,
        "accepted_as_evidence_truth": False,
        "runtime_activation_allowed_now": False,
        "master_index_mutation_allowed": False,
        "notes": list(notes),
    }


def _candidate_review_type(entry: Mapping[str, Any], decision: str) -> str:
    if decision == "mark_policy_blocked" or entry.get("priority_band") == "blocked":
        return "blocked_item_review"
    if decision == "request_more_evidence":
        return "request_more_evidence_review"
    if decision == "approve_for_manual_observation_future":
        return "manual_observation_selection"
    if entry.get("candidate_type") == "source_lead":
        return "source_gap_review"
    return "candidate_review"


def _normalize_decision(value: Any) -> str:
    text = str(value or "no_action")
    mapping = {
        "request_more_evidence_future": "request_more_evidence",
        "mark_policy_blocked_future": "mark_policy_blocked",
        "mark_duplicate_future": "mark_duplicate",
        "defer_future": "defer",
        "reject_future": "reject",
    }
    return mapping.get(text, text)


def _write_text(repo_root: Path, output_arg: str, text: str) -> None:
    output_path = Path(output_arg)
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, Mapping) else {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence_items(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    return []


def _string_items(value: Any) -> list[str]:
    return [item for item in _sequence_items(value) if isinstance(item, str)]


if __name__ == "__main__":
    raise SystemExit(main())
