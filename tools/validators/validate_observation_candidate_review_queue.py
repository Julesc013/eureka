"""Validate ObservationCandidate review queue artifacts.

This validator is read-only. It ensures review queue entries remain queued
governance records, not approvals, observed baselines, evidence truth, source
approval, or master-index mutations.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_observation_candidate import validate_candidate_record  # noqa: E402


CONTRACT_PATH = "contracts/schema/control/tasks/query/observation_candidate_review_queue.v0.json"
POLICY_PATH = "control/inventory/observations/observation_candidate_review_queue_policy.json"
TRIAGE_RULES_PATH = "control/inventory/observations/observation_candidate_triage_rules.json"
QUEUE_PATH = "control/inventory/observations/observation_candidate_review_queue.json"
AUDIT_REPORT_PATH = "control/audits/obs-agent-03-observation-candidate-review-queue-v0/obs_agent_03_report.json"
AUDIT_QUEUE_PATH = "control/audits/obs-agent-03-observation-candidate-review-queue-v0/observation_candidate_review_queue.json"
AUDIT_QUEUE_MD_PATH = "control/audits/obs-agent-03-observation-candidate-review-queue-v0/observation_candidate_review_queue.md"
AUDIT_TRIAGE_MD_PATH = "control/audits/obs-agent-03-observation-candidate-review-queue-v0/candidate_triage_summary.md"
DOC_PATH = "docs/operations/OBSERVATION_CANDIDATE_REVIEW_QUEUE.md"
TRIAGE_GUIDE_PATH = "docs/operations/OBS_CANDIDATE_TRIAGE_GUIDE.md"
PENDING_BATCH_PATH = "evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json"
SLOT_MANIFEST_PATH = "control/inventory/observations/manual_observation_batch_0_slot_manifest.json"
OBSERVATION_DIRS = (
    "evals/search_usefulness/external_baselines/batches/batch_0/observations",
    "evals/search_usefulness/external_baselines/observations",
)

EXAMPLE_PATHS = (
    "examples/review/observation_reviews/review_queue_minimal_v0.json",
    "examples/review/observation_reviews/review_queue_source_gap_batch_v0.json",
    "examples/review/observation_reviews/review_queue_policy_blocked_batch_v0.json",
    "examples/review/observation_reviews/review_queue_request_more_evidence_batch_v0.json",
)

REQUIRED_DOCS = (
    DOC_PATH,
    TRIAGE_GUIDE_PATH,
    "docs/operations/AGENT_ASSISTED_OBSERVATION_WORKFLOW.md",
    "docs/operations/OBSERVATION_CANDIDATE_REVIEW.md",
    "docs/operations/OBSERVATION_SOURCE_ACCESS_POLICY.md",
    "docs/operations/OBS_PARALLEL_DEVELOPMENT_POLICY.md",
    "docs/operations/OBS_AGENT_LOCAL_EVAL_FAILURE_MINING.md",
    "docs/operations/OBS_AGENT_SOURCE_GAP_CANDIDATES.md",
    "docs/operations/MANUAL_OBSERVATION_FAILURE_TAXONOMY.md",
)

ALLOWED_REVIEW_STATES = {
    "queued_for_review",
    "needs_human_review",
    "needs_more_evidence",
    "policy_blocked",
    "duplicate_possible",
    "deferred",
    "ready_for_human_decision",
}
ALLOWED_RECOMMENDED_ACTIONS = {
    "approve_as_source_lead_future",
    "approve_as_workunit_seed_future",
    "approve_as_search_need_seed_future",
    "approve_for_manual_observation_future",
    "reject_future",
    "mark_duplicate_future",
    "mark_policy_blocked_future",
    "request_more_evidence_future",
    "defer_future",
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
EXTRA_FALSE_BOUNDARY_FIELDS = {"approved_source_access", "modified_track_b_files"}
TRACK_B_PREFIXES = (
    "contracts/source/registry/",
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
    "observed-baseline claim",
    "source access approved",
    "source sync enabled",
    "provider call completed",
    "model call completed",
    "browser opened",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate observation candidate review queue artifacts.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--queue-file", default=QUEUE_PATH, help="Queue JSON path relative to repo root.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_observation_candidate_review_queue(Path(args.repo_root), args.queue_file)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_observation_candidate_review_queue(
    repo_root: Path = REPO_ROOT,
    queue_file: str = QUEUE_PATH,
) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    contract = _load_json(root / CONTRACT_PATH, errors)
    policy = _load_json(root / POLICY_PATH, errors)
    triage_rules = _load_json(root / TRIAGE_RULES_PATH, errors)
    queue = _load_json(root / queue_file, errors)
    audit_queue = _load_json(root / AUDIT_QUEUE_PATH, errors)
    audit_report = _load_json(root / AUDIT_REPORT_PATH, errors)

    errors.extend(validate_contract_payload(contract, CONTRACT_PATH))
    errors.extend(validate_policy_payload(policy, POLICY_PATH))
    errors.extend(validate_triage_rules_payload(triage_rules, TRIAGE_RULES_PATH))
    errors.extend(validate_queue_payload(queue, queue_file, root))
    errors.extend(validate_queue_payload(audit_queue, AUDIT_QUEUE_PATH, root))
    errors.extend(validate_audit_report_payload(audit_report, AUDIT_REPORT_PATH))
    errors.extend(_validate_examples(root))
    errors.extend(_validate_docs(root))
    errors.extend(_validate_pending_slots(root))
    errors.extend(_validate_no_observed_files(root))

    return {
        "schema_version": "observation_candidate_review_queue_validation.v0",
        "status": "valid" if not errors else "invalid",
        "contract_file": CONTRACT_PATH,
        "policy_file": POLICY_PATH,
        "triage_rules_file": TRIAGE_RULES_PATH,
        "queue_file": queue_file,
        "audit_queue_file": AUDIT_QUEUE_PATH,
        "audit_report_file": AUDIT_REPORT_PATH,
        "example_files": list(EXAMPLE_PATHS),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def validate_contract_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("title") != "EurekaObservationCandidateReviewQueueV0":
        errors.append(f"{source}: title must be EurekaObservationCandidateReviewQueueV0")
    required = set(_string_items(data.get("required")))
    for field in ("schema_version", "review_queue_id", "queue_entries", "truth_boundary", "product_boundary"):
        if field not in required:
            errors.append(f"{source}: required missing {field}")
    if data.get("x-master-index-mutation-allowed") is not False:
        errors.append(f"{source}: x-master-index-mutation-allowed must be false")
    if data.get("x-source-access-approved") is not False:
        errors.append(f"{source}: x-source-access-approved must be false")
    return errors


def validate_policy_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "observation_candidate_review_queue_policy.v0":
        errors.append(f"{source}: schema_version must be observation_candidate_review_queue_policy.v0")
    errors.extend(_missing_items(_string_items(data.get("allowed_review_states")), ALLOWED_REVIEW_STATES, f"{source}: allowed_review_states"))
    errors.extend(_missing_items(_string_items(data.get("allowed_recommended_actions")), ALLOWED_RECOMMENDED_ACTIONS, f"{source}: allowed_recommended_actions"))
    errors.extend(_missing_items(_string_items(data.get("allowed_priority_bands")), ALLOWED_PRIORITY_BANDS, f"{source}: allowed_priority_bands"))
    for field in ("accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed", "source_access_approved", "performed_external_observation"):
        if field not in _string_items(data.get("required_false_truth_boundary_fields")):
            errors.append(f"{source}: required_false_truth_boundary_fields missing {field}")
    for action in ("approve_candidate_now", "convert_to_evidence_truth", "mutate_master_index", "approve_source_access"):
        if action not in _string_items(data.get("forbidden_auto_actions")):
            errors.append(f"{source}: forbidden_auto_actions missing {action}")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source, include_extra=True))
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def validate_triage_rules_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "observation_candidate_triage_rules.v0":
        errors.append(f"{source}: schema_version must be observation_candidate_triage_rules.v0")
    bands = _mapping(data.get("priority_bands"))
    for band in ALLOWED_PRIORITY_BANDS:
        if band not in bands:
            errors.append(f"{source}: priority_bands missing {band}")
    if data.get("advisory_only") is not True:
        errors.append(f"{source}: advisory_only must be true")
    for field in ("approves_source_access", "creates_evidence_truth", "creates_observed_baseline", "mutates_master_index"):
        if data.get(field) is not False:
            errors.append(f"{source}: {field} must be false")
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def validate_queue_payload(payload: Any, source: str, repo_root: Path = REPO_ROOT) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "observation_candidate_review_queue.v0":
        errors.append(f"{source}: schema_version must be observation_candidate_review_queue.v0")
    if data.get("queue_status") not in {"queued_for_review", "no_generated_candidates_available"}:
        errors.append(f"{source}: invalid queue_status {data.get('queue_status')!r}")
    entries = [_mapping(item) for item in _sequence_items(data.get("queue_entries"))]
    if data.get("queue_status") == "queued_for_review" and not entries:
        errors.append(f"{source}: queued_for_review requires queue entries")
    errors.extend(_truth_boundary_errors(_mapping(data.get("truth_boundary")), source))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source, include_extra=True))

    if data.get("status_counts") != dict(sorted(Counter(str(entry.get("proposed_review_state")) for entry in entries).items())):
        errors.append(f"{source}: status_counts must match queue_entries")
    if data.get("recommended_action_counts") != dict(sorted(Counter(str(entry.get("recommended_review_action")) for entry in entries).items())):
        errors.append(f"{source}: recommended_action_counts must match queue_entries")
    if data.get("candidate_type_counts") != dict(sorted(Counter(str(entry.get("candidate_type")) for entry in entries).items())):
        errors.append(f"{source}: candidate_type_counts must match queue_entries")
    if data.get("source_family_counts") != dict(sorted(Counter(str(entry.get("source_family")) for entry in entries).items())):
        errors.append(f"{source}: source_family_counts must match queue_entries")
    if data.get("priority_band_counts") != dict(sorted(Counter(str(entry.get("priority_band")) for entry in entries).items())):
        errors.append(f"{source}: priority_band_counts must match queue_entries")
    errors.extend(_priority_summary_errors(_mapping(data.get("priority_summary")), entries, source))

    for entry in entries:
        errors.extend(validate_queue_entry(entry, source, repo_root))
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def validate_queue_entry(entry: Mapping[str, Any], source: str, repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    entry_id = str(entry.get("review_queue_entry_id", "<missing>"))
    for field in (
        "review_queue_entry_id",
        "observation_candidate_id",
        "candidate_file_path",
        "candidate_type",
        "candidate_status",
        "candidate_origin",
        "source_family",
        "source_access_mode",
        "proposed_failure_modes",
        "proposed_review_state",
        "recommended_review_action",
        "priority_score",
        "priority_band",
        "review_required",
        "review_decision_ref",
        "notes",
    ):
        if field not in entry:
            errors.append(f"{source}: {entry_id}: missing {field}")
    if entry.get("review_required") is not True:
        errors.append(f"{source}: {entry_id}: review_required must be true")
    for field in ("accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if entry.get(field) is not False:
            errors.append(f"{source}: {entry_id}: {field} must be false")
    if entry.get("review_decision_ref") is not None:
        errors.append(f"{source}: {entry_id}: review_decision_ref must be null")
    if entry.get("proposed_review_state") not in ALLOWED_REVIEW_STATES:
        errors.append(f"{source}: {entry_id}: invalid proposed_review_state {entry.get('proposed_review_state')!r}")
    action = entry.get("recommended_review_action")
    if action not in ALLOWED_RECOMMENDED_ACTIONS:
        errors.append(f"{source}: {entry_id}: invalid recommended_review_action {action!r}")
    elif not str(action).endswith("_future"):
        errors.append(f"{source}: {entry_id}: recommended_review_action must be future-only")
    if entry.get("priority_band") not in ALLOWED_PRIORITY_BANDS:
        errors.append(f"{source}: {entry_id}: invalid priority_band {entry.get('priority_band')!r}")
    score = entry.get("priority_score")
    if not isinstance(score, int) or score < 0 or score > 100:
        errors.append(f"{source}: {entry_id}: priority_score must be an integer from 0 to 100")
    mode = entry.get("source_access_mode")
    policy_status = str(entry.get("source_policy_status", "")).lower()
    if mode not in ALLOWED_SOURCE_ACCESS_MODES:
        errors.append(f"{source}: {entry_id}: invalid source_access_mode {mode!r}")
    if mode in {"approved_api_future", "approved_metadata_probe_future", "approved_static_dump_future"}:
        if not any(marker in policy_status for marker in ("future", "deferred", "required")):
            errors.append(f"{source}: {entry_id}: future source access mode must remain future/deferred or policy-required")
    candidate_path = entry.get("candidate_file_path")
    if isinstance(candidate_path, str):
        full_path = repo_root / candidate_path
        if not full_path.is_file():
            errors.append(f"{source}: {entry_id}: candidate_file_path missing {candidate_path}")
        else:
            candidate_payload = _load_json(full_path, errors)
            errors.extend(validate_candidate_record(candidate_payload, candidate_path))
    errors.extend(_forbidden_text_errors(entry, f"{source}: {entry_id}"))
    return errors


def validate_audit_report_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_agent_03_report.v0":
        errors.append(f"{source}: schema_version must be obs_agent_03_report.v0")
    if data.get("track") != "Observation":
        errors.append(f"{source}: track must be Observation")
    if data.get("task") != "OBS-AGENT-03":
        errors.append(f"{source}: task must be OBS-AGENT-03")
    truth = _mapping(data.get("truth_boundary"))
    if truth.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required must be true")
    for field in ("queue_entries_are_observed_baselines", "queue_entries_are_evidence_truth", "queue_entries_can_mutate_master_index"):
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
    for path in EXAMPLE_PATHS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"examples: missing {path}")
            continue
        errors.extend(validate_queue_payload(_load_json(full_path, errors), path, repo_root))
    return errors


def _validate_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_DOCS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"docs: missing {path}")
            continue
        text = full_path.read_text(encoding="utf-8").lower()
        if path in {DOC_PATH, TRIAGE_GUIDE_PATH}:
            for phrase in ("review queue", "not approval", "repo-local", "track b"):
                if phrase not in text:
                    errors.append(f"{path}: missing phrase {phrase!r}")
    for path in (AUDIT_QUEUE_MD_PATH, AUDIT_TRIAGE_MD_PATH):
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


def _truth_boundary_errors(boundary: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    if boundary.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required must be true")
    for field in ("queue_entries_are_observed_baselines", "queue_entries_are_evidence_truth", "queue_entries_can_mutate_master_index", "source_access_approved"):
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


def _priority_summary_errors(summary: Mapping[str, Any], entries: Sequence[Mapping[str, Any]], source: str) -> list[str]:
    scores = [entry.get("priority_score") for entry in entries if isinstance(entry.get("priority_score"), int)]
    expected = {"min": 0, "max": 0, "average": 0} if not scores else {
        "min": min(scores),
        "max": max(scores),
        "average": round(sum(scores) / len(scores), 2),
    }
    return [f"{source}: priority_summary must match queue entry priority scores"] if summary != expected else []


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
        f"validate_observation_candidate_review_queue: {report['status']}",
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
