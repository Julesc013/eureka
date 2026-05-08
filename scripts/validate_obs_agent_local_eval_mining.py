"""Validate OBS-AGENT-01 local eval failure mining artifacts.

This validator is read-only. It verifies that generated candidates remain
review-gated planning records and that the OBS lane did not claim external
observation, accepted evidence, or product behavior changes.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_observation_candidate import validate_candidate_record  # noqa: E402


POLICY_PATH = "control/inventory/observations/obs_agent_local_eval_failure_mining_policy.json"
INVENTORY_MANIFEST_PATH = "control/inventory/observations/obs_agent_candidate_batch_0_local_eval_manifest.json"
AUDIT_REPORT_PATH = "control/audits/obs-agent-01-local-eval-failure-mining-v0/obs_agent_01_report.json"
AUDIT_MANIFEST_PATH = "control/audits/obs-agent-01-local-eval-failure-mining-v0/local_eval_candidate_manifest.json"
AUDIT_SUMMARY_PATH = "control/audits/obs-agent-01-local-eval-failure-mining-v0/local_eval_candidate_summary.md"
DOC_PATH = "docs/operations/OBS_AGENT_LOCAL_EVAL_FAILURE_MINING.md"
PENDING_BATCH_PATH = "evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json"
SLOT_MANIFEST_PATH = "control/inventory/observations/manual_observation_batch_0_slot_manifest.json"
OBSERVATION_DIRS = (
    "evals/search_usefulness/external_baselines/batches/batch_0/observations",
    "evals/search_usefulness/external_baselines/observations",
)

EXAMPLE_PATHS = (
    "examples/observation_candidates/local_eval_failure_mining_batch_0_v0.json",
    "examples/observation_candidates/local_eval_source_gap_candidate_v0.json",
    "examples/observation_candidates/local_eval_extraction_gap_candidate_v0.json",
    "examples/observation_candidates/local_eval_ranking_gap_candidate_v0.json",
    "examples/observation_candidates/local_eval_policy_blocked_candidate_v0.json",
)

REQUIRED_DOCS = (
    DOC_PATH,
    "docs/operations/AGENT_ASSISTED_OBSERVATION_WORKFLOW.md",
    "docs/operations/OBSERVATION_CANDIDATE_REVIEW.md",
    "docs/operations/OBSERVATION_SOURCE_ACCESS_POLICY.md",
    "docs/operations/OBS_PARALLEL_DEVELOPMENT_POLICY.md",
    "docs/operations/MANUAL_OBSERVATION_FAILURE_TAXONOMY.md",
)

REQUIRED_ALLOWED_ROOTS = {
    "evals/search_usefulness/**",
    "examples/**",
    "control/audits/**",
    "control/inventory/observations/**",
    "site/dist/data/**",
    "site/dist/demo/**",
    "docs/operations/**",
    "docs/reference/**",
}

REQUIRED_FORBIDDEN_ROOTS = {
    "live web",
    "browser sessions",
    "API calls",
    "downloaded binary archives",
    "private local caches",
    ".aide.local/**",
    "secrets/**",
    ".git/**",
    "untracked external data",
}

REQUIRED_FAILURE_MODES = {
    "source_coverage_gap",
    "compatibility_evidence_gap",
    "decomposition_gap",
    "member_access_gap",
    "extraction_gap",
    "ranking_gap",
    "rights_or_policy_block",
    "insufficient_local_evidence",
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

LOCAL_ONLY_SOURCE_MODES = {"repo_local_only", "no_autonomous_access"}
TRACK_B_PREFIXES = (
    "contracts/",
    "runtime/",
    "control/audits/track-b-",
    "docs/reference/EUREKA_NODE",
    "docs/reference/NODE_",
    "docs/reference/WORKUNIT",
    "docs/reference/LOCAL_FOUNDRY",
)

FORBIDDEN_TEXT_MARKERS = (
    "scraped google result",
    "google scrape",
    "scrape_google",
    "live source observed",
    "external observation performed",
    "accepted evidence truth",
    "accepted-public-truth",
    "observed-baseline claim",
    "provider call completed",
    "model call completed",
    "browser opened",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate OBS local eval failure mining artifacts.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--manifest-file", default=INVENTORY_MANIFEST_PATH, help="Candidate batch manifest to validate.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_obs_agent_local_eval_mining(Path(args.repo_root), args.manifest_file)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_obs_agent_local_eval_mining(
    repo_root: Path = REPO_ROOT,
    manifest_file: str = INVENTORY_MANIFEST_PATH,
) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    policy = _load_json(root / POLICY_PATH, errors)
    manifest = _load_json(root / manifest_file, errors)
    audit_manifest = _load_json(root / AUDIT_MANIFEST_PATH, errors)
    audit_report = _load_json(root / AUDIT_REPORT_PATH, errors)

    errors.extend(_validate_docs(root))
    errors.extend(validate_policy_payload(policy, POLICY_PATH))
    errors.extend(validate_manifest_payload(manifest, manifest_file, root))
    errors.extend(validate_manifest_payload(audit_manifest, AUDIT_MANIFEST_PATH, root))
    errors.extend(validate_audit_report_payload(audit_report, AUDIT_REPORT_PATH))
    errors.extend(_validate_examples(root))
    errors.extend(_validate_pending_slots(root))
    errors.extend(_validate_no_observed_files(root))

    return {
        "schema_version": "obs_agent_local_eval_mining_validation.v0",
        "status": "valid" if not errors else "invalid",
        "policy_file": POLICY_PATH,
        "manifest_file": manifest_file,
        "audit_manifest_file": AUDIT_MANIFEST_PATH,
        "audit_report_file": AUDIT_REPORT_PATH,
        "example_files": list(EXAMPLE_PATHS),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def validate_policy_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_agent_local_eval_failure_mining_policy.v0":
        errors.append(f"{source}: schema_version must be obs_agent_local_eval_failure_mining_policy.v0")
    if data.get("review_required") is not True:
        errors.append(f"{source}: review_required must be true")
    for field in ("accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if data.get(field) is not False:
            errors.append(f"{source}: {field} must be false")
    errors.extend(_missing_items(_string_items(data.get("allowed_input_roots")), REQUIRED_ALLOWED_ROOTS, f"{source}: allowed_input_roots"))
    errors.extend(_missing_items(_string_items(data.get("forbidden_input_roots")), REQUIRED_FORBIDDEN_ROOTS, f"{source}: forbidden_input_roots"))
    errors.extend(_missing_items(_string_items(data.get("allowed_failure_modes")), REQUIRED_FAILURE_MODES, f"{source}: allowed_failure_modes"))
    source_policy = _mapping(data.get("source_access_policy"))
    for field in ("external_access_authorized", "live_source_access_authorized", "external_observation_authorized"):
        if source_policy.get(field) is not False:
            errors.append(f"{source}: source_access_policy.{field} must be false")
    truth = _mapping(data.get("truth_boundary"))
    if truth.get("human_review_required_before_downstream_use") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required_before_downstream_use must be true")
    for field in ("candidates_are_observed_baselines", "candidates_are_evidence_truth", "candidates_validate_sources", "candidates_can_mutate_index"):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source, include_track_b=True))
    return errors


def validate_manifest_payload(payload: Any, source: str, repo_root: Path = REPO_ROOT) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_agent_candidate_batch_local_eval_manifest.v0":
        errors.append(f"{source}: schema_version must be obs_agent_candidate_batch_local_eval_manifest.v0")
    records = [_mapping(item) for item in _sequence_items(data.get("candidate_records"))]
    if data.get("candidate_count") != len(records):
        errors.append(f"{source}: candidate_count must match candidate_records length")
    if data.get("review_required") is not True:
        errors.append(f"{source}: review_required must be true")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source, include_track_b=True))
    truth = _mapping(data.get("truth_boundary"))
    if truth.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required must be true")
    for field in ("candidates_are_observed_baselines", "candidates_are_evidence_truth", "candidates_can_mutate_master_index"):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")

    status_counts = Counter(str(record.get("candidate_status")) for record in records)
    if data.get("status_counts") != dict(sorted(status_counts.items())):
        errors.append(f"{source}: status_counts must match candidate_records")
    mode_counts = Counter(mode for record in records for mode in _string_items(record.get("proposed_failure_modes")))
    if data.get("failure_mode_counts") != dict(sorted(mode_counts.items())):
        errors.append(f"{source}: failure_mode_counts must match candidate_records")

    for record in records:
        errors.extend(validate_manifest_record(record, source))
        candidate_path = record.get("candidate_file_path")
        if isinstance(candidate_path, str) and candidate_path:
            candidate_file = repo_root / candidate_path
            if candidate_file.is_file():
                errors.extend(validate_candidate_payload(_load_json(candidate_file, errors), candidate_path))
            else:
                errors.append(f"{source}: missing candidate_file_path {candidate_path}")
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def validate_manifest_record(record: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    candidate_id = record.get("observation_candidate_id", "<missing>")
    for field in (
        "observation_candidate_id",
        "candidate_type",
        "candidate_status",
        "origin",
        "related_batch_id",
        "source_access_mode",
        "proposed_failure_modes",
        "candidate_file_path",
    ):
        if field not in record:
            errors.append(f"{source}: {candidate_id}: missing {field}")
    if record.get("requires_human_review") is not True:
        errors.append(f"{source}: {candidate_id}: requires_human_review must be true")
    for field in ("accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if record.get(field) is not False:
            errors.append(f"{source}: {candidate_id}: {field} must be false")
    mode = record.get("source_access_mode")
    if mode not in LOCAL_ONLY_SOURCE_MODES:
        errors.append(f"{source}: {candidate_id}: source_access_mode {mode!r} is not allowed for OBS local mining")
    if record.get("candidate_status") not in {"proposed", "needs_human_review", "policy_blocked", "deferred"}:
        errors.append(f"{source}: {candidate_id}: candidate_status must remain review-gated")
    errors.extend(_forbidden_text_errors(record, f"{source}: {candidate_id}"))
    return errors


def validate_candidate_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors = list(validate_candidate_record(data, source))
    mode = data.get("source_access_mode")
    if mode not in LOCAL_ONLY_SOURCE_MODES:
        errors.append(f"{source}: source_access_mode {mode!r} is not allowed without explicit OBS-AGENT-01 source approval")
    if data.get("required_human_review") is not True:
        errors.append(f"{source}: required_human_review must be true")
    for field in ("accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if data.get(field) is not False:
            errors.append(f"{source}: {field} must be false")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source, include_track_b=False))
    errors.extend(_forbidden_text_errors(data, source))
    return sorted(set(errors))


def validate_audit_report_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_agent_01_report.v0":
        errors.append(f"{source}: schema_version must be obs_agent_01_report.v0")
    if data.get("track") != "Observation":
        errors.append(f"{source}: track must be Observation")
    if data.get("task") != "OBS-AGENT-01":
        errors.append(f"{source}: task must be OBS-AGENT-01")
    truth = _mapping(data.get("truth_boundary"))
    if truth.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required must be true")
    for field in ("candidates_are_observed_baselines", "candidates_are_evidence_truth", "candidates_can_mutate_master_index"):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source, include_track_b=True))
    for section in ("added_docs", "added_inventories", "added_examples", "added_scripts", "added_tests"):
        for path in _string_items(data.get(section)):
            normalized = path.replace("\\", "/")
            if any(normalized.startswith(prefix) for prefix in TRACK_B_PREFIXES):
                errors.append(f"{source}: {section} contains Track B path {path}")
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def _validate_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_DOCS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"docs: missing {path}")
            continue
        text = full_path.read_text(encoding="utf-8").lower()
        if path == DOC_PATH:
            for phrase in ("review", "candidate", "repo-local"):
                if phrase not in text:
                    errors.append(f"{path}: missing phrase {phrase!r}")
    return errors


def _validate_examples(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in EXAMPLE_PATHS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"examples: missing {path}")
            continue
        errors.extend(validate_candidate_payload(_load_json(full_path, errors), path))
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


def _boundary_false_errors(boundary: Mapping[str, Any], source: str, *, include_track_b: bool) -> list[str]:
    errors: list[str] = []
    fields = set(PRODUCT_BOUNDARY_FIELDS)
    if include_track_b:
        fields.add("modified_track_b_files")
    for field in sorted(fields):
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
        f"validate_obs_agent_local_eval_mining: {report['status']}",
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
