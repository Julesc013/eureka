"""Validate OBS human review packet artifacts."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]

PACKET_POLICY_PATH = "control/inventory/observations/obs_human_review_packet_policy.json"
TEMPLATE_POLICY_PATH = "control/inventory/observations/obs_review_decision_template_policy.json"
MANIFEST_PATH = "control/inventory/observations/obs_human_review_packet_manifest.json"
AUDIT_REPORT_PATH = "control/audits/obs-agent-07-human-review-packet-v0/obs_agent_07_report.json"
AUDIT_PACKET_JSON_PATH = "control/audits/obs-agent-07-human-review-packet-v0/human_review_packet.json"
AUDIT_PACKET_MD_PATH = "control/audits/obs-agent-07-human-review-packet-v0/human_review_packet.md"
AUDIT_DECISION_TABLE_PATH = "control/audits/obs-agent-07-human-review-packet-v0/candidate_decision_table.md"
AUDIT_SOURCE_POLICY_PATH = "control/audits/obs-agent-07-human-review-packet-v0/source_policy_decision_items.md"
AUDIT_SEARCH_NEED_PATH = "control/audits/obs-agent-07-human-review-packet-v0/search_need_seed_review_items.md"
AUDIT_WORKUNIT_PATH = "control/audits/obs-agent-07-human-review-packet-v0/workunit_seed_review_items.md"
AUDIT_TEMPLATES_PATH = "control/audits/obs-agent-07-human-review-packet-v0/review_decision_templates.md"

REQUIRED_DOCS = (
    "docs/operations/OBS_HUMAN_REVIEW_PACKET.md",
    "docs/operations/OBS_REVIEW_DECISION_GUIDE.md",
    "docs/operations/OBSERVATION_CANDIDATE_REVIEW.md",
    "docs/operations/OBSERVATION_CANDIDATE_REVIEW_QUEUE.md",
    "docs/operations/OBS_CANDIDATE_TO_SEARCH_NEED_SEEDS.md",
    "docs/operations/OBS_CANDIDATE_TO_WORKUNIT_SEEDS.md",
    "docs/operations/OBS_TRACK_B_SYNCHRONIZATION.md",
    "docs/operations/OBS_TO_TRACK_B_HANDOFF_GUIDE.md",
)

EXAMPLE_PATHS = (
    "examples/observation_reviews/human_review_packet_minimal_v0.json",
    "examples/observation_reviews/human_review_decision_approve_source_lead_v0.json",
    "examples/observation_reviews/human_review_decision_request_more_evidence_v0.json",
    "examples/observation_reviews/human_review_decision_mark_policy_blocked_v0.json",
    "examples/observation_reviews/human_review_decision_defer_v0.json",
)

PENDING_BATCH_PATH = "evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json"
SLOT_MANIFEST_PATH = "control/inventory/observations/manual_observation_batch_0_slot_manifest.json"
OBSERVATION_DIRS = (
    "evals/search_usefulness/external_baselines/batches/batch_0/observations",
    "evals/search_usefulness/external_baselines/observations",
)

INPUT_FAMILIES = {
    "observation_candidate",
    "observation_candidate_review_queue",
    "source_gap_candidate",
    "search_need_seed",
    "workunit_seed",
    "obs_track_b_sync_item",
    "source_policy_decision_item",
    "manual_observation_pending_slot",
}
REVIEW_ITEM_TYPES = {
    "candidate_review",
    "source_gap_review",
    "source_policy_decision_preview",
    "search_need_seed_review",
    "workunit_seed_review",
    "manual_observation_selection",
    "blocked_item_review",
    "duplicate_or_defer_review",
    "request_more_evidence_review",
    "track_b_dependency_review",
}
ALLOWED_DECISIONS = {
    "approve_as_source_lead_future",
    "approve_as_search_need_seed_future",
    "approve_as_workunit_seed_future",
    "approve_for_manual_observation_future",
    "request_more_evidence",
    "mark_duplicate",
    "mark_policy_blocked",
    "defer",
    "reject",
    "no_action",
}
ALLOWED_PRIORITY_BANDS = {"high", "medium", "low", "blocked", "insufficient_local_evidence"}

PRODUCT_BOUNDARY_FIELDS = {
    "performed_observations",
    "automated_external_search",
    "scraped_external_systems",
    "crawled_external_systems",
    "called_external_apis",
    "opened_browsers",
    "fabricated_results",
    "marked_pending_as_observed",
    "changed_product_behavior",
    "changed_public_routes",
    "enabled_hosting",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_source_connectors",
    "enabled_downloads",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "mutated_master_index",
    "approved_source_access",
    "executed_workunits",
    "modified_track_b_files",
    "created_runtime_search_needs",
    "created_runtime_workunits",
}

FORBIDDEN_TEXT_MARKERS = (
    "live source observed",
    "external observation performed",
    "google scrape",
    "scraped google result",
    "source access approved",
    "source approval granted",
    "runtime searchneed created",
    "runtime searchneed claim",
    "runtime workunit created",
    "runtime workunit claim",
    "workunit executed",
    "executed workunit",
    "accepted evidence truth",
    "observed-baseline claim",
    "rights clearance confirmed",
    "malware safe",
)

TRACK_B_PREFIXES = (
    "contracts/node/",
    "control/inventory/nodes/",
    "control/audits/track-b-",
    "runtime/",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate OBS human review packet artifacts.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--manifest-file", default=MANIFEST_PATH, help="Packet manifest path relative to repo root.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_obs_human_review_packet(Path(args.repo_root), args.manifest_file)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_obs_human_review_packet(repo_root: Path = REPO_ROOT, manifest_file: str = MANIFEST_PATH) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    packet_policy = _load_json(root / PACKET_POLICY_PATH, errors)
    template_policy = _load_json(root / TEMPLATE_POLICY_PATH, errors)
    manifest = _load_json(root / manifest_file, errors)
    audit_packet = _load_json(root / AUDIT_PACKET_JSON_PATH, errors)
    audit_report = _load_json(root / AUDIT_REPORT_PATH, errors)

    errors.extend(validate_packet_policy_payload(packet_policy, PACKET_POLICY_PATH))
    errors.extend(validate_template_policy_payload(template_policy, TEMPLATE_POLICY_PATH))
    errors.extend(validate_packet_manifest_payload(manifest, manifest_file, root))
    errors.extend(validate_packet_manifest_payload(audit_packet, AUDIT_PACKET_JSON_PATH, root))
    errors.extend(validate_audit_report_payload(audit_report, AUDIT_REPORT_PATH))
    errors.extend(_validate_examples(root))
    errors.extend(_validate_required_docs(root))
    errors.extend(_validate_pending_slots(root))
    errors.extend(_validate_no_observed_files(root))

    return {
        "schema_version": "obs_human_review_packet_validation.v0",
        "status": "valid" if not errors else "invalid",
        "packet_policy_file": PACKET_POLICY_PATH,
        "template_policy_file": TEMPLATE_POLICY_PATH,
        "manifest_file": manifest_file,
        "audit_packet_file": AUDIT_PACKET_JSON_PATH,
        "audit_report_file": AUDIT_REPORT_PATH,
        "example_files": list(EXAMPLE_PATHS),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def validate_packet_policy_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_human_review_packet_policy.v0":
        errors.append(f"{source}: schema_version must be obs_human_review_packet_policy.v0")
    errors.extend(_missing_items(_string_items(data.get("input_artifact_families")), INPUT_FAMILIES, f"{source}: input_artifact_families"))
    errors.extend(_missing_items(_string_items(data.get("review_item_types")), REVIEW_ITEM_TYPES, f"{source}: review_item_types"))
    errors.extend(_missing_items(_string_items(data.get("allowed_decision_options")), ALLOWED_DECISIONS, f"{source}: allowed_decision_options"))
    for effect in (
        "mark_observed_baseline",
        "accept_evidence_truth",
        "approve_source_access",
        "enable_live_probe",
        "create_runtime_search_need",
        "create_runtime_workunit",
        "execute_workunit",
        "mutate_master_index",
        "approve_download_or_execution",
        "claim_rights_clearance",
        "claim_malware_safety",
        "claim_exhaustive_global_search",
    ):
        if effect not in _string_items(data.get("forbidden_decision_effects")):
            errors.append(f"{source}: forbidden_decision_effects missing {effect}")
    truth = _mapping(data.get("truth_boundary"))
    if truth.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required must be true")
    for field in ("review_packet_makes_decisions", "human_decisions_prefilled", "source_access_approved", "accepted_as_observed_baseline", "accepted_as_evidence_truth", "runtime_activation_allowed_now", "creates_runtime_search_need", "creates_runtime_workunit", "executes_workunit", "master_index_mutation_allowed"):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_template_policy_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_review_decision_template_policy.v0":
        errors.append(f"{source}: schema_version must be obs_review_decision_template_policy.v0")
    required_fields = set(_string_items(data.get("required_template_fields")))
    for field in (
        "review_item_id",
        "source_artifact_ref",
        "proposed_decision",
        "human_decision",
        "decision_rationale",
        "confidence",
        "approve_next_action",
        "reject_reason",
        "request_more_evidence_fields",
        "policy_notes",
        "source_policy_decision_required",
        "track_b_dependency",
        "do_not_treat_as_observed_baseline",
        "do_not_treat_as_evidence_truth",
        "do_not_mutate_master_index",
        "reviewer",
        "reviewed_at",
        "notes",
    ):
        if field not in required_fields:
            errors.append(f"{source}: required_template_fields missing {field}")
    defaults = _mapping(data.get("default_template_values"))
    if defaults.get("human_decision") is not None:
        errors.append(f"{source}: default human_decision must be null")
    if defaults.get("reviewer") is not None:
        errors.append(f"{source}: default reviewer must be null")
    if defaults.get("reviewed_at") is not None:
        errors.append(f"{source}: default reviewed_at must be null")
    truth = _mapping(data.get("truth_boundary"))
    for field in ("templates_make_decisions", "real_human_decisions_prefilled", "source_access_approved", "accepted_as_observed_baseline", "accepted_as_evidence_truth", "runtime_activation_allowed_now", "creates_runtime_search_need", "creates_runtime_workunit", "executes_workunit", "master_index_mutation_allowed"):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    return errors


def validate_packet_manifest_payload(payload: Any, source: str, repo_root: Path = REPO_ROOT) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_human_review_packet_manifest.v0":
        errors.append(f"{source}: schema_version must be obs_human_review_packet_manifest.v0")
    items = [_mapping(item) for item in _sequence_items(data.get("review_items"))]
    if data.get("review_item_count") != len(items):
        errors.append(f"{source}: review_item_count must match review_items")
    if data.get("decision_status") != "decision_pending":
        errors.append(f"{source}: decision_status must be decision_pending")
    if data.get("decision_option_counts") != dict(sorted(Counter(str(item.get("recommended_decision")) for item in items).items())):
        errors.append(f"{source}: decision_option_counts must match review_items")
    if data.get("priority_band_counts") != dict(sorted(Counter(str(item.get("priority_band")) for item in items).items())):
        errors.append(f"{source}: priority_band_counts must match review_items")
    if data.get("source_policy_item_count") != sum(1 for item in items if item.get("review_item_type") == "source_policy_decision_preview"):
        errors.append(f"{source}: source_policy_item_count must match review_items")
    if data.get("search_need_seed_item_count") != sum(1 for item in items if item.get("review_item_type") == "search_need_seed_review"):
        errors.append(f"{source}: search_need_seed_item_count must match review_items")
    if data.get("workunit_seed_item_count") != sum(1 for item in items if item.get("review_item_type") == "workunit_seed_review"):
        errors.append(f"{source}: workunit_seed_item_count must match review_items")
    if data.get("track_b_dependency_item_count") != sum(1 for item in items if item.get("review_item_type") == "track_b_dependency_review"):
        errors.append(f"{source}: track_b_dependency_item_count must match review_items")
    truth = _mapping(data.get("truth_boundary"))
    if truth.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required must be true")
    for field in ("review_packet_makes_decisions", "human_decisions_prefilled", "review_items_are_observed_baselines", "review_items_are_evidence_truth", "review_items_create_runtime_search_needs", "review_items_create_runtime_workunits", "review_items_execute_workunits", "review_items_can_mutate_master_index", "source_access_approved"):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    for item in items:
        errors.extend(validate_review_item_payload(item, source, repo_root, allow_synthetic=False))
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def validate_review_item_payload(item: Mapping[str, Any], source: str, repo_root: Path = REPO_ROOT, *, allow_synthetic: bool) -> list[str]:
    errors: list[str] = []
    item_id = str(item.get("review_item_id", "<missing>"))
    for field in (
        "review_item_id",
        "review_item_type",
        "source_artifact_family",
        "source_artifact_ref",
        "source_candidate_or_seed_id",
        "label",
        "summary",
        "recommended_decision",
        "decision_status",
        "priority_band",
        "source_policy_status",
        "track_b_dependency",
        "human_decision",
        "human_review_required",
        "source_access_approved",
        "accepted_as_observed_baseline",
        "accepted_as_evidence_truth",
        "runtime_activation_allowed_now",
        "master_index_mutation_allowed",
        "notes",
    ):
        if field not in item:
            errors.append(f"{source}: {item_id}: missing {field}")
    if item.get("review_item_type") not in REVIEW_ITEM_TYPES:
        errors.append(f"{source}: {item_id}: invalid review_item_type {item.get('review_item_type')!r}")
    if item.get("source_artifact_family") not in INPUT_FAMILIES:
        errors.append(f"{source}: {item_id}: invalid source_artifact_family {item.get('source_artifact_family')!r}")
    if item.get("recommended_decision") not in ALLOWED_DECISIONS:
        errors.append(f"{source}: {item_id}: invalid recommended_decision {item.get('recommended_decision')!r}")
    if item.get("priority_band") not in ALLOWED_PRIORITY_BANDS:
        errors.append(f"{source}: {item_id}: invalid priority_band {item.get('priority_band')!r}")
    if item.get("decision_status") != "decision_pending":
        errors.append(f"{source}: {item_id}: decision_status must be decision_pending")
    if item.get("human_review_required") is not True:
        errors.append(f"{source}: {item_id}: human_review_required must be true")
    if item.get("human_decision") not in (None, "") and not (allow_synthetic and item.get("synthetic_example") is True):
        errors.append(f"{source}: {item_id}: human_decision must be blank")
    for field in ("source_access_approved", "accepted_as_observed_baseline", "accepted_as_evidence_truth", "runtime_activation_allowed_now", "master_index_mutation_allowed"):
        if item.get(field) is not False:
            errors.append(f"{source}: {item_id}: {field} must be false")
    source_ref = item.get("source_artifact_ref")
    if isinstance(source_ref, str) and source_ref and not source_ref.startswith("synthetic/") and not (repo_root / source_ref).exists():
        errors.append(f"{source}: {item_id}: source_artifact_ref missing {source_ref}")
    errors.extend(_forbidden_text_errors(item, f"{source}: {item_id}"))
    return errors


def validate_decision_example_payload(payload: Any, source: str, repo_root: Path = REPO_ROOT) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_human_review_decision_template.v0":
        errors.append(f"{source}: schema_version must be obs_human_review_decision_template.v0")
    if data.get("synthetic_example") is not True:
        errors.append(f"{source}: synthetic examples must set synthetic_example true")
    if data.get("human_decision") not in ALLOWED_DECISIONS:
        errors.append(f"{source}: invalid human_decision {data.get('human_decision')!r}")
    for field in ("source_access_approved", "accepted_as_observed_baseline", "accepted_as_evidence_truth", "runtime_activation_allowed_now", "master_index_mutation_allowed", "creates_runtime_search_need", "creates_runtime_workunit", "executes_workunit"):
        if data.get(field) is not False:
            errors.append(f"{source}: {field} must be false")
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def validate_audit_report_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_agent_07_report.v0":
        errors.append(f"{source}: schema_version must be obs_agent_07_report.v0")
    if data.get("track") != "Observation" or data.get("task") != "OBS-AGENT-07":
        errors.append(f"{source}: track/task mismatch")
    truth = _mapping(data.get("truth_boundary"))
    if truth.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required must be true")
    for field in ("review_packet_makes_decisions", "review_items_are_observed_baselines", "review_items_are_evidence_truth", "review_items_create_runtime_search_needs", "review_items_create_runtime_workunits", "review_items_execute_workunits", "review_items_can_mutate_master_index"):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    for section in ("added_docs", "added_inventories", "added_examples", "added_scripts", "added_tests"):
        for path in _string_items(data.get(section)):
            normalized = path.replace("\\", "/")
            if any(normalized.startswith(prefix) for prefix in TRACK_B_PREFIXES):
                errors.append(f"{source}: {section} contains Track B path {path}")
    return errors


def _validate_examples(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in EXAMPLE_PATHS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"examples: missing {path}")
            continue
        payload = _load_json(full_path, errors)
        if path.endswith("packet_minimal_v0.json"):
            errors.extend(validate_packet_manifest_payload(payload, path, repo_root))
        else:
            errors.extend(validate_decision_example_payload(payload, path, repo_root))
    return errors


def _validate_required_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_DOCS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"docs: missing {path}")
            continue
        if path in {"docs/operations/OBS_HUMAN_REVIEW_PACKET.md", "docs/operations/OBS_REVIEW_DECISION_GUIDE.md"}:
            text = full_path.read_text(encoding="utf-8").lower()
            for phrase in ("review packet", "human review", "track b", "no-goals"):
                if phrase not in text:
                    errors.append(f"{path}: missing phrase {phrase!r}")
    for path in (AUDIT_PACKET_MD_PATH, AUDIT_DECISION_TABLE_PATH, AUDIT_SOURCE_POLICY_PATH, AUDIT_SEARCH_NEED_PATH, AUDIT_WORKUNIT_PATH, AUDIT_TEMPLATES_PATH):
        if not (repo_root / path).is_file():
            errors.append(f"audit: missing {path}")
    return errors


def _validate_pending_slots(repo_root: Path) -> list[str]:
    errors: list[str] = []
    pending = _mapping(_load_json(repo_root / PENDING_BATCH_PATH, errors))
    if pending.get("observation_status") != "pending_manual_observation":
        errors.append(f"{PENDING_BATCH_PATH}: observation_status must remain pending_manual_observation")
    for record in _sequence_items(pending.get("observations")):
        item = _mapping(record)
        observation_id = item.get("observation_id", "<missing>")
        if item.get("observation_status") != "pending_manual_observation":
            errors.append(f"{PENDING_BATCH_PATH}: {observation_id}: observation_status must remain pending_manual_observation")
        if item.get("top_results") != []:
            errors.append(f"{PENDING_BATCH_PATH}: {observation_id}: top_results must remain empty")
    slot_manifest = _mapping(_load_json(repo_root / SLOT_MANIFEST_PATH, errors))
    for slot in _sequence_items(slot_manifest.get("slots")):
        item = _mapping(slot)
        slot_id = item.get("slot_id", "<missing>")
        if item.get("slot_status") != "pending_manual_observation":
            errors.append(f"{SLOT_MANIFEST_PATH}: {slot_id}: slot_status must remain pending_manual_observation")
        if item.get("observed_file_path_if_any") is not None:
            errors.append(f"{SLOT_MANIFEST_PATH}: {slot_id}: observed_file_path_if_any must remain null")
    return errors


def _validate_no_observed_files(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for relative_dir in OBSERVATION_DIRS:
        directory = repo_root / relative_dir
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            name = path.name.lower()
            if name.startswith("observed") or name.startswith("accepted"):
                errors.append(f"{relative_dir}: observed/accepted result file is not allowed: {path.name}")
    return errors


def _boundary_false_errors(boundary: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    for field in sorted(PRODUCT_BOUNDARY_FIELDS):
        if field not in boundary:
            errors.append(f"{source}: product_boundary missing {field}")
        elif boundary[field] is not False:
            errors.append(f"{source}: product_boundary.{field} must be false")
    return errors


def _forbidden_text_errors(payload: Any, source: str) -> list[str]:
    text = json.dumps(payload, sort_keys=True).lower()
    return [f"{source}: forbidden claim marker {marker}" for marker in FORBIDDEN_TEXT_MARKERS if marker in text]


def _missing_items(found_items: Sequence[str], required_items: set[str], source: str) -> list[str]:
    found = set(found_items)
    return [f"{source} missing {item}" for item in sorted(required_items - found)]


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{path.as_posix()}: missing JSON file")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.as_posix()}: invalid JSON at line {exc.lineno}: {exc.msg}")
    return {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence_items(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    return []


def _string_items(value: Any) -> list[str]:
    return [item for item in _sequence_items(value) if isinstance(item, str)]


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"validate_obs_human_review_packet: {report['status']}",
        f"schema_version: {report['schema_version']}",
    ]
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
