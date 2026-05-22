"""Validate SearchNeed seed draft artifacts.

This validator is read-only. It keeps OBS side-lane SearchNeed seed artifacts
as review-gated drafts, not runtime SearchNeeds, observed baselines, evidence
truth, source approval, or master-index mutations.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]

SEED_CONTRACT_PATH = "contracts/query/search_need_seed.v0.json"
CONVERSION_CONTRACT_PATH = "contracts/query/search_need_seed_conversion.v0.json"
POLICY_PATH = "control/inventory/observations/search_need_seed_conversion_policy.json"
PRIORITY_MODEL_PATH = "control/inventory/observations/search_need_seed_priority_model.json"
MANIFEST_PATH = "control/inventory/observations/search_need_seed_manifest.json"
AUDIT_REPORT_PATH = "control/audits/obs-agent-04-candidate-to-search-need-seeds-v0/obs_agent_04_report.json"
AUDIT_MANIFEST_PATH = "control/audits/obs-agent-04-candidate-to-search-need-seeds-v0/search_need_seed_manifest.json"
AUDIT_SUMMARY_PATH = "control/audits/obs-agent-04-candidate-to-search-need-seeds-v0/search_need_seed_summary.md"
AUDIT_REVIEW_PACKET_PATH = "control/audits/obs-agent-04-candidate-to-search-need-seeds-v0/search_need_seed_review_packet.md"
DOC_PATH = "docs/operations/OBS_CANDIDATE_TO_SEARCH_NEED_SEEDS.md"
GUIDE_PATH = "docs/operations/SEARCH_NEED_SEED_REVIEW_GUIDE.md"
PENDING_BATCH_PATH = "evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json"
SLOT_MANIFEST_PATH = "control/inventory/observations/manual_observation_batch_0_slot_manifest.json"
OBSERVATION_DIRS = (
    "evals/search_usefulness/external_baselines/batches/batch_0/observations",
    "evals/search_usefulness/external_baselines/observations",
)

SEED_EXAMPLE_PATHS = (
    "examples/search_need_seeds/minimal_search_need_seed_v0.json",
    "examples/search_need_seeds/source_gap_search_need_seed_v0.json",
    "examples/search_need_seeds/extraction_gap_search_need_seed_v0.json",
    "examples/search_need_seeds/compatibility_gap_search_need_seed_v0.json",
    "examples/search_need_seeds/policy_blocked_search_need_seed_v0.json",
)

CONVERSION_EXAMPLE_PATHS = (
    "examples/search_need_seed_conversions/minimal_candidate_to_need_conversion_v0.json",
    "examples/search_need_seed_conversions/source_gap_candidate_to_need_conversion_v0.json",
    "examples/search_need_seed_conversions/request_more_evidence_conversion_v0.json",
)

REQUIRED_DOCS = (
    DOC_PATH,
    GUIDE_PATH,
    "docs/operations/OBSERVATION_CANDIDATE_REVIEW_QUEUE.md",
    "docs/operations/OBS_CANDIDATE_TRIAGE_GUIDE.md",
    "docs/operations/OBSERVATION_SOURCE_ACCESS_POLICY.md",
    "docs/operations/OBS_PARALLEL_DEVELOPMENT_POLICY.md",
    "docs/operations/MANUAL_OBSERVATION_FAILURE_TAXONOMY.md",
)

ALLOWED_SEED_STATUSES = {
    "proposed",
    "needs_human_review",
    "needs_more_evidence",
    "policy_blocked",
    "duplicate_possible",
    "deferred",
    "ready_for_track_b_after_contracts_future",
    "rejected_future",
    "accepted_runtime_future",
}
CURRENT_FORBIDDEN_SEED_STATUSES = {"accepted_runtime_future"}
ALLOWED_SEED_TYPES = {
    "manual_observation_need_seed",
    "source_gap_need_seed",
    "extraction_gap_need_seed",
    "compatibility_gap_need_seed",
    "ranking_gap_need_seed",
    "policy_blocked_need_seed",
    "evidence_gap_need_seed",
}
ALLOWED_CONVERSION_STATUSES = {
    "proposed",
    "needs_human_review",
    "needs_more_evidence",
    "policy_blocked",
    "deferred",
    "rejected_future",
    "accepted_runtime_future",
}
ALLOWED_CONVERSION_TYPES = {
    "observation_candidate_to_search_need_seed_draft",
    "review_queue_entry_to_search_need_seed_draft",
    "source_gap_candidate_to_search_need_seed_draft",
    "request_more_evidence_only",
    "policy_blocked_candidate_to_search_need_seed_draft",
}
ALLOWED_PRIORITY_BANDS = {
    "high",
    "medium",
    "low",
    "blocked",
    "insufficient_local_evidence",
}
ALLOWED_SOURCE_ACCESS_MODES = {
    "repo_local_only",
    "manual_human_only",
    "permission_needed",
    "no_autonomous_access",
    "approved_api_future",
    "approved_metadata_probe_future",
    "approved_static_dump_future",
    "restricted_demand_signal_only",
    "approved_fixture_only",
}
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
}
EXTRA_FALSE_BOUNDARY_FIELDS = {
    "approved_source_access",
    "modified_track_b_files",
    "accepted_runtime_search_need",
}
TRACK_B_PREFIXES = (
    "contracts/source_registry/",
    "contracts/workunit/",
    "contracts/node/",
    "contracts/local/",
    "runtime/",
    "control/audits/track-b-",
    "docs/reference/EUREKA_NODE",
    "docs/reference/WORKUNIT",
    "docs/reference/LOCAL_FOUNDRY",
)
FORBIDDEN_TEXT_MARKERS = (
    "scraped google result",
    "google " + "scrape",
    "scrape_google",
    "forum scrape",
    "reddit thread contents",
    "live source observed",
    "external observation performed",
    "accepted evidence truth",
    "accepted-public-truth",
    "accepted runtime searchneed",
    "accepted runtime search need",
    "accepted-runtime-need",
    "source access approved",
    "approved source access",
    "source sync enabled",
    "provider call completed",
    "model call completed",
    "browser opened",
    "rights clearance confirmed",
    "malware safe",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate SearchNeed seed draft artifacts.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--manifest-file", default=MANIFEST_PATH, help="Seed manifest JSON path relative to repo root.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_search_need_seed_candidates(Path(args.repo_root), args.manifest_file)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_search_need_seed_candidates(
    repo_root: Path = REPO_ROOT,
    manifest_file: str = MANIFEST_PATH,
) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    seed_contract = _load_json(root / SEED_CONTRACT_PATH, errors)
    conversion_contract = _load_json(root / CONVERSION_CONTRACT_PATH, errors)
    policy = _load_json(root / POLICY_PATH, errors)
    priority_model = _load_json(root / PRIORITY_MODEL_PATH, errors)
    manifest = _load_json(root / manifest_file, errors)
    audit_manifest = _load_json(root / AUDIT_MANIFEST_PATH, errors)
    audit_report = _load_json(root / AUDIT_REPORT_PATH, errors)

    errors.extend(validate_seed_contract_payload(seed_contract, SEED_CONTRACT_PATH))
    errors.extend(validate_conversion_contract_payload(conversion_contract, CONVERSION_CONTRACT_PATH))
    errors.extend(validate_policy_payload(policy, POLICY_PATH))
    errors.extend(validate_priority_model_payload(priority_model, PRIORITY_MODEL_PATH))
    errors.extend(validate_manifest_payload(manifest, manifest_file, root))
    errors.extend(validate_manifest_payload(audit_manifest, AUDIT_MANIFEST_PATH, root))
    errors.extend(validate_audit_report_payload(audit_report, AUDIT_REPORT_PATH))
    errors.extend(_validate_examples(root))
    errors.extend(_validate_docs(root))
    errors.extend(_validate_pending_slots(root))
    errors.extend(_validate_no_observed_files(root))

    return {
        "schema_version": "search_need_seed_validation.v0",
        "status": "valid" if not errors else "invalid",
        "seed_contract_file": SEED_CONTRACT_PATH,
        "conversion_contract_file": CONVERSION_CONTRACT_PATH,
        "policy_file": POLICY_PATH,
        "priority_model_file": PRIORITY_MODEL_PATH,
        "manifest_file": manifest_file,
        "audit_manifest_file": AUDIT_MANIFEST_PATH,
        "audit_report_file": AUDIT_REPORT_PATH,
        "seed_example_files": list(SEED_EXAMPLE_PATHS),
        "conversion_example_files": list(CONVERSION_EXAMPLE_PATHS),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def validate_seed_contract_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("title") != "EurekaSearchNeedSeedV0":
        errors.append(f"{source}: title must be EurekaSearchNeedSeedV0")
    required = set(_string_items(data.get("required")))
    for field in ("schema_version", "search_need_seed_id", "seed_status", "seed_type", "review_required", "accepted_as_runtime_search_need", "product_boundary"):
        if field not in required:
            errors.append(f"{source}: required missing {field}")
    for field in ("x-runtime-search-need-created", "x-observed-baseline-created", "x-evidence-truth-created", "x-source-access-approved", "x-master-index-mutation-allowed"):
        if data.get(field) is not False:
            errors.append(f"{source}: {field} must be false")
    return errors


def validate_conversion_contract_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("title") != "EurekaSearchNeedSeedConversionV0":
        errors.append(f"{source}: title must be EurekaSearchNeedSeedConversionV0")
    required = set(_string_items(data.get("required")))
    for field in ("schema_version", "conversion_id", "conversion_status", "review_required", "accepted_as_runtime_search_need", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if field not in required:
            errors.append(f"{source}: required missing {field}")
    for field in ("x-runtime-search-need-created", "x-evidence-truth-created", "x-source-access-approved", "x-master-index-mutation-allowed"):
        if data.get(field) is not False:
            errors.append(f"{source}: {field} must be false")
    return errors


def validate_policy_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "search_need_seed_conversion_policy.v0":
        errors.append(f"{source}: schema_version must be search_need_seed_conversion_policy.v0")
    errors.extend(_missing_items(_string_items(data.get("allowed_seed_statuses")), ALLOWED_SEED_STATUSES, f"{source}: allowed_seed_statuses"))
    errors.extend(_missing_items(_string_items(data.get("allowed_seed_types")), ALLOWED_SEED_TYPES, f"{source}: allowed_seed_types"))
    for field in ("accepted_as_runtime_search_need", "accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed", "source_access_approved", "performed_external_observation"):
        if field not in _string_items(data.get("required_false_truth_boundary_fields")):
            errors.append(f"{source}: required_false_truth_boundary_fields missing {field}")
    for conversion in (
        "candidate_to_accepted_runtime_need",
        "candidate_to_observed_baseline",
        "candidate_to_evidence_truth",
        "source_lead_to_source_approval",
        "demand_signal_to_object_truth",
        "ai_summary_to_need_truth",
        "policy_blocked_candidate_to_runtime_need_without_review",
        "master_index_mutation",
    ):
        if conversion not in _string_items(data.get("forbidden_conversions")):
            errors.append(f"{source}: forbidden_conversions missing {conversion}")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source, include_extra=True))
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def validate_priority_model_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "search_need_seed_priority_model.v0":
        errors.append(f"{source}: schema_version must be search_need_seed_priority_model.v0")
    score_fields = _mapping(data.get("score_fields"))
    if score_fields.get("minimum") != 0 or score_fields.get("maximum") != 100:
        errors.append(f"{source}: score_fields must be bounded 0..100")
    interpretation = _mapping(data.get("output_interpretation"))
    if interpretation.get("advisory_only") is not True:
        errors.append(f"{source}: output_interpretation.advisory_only must be true")
    for field in ("approves_or_accepts_seeds", "creates_runtime_search_needs", "creates_observed_baselines", "creates_evidence_truth", "approves_source_access", "mutates_master_index"):
        if interpretation.get(field) is not False:
            errors.append(f"{source}: output_interpretation.{field} must be false")
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def validate_manifest_payload(payload: Any, source: str, repo_root: Path = REPO_ROOT) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "search_need_seed_manifest.v0":
        errors.append(f"{source}: schema_version must be search_need_seed_manifest.v0")
    records = [_mapping(item) for item in _sequence_items(data.get("seed_records"))]
    if data.get("seed_count") != len(records):
        errors.append(f"{source}: seed_count must match seed_records")
    if data.get("review_required") is not True:
        errors.append(f"{source}: review_required must be true")
    errors.extend(_truth_boundary_errors(_mapping(data.get("truth_boundary")), source))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source, include_extra=True))
    if data.get("seed_status_counts") != dict(sorted(Counter(str(record.get("seed_status")) for record in records).items())):
        errors.append(f"{source}: seed_status_counts must match seed_records")
    if data.get("seed_type_counts") != dict(sorted(Counter(str(record.get("seed_type")) for record in records).items())):
        errors.append(f"{source}: seed_type_counts must match seed_records")
    if data.get("priority_band_counts") != dict(sorted(Counter(_priority_band(record.get("proposed_priority")) for record in records).items())):
        errors.append(f"{source}: priority_band_counts must match seed_records")
    expected_candidates = Counter(
        candidate_id
        for record in records
        for candidate_id in _string_items(record.get("related_observation_candidate_ids"))
    )
    if data.get("related_candidate_counts") != dict(sorted(expected_candidates.items())):
        errors.append(f"{source}: related_candidate_counts must match seed_records")
    errors.extend(_priority_summary_errors(_mapping(data.get("priority_score_summary")), records, source))
    for record in records:
        errors.extend(validate_manifest_record(record, source, repo_root))
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def validate_manifest_record(record: Mapping[str, Any], source: str, repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    seed_id = str(record.get("search_need_seed_id", "<missing>"))
    for field in (
        "search_need_seed_id",
        "seed_status",
        "seed_type",
        "related_observation_candidate_ids",
        "related_review_queue_entry_ids",
        "related_query_ids",
        "canonical_need_label",
        "proposed_priority",
        "proposed_review_action",
        "seed_file_path",
        "review_required",
        "accepted_as_runtime_search_need",
        "accepted_as_observed_baseline",
        "accepted_as_evidence_truth",
        "master_index_mutation_allowed",
        "notes",
    ):
        if field not in record:
            errors.append(f"{source}: {seed_id}: missing {field}")
    errors.extend(_status_type_priority_errors(record, source, seed_id))
    if record.get("review_required") is not True:
        errors.append(f"{source}: {seed_id}: review_required must be true")
    for field in ("accepted_as_runtime_search_need", "accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if record.get(field) is not False:
            errors.append(f"{source}: {seed_id}: {field} must be false")
    seed_path = record.get("seed_file_path")
    if isinstance(seed_path, str):
        full_path = repo_root / seed_path
        if not full_path.is_file():
            errors.append(f"{source}: {seed_id}: seed_file_path missing {seed_path}")
        else:
            seed_payload = _load_json(full_path, errors)
            errors.extend(validate_seed_payload(seed_payload, seed_path, repo_root))
    errors.extend(_forbidden_text_errors(record, f"{source}: {seed_id}"))
    return errors


def validate_seed_payload(payload: Any, source: str, repo_root: Path = REPO_ROOT) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    seed_id = str(data.get("search_need_seed_id", "<missing>"))
    for field in (
        "schema_version",
        "search_need_seed_id",
        "seed_status",
        "seed_type",
        "seed_origin",
        "seed_origin_ref",
        "related_observation_candidate_ids",
        "related_review_queue_entry_ids",
        "canonical_need_label",
        "desired_user_action",
        "failure_mode_summary",
        "evidence_or_observation_limitations",
        "proposed_priority",
        "required_review_state",
        "downstream_track_b_dependency",
        "review_required",
        "accepted_as_runtime_search_need",
        "accepted_as_observed_baseline",
        "accepted_as_evidence_truth",
        "master_index_mutation_allowed",
        "product_boundary",
        "no_goals",
        "notes",
    ):
        if field not in data:
            errors.append(f"{source}: {seed_id}: missing {field}")
    if data.get("schema_version") != "search_need_seed.v0":
        errors.append(f"{source}: schema_version must be search_need_seed.v0")
    errors.extend(_status_type_priority_errors(data, source, seed_id))
    if data.get("review_required") is not True:
        errors.append(f"{source}: {seed_id}: review_required must be true")
    for field in ("accepted_as_runtime_search_need", "accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if data.get(field) is not False:
            errors.append(f"{source}: {seed_id}: {field} must be false")
    if "review" not in str(data.get("required_review_state", "")).lower():
        errors.append(f"{source}: {seed_id}: required_review_state must require review")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source, include_extra=True))
    mode = data.get("source_access_mode")
    policy_status = str(data.get("source_policy_status", "")).lower()
    if mode is not None:
        if mode not in ALLOWED_SOURCE_ACCESS_MODES:
            errors.append(f"{source}: {seed_id}: invalid source_access_mode {mode!r}")
        if mode in {"approved_api_future", "approved_metadata_probe_future", "approved_static_dump_future"}:
            if not any(marker in policy_status for marker in ("future", "deferred", "required")):
                errors.append(f"{source}: {seed_id}: future source mode must remain future/deferred or policy-required")
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def validate_conversion_payload(payload: Any, source: str, repo_root: Path = REPO_ROOT) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    conversion_id = str(data.get("conversion_id", "<missing>"))
    for field in (
        "schema_version",
        "conversion_id",
        "conversion_status",
        "conversion_type",
        "source_candidate_ref",
        "source_review_queue_entry_ref",
        "produced_seed_ref",
        "conversion_rules_applied",
        "fields_mapped",
        "fields_unmapped",
        "missing_evidence",
        "review_required",
        "conversion_limitations",
        "rejected_conversion_reason",
        "downstream_dependencies",
        "accepted_as_runtime_search_need",
        "accepted_as_evidence_truth",
        "master_index_mutation_allowed",
        "notes",
    ):
        if field not in data:
            errors.append(f"{source}: {conversion_id}: missing {field}")
    if data.get("schema_version") != "search_need_seed_conversion.v0":
        errors.append(f"{source}: schema_version must be search_need_seed_conversion.v0")
    status = data.get("conversion_status")
    if status not in ALLOWED_CONVERSION_STATUSES:
        errors.append(f"{source}: {conversion_id}: invalid conversion_status {status!r}")
    if status == "accepted_runtime_future":
        errors.append(f"{source}: {conversion_id}: current conversion_status cannot be accepted_runtime_future")
    if data.get("conversion_type") not in ALLOWED_CONVERSION_TYPES:
        errors.append(f"{source}: {conversion_id}: invalid conversion_type {data.get('conversion_type')!r}")
    if data.get("review_required") is not True:
        errors.append(f"{source}: {conversion_id}: review_required must be true")
    for field in ("accepted_as_runtime_search_need", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if data.get(field) is not False:
            errors.append(f"{source}: {conversion_id}: {field} must be false")
    if "source_policy_decision_id" in _mapping(data.get("fields_mapped")):
        errors.append(f"{source}: {conversion_id}: source_policy_decision_id must not be mapped by OBS-04")
    if "runtime_search_need_id" in _mapping(data.get("fields_mapped")):
        errors.append(f"{source}: {conversion_id}: runtime_search_need_id must not be mapped by OBS-04")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source, include_extra=True))
    seed_ref = _mapping(data.get("produced_seed_ref")).get("seed_file_path")
    if isinstance(seed_ref, str) and (repo_root / seed_ref).is_file():
        errors.extend(validate_seed_payload(_load_json(repo_root / seed_ref, errors), seed_ref, repo_root))
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def validate_audit_report_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_agent_04_report.v0":
        errors.append(f"{source}: schema_version must be obs_agent_04_report.v0")
    if data.get("track") != "Observation":
        errors.append(f"{source}: track must be Observation")
    if data.get("task") != "OBS-AGENT-04":
        errors.append(f"{source}: task must be OBS-AGENT-04")
    truth = _mapping(data.get("truth_boundary"))
    if truth.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required must be true")
    for field in ("seeds_are_runtime_search_needs", "seeds_are_observed_baselines", "seeds_are_evidence_truth", "seeds_can_mutate_master_index"):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source, include_extra=True))
    for section in ("added_contracts", "added_docs", "added_inventories", "added_examples", "added_scripts", "added_tests"):
        for path in _string_items(data.get(section)):
            normalized = path.replace("\\", "/")
            if any(normalized.startswith(prefix) for prefix in TRACK_B_PREFIXES):
                errors.append(f"{source}: {section} contains Track B path {path}")
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def _validate_examples(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in SEED_EXAMPLE_PATHS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"examples: missing {path}")
            continue
        errors.extend(validate_seed_payload(_load_json(full_path, errors), path, repo_root))
    for path in CONVERSION_EXAMPLE_PATHS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"examples: missing {path}")
            continue
        errors.extend(validate_conversion_payload(_load_json(full_path, errors), path, repo_root))
    return errors


def _validate_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_DOCS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"docs: missing {path}")
            continue
        if path in {DOC_PATH, GUIDE_PATH}:
            text = full_path.read_text(encoding="utf-8").lower()
            for phrase in ("searchneed seed", "not a runtime searchneed", "repo-local", "track b", "human review"):
                if phrase not in text:
                    errors.append(f"{path}: missing phrase {phrase!r}")
    for path in (AUDIT_SUMMARY_PATH, AUDIT_REVIEW_PACKET_PATH):
        if not (repo_root / path).is_file():
            errors.append(f"docs: missing {path}")
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
        for field in ("operator", "observed_at", "exact_query_submitted", "first_useful_result_rank", "usefulness_scores"):
            if item.get(field) is not None:
                errors.append(f"{PENDING_BATCH_PATH}: {observation_id}: {field} must remain null")
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


def _status_type_priority_errors(record: Mapping[str, Any], source: str, item_id: str) -> list[str]:
    errors: list[str] = []
    status = record.get("seed_status")
    if status not in ALLOWED_SEED_STATUSES:
        errors.append(f"{source}: {item_id}: invalid seed_status {status!r}")
    if status in CURRENT_FORBIDDEN_SEED_STATUSES:
        errors.append(f"{source}: {item_id}: current seed_status cannot be {status}")
    if record.get("seed_type") not in ALLOWED_SEED_TYPES:
        errors.append(f"{source}: {item_id}: invalid seed_type {record.get('seed_type')!r}")
    priority = _mapping(record.get("proposed_priority"))
    score = priority.get("score")
    if not isinstance(score, int) or score < 0 or score > 100:
        errors.append(f"{source}: {item_id}: proposed_priority.score must be an integer from 0 to 100")
    if priority.get("band") not in ALLOWED_PRIORITY_BANDS:
        errors.append(f"{source}: {item_id}: invalid proposed_priority.band {priority.get('band')!r}")
    return errors


def _truth_boundary_errors(boundary: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    if boundary.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required must be true")
    for field in ("seeds_are_runtime_search_needs", "seeds_are_observed_baselines", "seeds_are_evidence_truth", "seeds_can_mutate_master_index", "source_access_approved"):
        if boundary.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    return errors


def _boundary_false_errors(boundary: Mapping[str, Any], source: str, *, include_extra: bool) -> list[str]:
    errors: list[str] = []
    fields = set(PRODUCT_BOUNDARY_FIELDS)
    if include_extra:
        fields.update(EXTRA_FALSE_BOUNDARY_FIELDS)
    for field in sorted(fields):
        if field not in boundary:
            errors.append(f"{source}: product_boundary missing {field}")
        elif boundary[field] is not False:
            errors.append(f"{source}: product_boundary.{field} must be false")
    return errors


def _priority_summary_errors(summary: Mapping[str, Any], records: Sequence[Mapping[str, Any]], source: str) -> list[str]:
    scores = [_priority_score(record.get("proposed_priority")) for record in records]
    expected = {"min": 0, "max": 0, "average": 0} if not scores else {
        "min": min(scores),
        "max": max(scores),
        "average": round(sum(scores) / len(scores), 2),
    }
    return [f"{source}: priority_score_summary must match seed record priority scores"] if summary != expected else []


def _priority_score(priority: Any) -> int:
    value = _mapping(priority).get("score")
    return int(value) if isinstance(value, int) else 0


def _priority_band(priority: Any) -> str:
    value = _mapping(priority).get("band")
    return str(value) if isinstance(value, str) else "insufficient_local_evidence"


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
        f"validate_search_need_seed_candidates: {report['status']}",
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
