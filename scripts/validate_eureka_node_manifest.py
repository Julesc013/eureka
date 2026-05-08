"""Validate Track B Eureka Node manifest governance artifacts.

The validator is intentionally local and read-only. It checks contracts,
registries, examples, and audit evidence for node identity boundaries without
creating node runtime state or authorizing source access.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/node/eureka_node_manifest.v0.json"
POLICY_PATH = "control/inventory/nodes/eureka_node_manifest_policy.json"
MODE_REGISTRY_PATH = "control/inventory/nodes/node_mode_registry.json"
CAPABILITY_REGISTRY_PATH = "control/inventory/nodes/node_capability_registry.json"
AUDIT_REPORT_PATH = "control/audits/track-b-01-eureka-node-manifest-v0/track_b_01_report.json"
EXAMPLE_ROOT = "examples/nodes"
DOC_PATHS = (
    "docs/reference/EUREKA_NODE_MANIFEST_CONTRACT.md",
    "docs/architecture/EUREKA_NODE.md",
)

REQUIRED_MODES = {
    "local_private",
    "local_pack_builder",
    "local_autonomous_dry_run",
    "community_node_future",
    "institution_node_future",
    "hosted_worker_future",
}
REQUIRED_STATUSES = {
    "example_only",
    "contract_only",
    "disabled",
    "dry_run_only",
    "local_private_ready_future",
    "review_required",
    "approval_gated",
    "operator_gated",
    "deferred",
    "blocked",
    "active_future",
}
CURRENT_EXAMPLE_STATUSES = {
    "example_only",
    "contract_only",
    "dry_run_only",
    "deferred",
    "approval_gated",
    "operator_gated",
}
REQUIRED_CAPABILITIES = {
    "repo_local_inspection",
    "local_eval_analysis",
    "search_need_analysis",
    "observation_candidate_preparation",
    "source_lead_preparation",
    "workunit_candidate_preparation_future",
    "pack_validation",
    "pack_drafting_future",
    "evidence_drafting_future",
    "candidate_drafting_future",
    "local_index_read_future",
    "local_index_write_future",
    "local_source_cache_read_future",
    "local_source_cache_write_future",
    "local_evidence_ledger_read_future",
    "local_evidence_ledger_write_future",
    "extraction_planning_future",
    "extraction_runtime_future",
    "approved_metadata_probe_future",
    "approved_api_access_future",
    "local_model_assist_future",
    "hosted_worker_execution_future",
}
REQUIRED_FORBIDDEN_SOURCE_MODES = {
    "unapproved_live_probe",
    "arbitrary_url_fetch",
    "scraping",
    "crawling",
    "browser_automation",
    "bulk_forum_ingestion",
    "bulk_reddit_ingestion",
    "download_binary",
    "installer_execution",
    "credentials_without_approval",
    "api_without_approval",
}
REQUIRED_FORBIDDEN_ACTIONS = {
    "mutate_master_index",
    "mark_candidate_accepted",
    "mark_evidence_accepted",
    "mark_observation_observed_without_human",
    "enable_live_probe",
    "scrape_external_site",
    "crawl_external_site",
    "call_unapproved_api",
    "download_binary",
    "run_installer",
    "execute_downloaded_artifact",
    "store_credentials",
    "upload_to_hosted_backend",
    "create_account_or_user_data",
    "emit_telemetry",
    "claim_rights_clearance",
    "claim_malware_safety",
    "claim_verified_installability",
    "claim_exhaustive_global_search",
    "claim_production_readiness",
}
TRUTH_FALSE_FIELDS = {
    "can_create_observed_baseline",
    "can_create_accepted_evidence",
    "can_create_public_truth",
    "can_mutate_master_index",
    "can_claim_rights_clearance",
    "can_claim_malware_safety",
    "can_claim_verified_installability",
}
PACK_FALSE_FIELDS = {
    "automatic_acceptance_allowed",
    "import_runtime_enabled",
    "upload_runtime_enabled",
    "hosted_submission_enabled",
}
REVIEW_REQUIREMENTS = {
    "human_review_required",
    "review_required_for_public_export",
    "review_required_for_evidence_acceptance",
    "review_required_for_candidate_promotion",
    "review_required_for_source_policy",
    "review_required_for_network_access",
    "review_required_for_master_index_mutation",
}
PRODUCT_BOUNDARY_FIELDS = {
    "implemented_node_runtime",
    "enabled_network_access",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_source_connectors",
    "enabled_downloads",
    "enabled_installers",
    "enabled_execution",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "enabled_pack_import_runtime",
    "enabled_review_runtime",
    "mutated_master_index",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
}
ALLOWED_INPUTS = {
    "repo_local_fixture",
    "committed_pack_example",
    "committed_static_artifact",
    "committed_eval_report",
    "manual_pending_slot",
    "observation_candidate",
    "search_need_record_future",
    "workunit_future",
    "node_policy_future",
    "source_policy_future",
}
ALLOWED_OUTPUTS = {
    "node_report",
    "dry_run_report",
    "observation_candidate",
    "source_lead_candidate",
    "search_need_seed",
    "workunit_seed_future",
    "evidence_draft_future",
    "candidate_record_future",
    "contribution_pack_draft_future",
    "review_item_future",
    "pack_export_future",
}

SENSITIVE_KEY_NAMES = {"api_key", "password", "secret", "credential", "credentials", "token"}
PRIVATE_PATH_MARKERS = ("c:\\", "\\users\\", "/users/", "/home/")
FORBIDDEN_TEXT_CLAIMS = (
    "production ready",
    "production-ready",
    "rights clearance confirmed",
    "rights cleared",
    "malware safe",
    "malware-safe",
    "verified installability",
    "verified installable",
    "exhaustive global search proof",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Eureka Node manifest contract files.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_eureka_node_manifests(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_eureka_node_manifests(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    schema = _load_json(root / SCHEMA_PATH, errors)
    policy = _load_json(root / POLICY_PATH, errors)
    mode_registry = _load_json(root / MODE_REGISTRY_PATH, errors)
    capability_registry = _load_json(root / CAPABILITY_REGISTRY_PATH, errors)
    audit_report = _load_json(root / AUDIT_REPORT_PATH, errors)

    errors.extend(validate_docs(root))
    errors.extend(validate_schema(schema, SCHEMA_PATH))
    errors.extend(validate_policy(policy, POLICY_PATH))
    errors.extend(validate_mode_registry(mode_registry, MODE_REGISTRY_PATH, policy))
    errors.extend(validate_capability_registry(capability_registry, CAPABILITY_REGISTRY_PATH, policy))
    errors.extend(validate_audit_report(audit_report, AUDIT_REPORT_PATH))

    example_paths = list_example_paths(root)
    if len(example_paths) != 6:
        errors.append(f"{EXAMPLE_ROOT}: expected 6 example manifests, found {len(example_paths)}")
    for path in example_paths:
        payload = _load_json(path, errors)
        errors.extend(validate_node_manifest(payload, _relative(root, path), policy, mode_registry, capability_registry))

    return {
        "schema_version": "eureka_node_manifest_validation.v0",
        "status": "valid" if not errors else "invalid",
        "validated_files": sorted(
            [
                SCHEMA_PATH,
                POLICY_PATH,
                MODE_REGISTRY_PATH,
                CAPABILITY_REGISTRY_PATH,
                AUDIT_REPORT_PATH,
                *DOC_PATHS,
                *[_relative(root, path) for path in example_paths],
            ]
        ),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def list_example_paths(repo_root: Path = REPO_ROOT) -> list[Path]:
    root = repo_root.resolve() / EXAMPLE_ROOT
    return sorted(root.glob("*/eureka_node_manifest.json"))


def validate_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in DOC_PATHS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"docs: missing {path}")
            continue
        text = full_path.read_text(encoding="utf-8").lower()
        for phrase in ("eureka node", "review", "master index", "network"):
            if phrase not in text:
                errors.append(f"{path}: missing required phrase {phrase!r}")
    return errors


def validate_schema(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("title") != "EurekaNodeManifestV0":
        errors.append(f"{source}: title must be EurekaNodeManifestV0")
    properties = _mapping(data.get("properties"))
    schema_version = _mapping(properties.get("schema_version"))
    if schema_version.get("const") != "eureka_node_manifest.v0":
        errors.append(f"{source}: schema_version const must be eureka_node_manifest.v0")
    required = set(_string_items(data.get("required")))
    errors.extend(_missing_items(required, _required_policy_fields(), f"{source}: required"))
    if data.get("x-node-runtime-implemented") is not False:
        errors.append(f"{source}: x-node-runtime-implemented must be false")
    if data.get("x-network-access-enabled") is not False:
        errors.append(f"{source}: x-network-access-enabled must be false")
    if data.get("x-master-index-mutation-allowed") is not False:
        errors.append(f"{source}: x-master-index-mutation-allowed must be false")
    return errors


def validate_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "eureka_node_manifest_policy.v0":
        errors.append(f"{source}: schema_version must be eureka_node_manifest_policy.v0")
    errors.extend(_missing_items(data.get("required_fields"), _required_policy_fields(), f"{source}: required_fields"))
    errors.extend(_missing_items(data.get("allowed_modes"), REQUIRED_MODES, f"{source}: allowed_modes"))
    errors.extend(_missing_items(data.get("allowed_statuses"), REQUIRED_STATUSES, f"{source}: allowed_statuses"))
    errors.extend(_missing_items(data.get("current_example_statuses"), CURRENT_EXAMPLE_STATUSES, f"{source}: current_example_statuses"))
    errors.extend(_missing_items(data.get("allowed_capabilities"), REQUIRED_CAPABILITIES, f"{source}: allowed_capabilities"))
    errors.extend(_missing_items(data.get("allowed_inputs"), ALLOWED_INPUTS, f"{source}: allowed_inputs"))
    errors.extend(_missing_items(data.get("allowed_outputs"), ALLOWED_OUTPUTS, f"{source}: allowed_outputs"))
    errors.extend(_missing_items(data.get("forbidden_actions"), REQUIRED_FORBIDDEN_ACTIONS, f"{source}: forbidden_actions"))
    errors.extend(_missing_items(data.get("required_false_booleans"), TRUTH_FALSE_FIELDS | PACK_FALSE_FIELDS, f"{source}: required_false_booleans"))
    errors.extend(_missing_items(data.get("review_requirements"), REVIEW_REQUIREMENTS, f"{source}: review_requirements"))
    errors.extend(_missing_items(data.get("product_boundary_false_fields"), PRODUCT_BOUNDARY_FIELDS, f"{source}: product_boundary_false_fields"))
    return errors


def validate_mode_registry(payload: Any, source: str, policy: Any | None = None) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "node_mode_registry.v0":
        errors.append(f"{source}: schema_version must be node_mode_registry.v0")
    policy_modes = set(_string_items(_mapping(policy).get("allowed_modes"))) or REQUIRED_MODES
    modes = _records_by_id(data.get("modes"), "mode_id", f"{source}: modes", errors)
    errors.extend(_missing_items(modes, policy_modes, f"{source}: modes"))
    for mode_id, record in modes.items():
        if mode_id not in policy_modes:
            errors.append(f"{source}: unknown mode {mode_id}")
        availability = str(record.get("current_availability", ""))
        if mode_id.endswith("_future") and "future" not in availability and "deferred" not in availability:
            errors.append(f"{source}: future mode {mode_id} must be marked future/deferred")
        if not _string_items(record.get("required_approvals")):
            errors.append(f"{source}: mode {mode_id} missing required_approvals")
        if not _string_items(record.get("boundaries")):
            errors.append(f"{source}: mode {mode_id} missing boundaries")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_capability_registry(payload: Any, source: str, policy: Any | None = None) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "node_capability_registry.v0":
        errors.append(f"{source}: schema_version must be node_capability_registry.v0")
    policy_modes = set(_string_items(_mapping(policy).get("allowed_modes"))) or REQUIRED_MODES
    policy_capabilities = set(_string_items(_mapping(policy).get("allowed_capabilities"))) or REQUIRED_CAPABILITIES
    capabilities = _records_by_id(data.get("capabilities"), "capability_id", f"{source}: capabilities", errors)
    errors.extend(_missing_items(capabilities, policy_capabilities, f"{source}: capabilities"))
    for capability_id, record in capabilities.items():
        if capability_id not in policy_capabilities:
            errors.append(f"{source}: unknown capability {capability_id}")
        status = str(record.get("status", ""))
        if capability_id.endswith("_future") and "future" not in status and "deferred" not in status and "disabled" not in status:
            errors.append(f"{source}: future capability {capability_id} must be marked future/deferred/disabled")
        allowed_modes = set(_string_items(record.get("allowed_modes")))
        errors.extend(_unknown_items(allowed_modes, policy_modes, f"{source}: capability {capability_id} allowed_modes"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_audit_report(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "track_b_01_report.v0":
        errors.append(f"{source}: schema_version must be track_b_01_report.v0")
    if data.get("task") != "TRACK-B-01":
        errors.append(f"{source}: task must be TRACK-B-01")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    truth = _mapping(data.get("truth_boundary"))
    for field in (
        "node_output_is_public_truth",
        "node_output_is_accepted_evidence",
        "node_can_mutate_master_index",
        "node_can_mark_observations_observed",
    ):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    if truth.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required must be true")
    return errors


def validate_node_manifest(
    payload: Any,
    source: str,
    policy: Any | None = None,
    mode_registry: Any | None = None,
    capability_registry: Any | None = None,
) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    policy_data = _mapping(policy)
    allowed_modes = set(_string_items(policy_data.get("allowed_modes"))) or REQUIRED_MODES
    allowed_statuses = set(_string_items(policy_data.get("allowed_statuses"))) or REQUIRED_STATUSES
    current_statuses = set(_string_items(policy_data.get("current_example_statuses"))) or CURRENT_EXAMPLE_STATUSES
    allowed_capabilities = set(_string_items(policy_data.get("allowed_capabilities"))) or REQUIRED_CAPABILITIES
    allowed_inputs = set(_string_items(policy_data.get("allowed_inputs"))) or ALLOWED_INPUTS
    allowed_outputs = set(_string_items(policy_data.get("allowed_outputs"))) or ALLOWED_OUTPUTS
    forbidden_actions = set(_string_items(policy_data.get("forbidden_actions"))) or REQUIRED_FORBIDDEN_ACTIONS
    product_boundary_fields = set(_string_items(policy_data.get("product_boundary_false_fields"))) or PRODUCT_BOUNDARY_FIELDS
    review_requirements = set(_string_items(policy_data.get("review_requirements"))) or REVIEW_REQUIREMENTS
    registry_capabilities = _capability_statuses(capability_registry)
    registry_modes = _mode_ids(mode_registry)

    if data.get("schema_version") != "eureka_node_manifest.v0":
        errors.append(f"{source}: schema_version must be eureka_node_manifest.v0")
    errors.extend(_missing_items(data, _required_policy_fields(), f"{source}: top-level"))

    node_mode = str(data.get("node_mode", ""))
    if node_mode not in allowed_modes:
        errors.append(f"{source}: node_mode {node_mode!r} is not allowed")
    if registry_modes and node_mode not in registry_modes:
        errors.append(f"{source}: node_mode {node_mode!r} missing from mode registry")

    node_status = str(data.get("node_status", ""))
    if node_status not in allowed_statuses:
        errors.append(f"{source}: node_status {node_status!r} is not allowed")
    if node_status not in current_statuses:
        errors.append(f"{source}: current example node_status {node_status!r} is not allowed")

    network_access = _mapping(data.get("network_access"))
    if network_access.get("enabled") is not False:
        errors.append(f"{source}: network_access.enabled must be false")
    errors.extend(_missing_items(network_access.get("forbidden_modes"), REQUIRED_FORBIDDEN_SOURCE_MODES, f"{source}: network_access.forbidden_modes"))
    if _string_items(network_access.get("allowed_modes")):
        errors.append(f"{source}: network_access.allowed_modes must be empty for current examples")

    source_access = _mapping(data.get("source_access_policy"))
    if source_access.get("approval_required") is not True:
        errors.append(f"{source}: source_access_policy.approval_required must be true")
    if source_access.get("operator_required") is not True:
        errors.append(f"{source}: source_access_policy.operator_required must be true")
    errors.extend(_missing_items(source_access.get("forbidden_source_modes"), REQUIRED_FORBIDDEN_SOURCE_MODES, f"{source}: source_access_policy.forbidden_source_modes"))

    capability_records = _sequence(data.get("node_capabilities"))
    if not capability_records:
        errors.append(f"{source}: node_capabilities must not be empty")
    for index, item in enumerate(capability_records):
        record = _mapping(item)
        capability_id = str(record.get("capability_id", ""))
        if capability_id not in allowed_capabilities:
            errors.append(f"{source}: node_capabilities[{index}] unknown capability {capability_id!r}")
        if registry_capabilities and capability_id not in registry_capabilities:
            errors.append(f"{source}: node_capabilities[{index}] missing from capability registry")
        if capability_id.endswith("_future"):
            status = str(record.get("capability_status", ""))
            if "future" not in status and "deferred" not in status and "disabled" not in status:
                errors.append(f"{source}: future capability {capability_id} must be marked future/deferred/disabled")

    errors.extend(_unknown_items(set(_string_items(data.get("allowed_inputs"))), allowed_inputs, f"{source}: allowed_inputs"))
    outputs = _mapping(data.get("allowed_outputs"))
    errors.extend(_unknown_items(set(_string_items(outputs.get("categories"))), allowed_outputs, f"{source}: allowed_outputs.categories"))
    errors.extend(_false_field_errors(outputs, TRUTH_FALSE_FIELDS, f"{source}: allowed_outputs"))

    errors.extend(_missing_items(data.get("forbidden_actions"), forbidden_actions, f"{source}: forbidden_actions"))

    local_state = _mapping(data.get("local_state_policy"))
    if local_state.get("local_state_allowed") is not False:
        errors.append(f"{source}: local_state_policy.local_state_allowed must be false")
    if local_state.get("local_state_root_future") is not None:
        errors.append(f"{source}: local_state_policy.local_state_root_future must be null")
    if local_state.get("public_export_requires_review") is not True:
        errors.append(f"{source}: local_state_policy.public_export_requires_review must be true")
    if local_state.get("no_private_data_publication") is not True:
        errors.append(f"{source}: local_state_policy.no_private_data_publication must be true")

    review_policy = _mapping(data.get("review_policy"))
    for field in sorted(review_requirements):
        if review_policy.get(field) is not True:
            errors.append(f"{source}: review_policy.{field} must be true")

    pack_policy = _mapping(data.get("pack_policy"))
    errors.extend(_false_field_errors(pack_policy, PACK_FALSE_FIELDS, f"{source}: pack_policy"))

    product_boundary = _mapping(data.get("product_boundary"))
    errors.extend(_false_field_errors(product_boundary, product_boundary_fields, f"{source}: product_boundary"))

    errors.extend(_sensitive_key_errors(data, source))
    errors.extend(_private_path_errors(data, source))
    errors.extend(_forbidden_text_claim_errors(data, source))
    return errors


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [f"validate_eureka_node_manifest: {report['status']}"]
    lines.append(f"schema_version: {report['schema_version']}")
    lines.append(f"validated_files: {len(report.get('validated_files', []))}")
    errors = report.get("errors", [])
    if errors:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in errors)
    warnings = report.get("warnings", [])
    if warnings:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in warnings)
    return "\n".join(lines) + "\n"


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.is_file():
        errors.append(f"{_relative(REPO_ROOT, path)}: missing file")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_relative(REPO_ROOT, path)}: invalid JSON: {exc}")
        return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _string_items(value: Any) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _missing_items(value: Any, required: set[str], label: str) -> list[str]:
    present = set(value) if isinstance(value, set) else set(_string_items(value))
    if isinstance(value, Mapping):
        present = set(str(key) for key in value)
    return [f"{label} missing {item}" for item in sorted(required - present)]


def _unknown_items(value: set[str], allowed: set[str], label: str) -> list[str]:
    return [f"{label} unknown {item}" for item in sorted(value - allowed)]


def _records_by_id(value: Any, key: str, label: str, errors: list[str]) -> dict[str, Mapping[str, Any]]:
    records: dict[str, Mapping[str, Any]] = {}
    for index, item in enumerate(_sequence(value)):
        record = _mapping(item)
        item_id = record.get(key)
        if not isinstance(item_id, str) or not item_id:
            errors.append(f"{label}[{index}]: missing {key}")
            continue
        if item_id in records:
            errors.append(f"{label}: duplicate {key} {item_id}")
        records[item_id] = record
    return records


def _mode_ids(payload: Any | None) -> set[str]:
    errors: list[str] = []
    return set(_records_by_id(_mapping(payload).get("modes"), "mode_id", "modes", errors))


def _capability_statuses(payload: Any | None) -> dict[str, str]:
    errors: list[str] = []
    records = _records_by_id(_mapping(payload).get("capabilities"), "capability_id", "capabilities", errors)
    return {key: str(record.get("status", "")) for key, record in records.items()}


def _boundary_false_errors(payload: Mapping[str, Any], source: str) -> list[str]:
    return _false_field_errors(payload, PRODUCT_BOUNDARY_FIELDS, f"{source}: product_boundary")


def _false_field_errors(payload: Mapping[str, Any], fields: set[str], label: str) -> list[str]:
    errors: list[str] = []
    for field in sorted(fields):
        if payload.get(field) is not False:
            errors.append(f"{label}.{field} must be false")
    return errors


def _sensitive_key_errors(value: Any, source: str, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in SENSITIVE_KEY_NAMES:
                errors.append(f"{source}: sensitive key {path}.{key_text} is not allowed")
            errors.extend(_sensitive_key_errors(child, source, f"{path}.{key_text}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_sensitive_key_errors(child, source, f"{path}[{index}]"))
    return errors


def _private_path_errors(value: Any, source: str, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in PRIVATE_PATH_MARKERS):
            errors.append(f"{source}: private/local user path marker at {path}")
    elif isinstance(value, Mapping):
        for key, child in value.items():
            errors.extend(_private_path_errors(child, source, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_private_path_errors(child, source, f"{path}[{index}]"))
    return errors


def _forbidden_text_claim_errors(value: Any, source: str, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, str):
        lowered = value.lower()
        for marker in FORBIDDEN_TEXT_CLAIMS:
            if marker in lowered:
                errors.append(f"{source}: forbidden product claim marker {marker!r} at {path}")
    elif isinstance(value, Mapping):
        for key, child in value.items():
            errors.extend(_forbidden_text_claim_errors(child, source, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_forbidden_text_claim_errors(child, source, f"{path}[{index}]"))
    return errors


def _required_policy_fields() -> set[str]:
    return {
        "schema_version",
        "node_manifest_id",
        "node_id",
        "node_label",
        "node_mode",
        "node_status",
        "node_scope",
        "node_operator_posture",
        "node_capabilities",
        "node_limits",
        "network_access",
        "source_access_policy",
        "allowed_inputs",
        "allowed_outputs",
        "forbidden_actions",
        "local_state_policy",
        "privacy_policy",
        "review_policy",
        "pack_policy",
        "workunit_policy_future",
        "audit_policy",
        "product_boundary",
        "no_goals",
        "notes",
    }


def _relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
