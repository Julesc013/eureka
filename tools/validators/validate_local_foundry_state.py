"""Validate Track B Local Foundry State governance artifacts.

The validator is deterministic and read-only. It checks declarative local
foundry state contracts, policies, examples, and docs without creating local
state, calling networks, calling models, or granting runtime permission.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = "contracts/schema/control/policies/node/local_foundry_state.v0.json"
STATE_POLICY_PATH = "control/inventory/local_state/local_foundry_state_policy.json"
KIND_REGISTRY_PATH = "control/inventory/local_state/local_foundry_state_kind_registry.json"
PATH_POLICY_PATH = "control/inventory/local_state/local_foundry_path_policy.json"
PRIVACY_POLICY_PATH = "control/inventory/local_state/local_foundry_privacy_policy.json"
EXPORT_POLICY_PATH = "control/inventory/local_state/local_foundry_export_policy.json"
RESET_POLICY_PATH = "control/inventory/local_state/local_foundry_reset_policy.json"
AUDIT_REPORT_PATH = "control/audits/track-b-06-local-foundry-state-contract-v0/track_b_06_report.json"
EXAMPLE_ROOT = "examples/local_foundry_state"
DOC_PATHS = (
    "docs/reference/LOCAL_FOUNDRY_STATE_CONTRACT.md",
    "docs/architecture/LOCAL_FOUNDRY_STATE_MODEL.md",
    "docs/operations/LOCAL_FOUNDRY_STATE_POLICY.md",
    "docs/operations/LOCAL_FOUNDRY_RESET_AND_EXPORT.md",
)

ALLOWED_STATUSES = {
    "example_only",
    "contract_only",
    "disabled",
    "planned",
    "dry_run_only",
    "private_local_future",
    "review_required",
    "approval_gated",
    "operator_gated",
    "deferred",
    "blocked",
    "active_future",
}
CURRENT_ALLOWED_STATUSES = {
    "example_only",
    "contract_only",
    "disabled",
    "planned",
    "dry_run_only",
    "deferred",
    "blocked",
}
ALLOWED_SCOPES = {
    "local_private",
    "local_pack_builder",
    "local_autonomous_dry_run",
    "local_review_queue_future",
    "local_source_cache_future",
    "local_evidence_ledger_future",
    "local_candidate_store_future",
    "local_index_preview_future",
    "community_node_future",
    "institution_node_future",
    "hosted_worker_future",
}
ALLOWED_STATE_KINDS = {
    "node_report",
    "workunit_run_report",
    "workunit_result",
    "dry_run_report",
    "validation_report",
    "observation_candidate",
    "observation_review_decision",
    "source_lead_candidate",
    "search_need_seed",
    "workunit_seed",
    "candidate_draft",
    "evidence_draft",
    "source_cache_draft",
    "evidence_ledger_draft",
    "review_queue_draft",
    "pack_builder_draft",
    "pack_export_draft",
    "local_index_preview",
    "snapshot_preview",
    "relay_preview",
    "private_user_note_future",
}
FORBIDDEN_STATE_KINDS = {
    "secret_or_credential",
    "account_session",
    "telemetry_stream",
    "private_user_file",
    "raw_browser_profile",
    "executable_download",
    "installer_payload",
    "accepted_public_record",
    "accepted_evidence_truth",
    "master_index_record",
    "rights_clearance",
    "malware_safety",
    "verified_installability",
    "exhaustive_global_search_proof",
    "production_readiness_claim",
}
ALLOWED_DATA_CLASSIFICATIONS = {
    "public_safe",
    "public_safe_after_review",
    "local_private",
    "sensitive",
    "secret",
    "prohibited",
}
CURRENT_EXAMPLE_CLASSIFICATIONS = {
    "public_safe",
    "public_safe_after_review",
}
EXPORT_MODES = {
    "no_export",
    "audit_report_export",
    "pack_draft_export_future",
    "contribution_pack_export_future",
    "source_pack_export_future",
    "evidence_pack_export_future",
    "index_pack_export_future",
    "snapshot_export_future",
    "review_required_export_future",
}
ALLOWED_FUTURE_ROOTS = {
    ".aide.local/eureka/",
    ".local/eureka/",
    ".cache/eureka/",
    ".tmp/eureka/",
    "control/audits/**/generated/",
    "control/audits/**/reports/",
}
FORBIDDEN_ROOTS = {
    "site/dist/",
    "contracts/",
    "runtime/",
    "surfaces/",
    "snapshots/",
    "native/",
    "crates/",
    "control/inventory/publication/",
    "control/inventory/sources/",
    "control/inventory/observations/accepted/",
    "evals/search_usefulness/external_baselines/batches/*/observations/observed*",
    ".git/",
}
REVIEW_GATES = {
    "human_review_required_for_public_export",
    "source_policy_review_required",
    "evidence_review_required",
    "candidate_review_required",
    "pack_review_required",
    "master_index_review_required",
    "privacy_review_required",
    "rights_review_required",
    "risk_review_required",
    "operator_approval_required_for_network",
    "legal_or_rights_decision_stop_required",
}
TRUTH_FALSE_FIELDS = {
    "local_state_is_public_truth",
    "local_state_is_accepted_evidence",
    "local_state_is_master_index",
    "local_state_can_mutate_master_index",
    "local_state_can_mark_observed_baseline",
    "local_state_can_claim_rights_clearance",
    "local_state_can_claim_malware_safety",
    "local_state_can_claim_verified_installability",
    "local_state_can_claim_exhaustive_global_search",
    "local_state_can_claim_production_readiness",
}
PRODUCT_BOUNDARY_FIELDS = {
    "implemented_local_foundry_runtime",
    "created_local_state",
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
    "enabled_node_runtime",
    "enabled_workunit_runtime",
    "enabled_pack_import_runtime",
    "enabled_review_runtime",
    "enabled_model_provider_calls",
    "mutated_master_index",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "local_foundry_state_id",
    "state_label",
    "state_status",
    "state_scope",
    "state_owner_posture",
    "state_root_policy",
    "state_kinds",
    "allowed_paths",
    "forbidden_paths",
    "git_tracking_policy",
    "privacy_policy",
    "data_classification",
    "source_access_posture",
    "network_posture",
    "node_refs",
    "workunit_refs",
    "workunit_result_refs",
    "observation_candidate_refs",
    "source_lead_refs",
    "search_need_seed_refs",
    "candidate_draft_refs",
    "evidence_draft_refs",
    "source_cache_draft_refs",
    "evidence_ledger_draft_refs",
    "review_queue_refs",
    "pack_builder_refs",
    "export_policy",
    "reset_delete_policy",
    "retention_policy",
    "review_gates",
    "truth_boundary",
    "product_boundary",
    "no_goals",
    "notes",
}
SOURCE_POSTURE_FALSE_FIELDS = {
    "source_access_enabled",
    "live_probe_enabled",
    "source_sync_enabled",
    "source_connectors_enabled",
}
NETWORK_POSTURE_FALSE_FIELDS = {
    "network_access_enabled",
    "model_provider_calls_enabled",
}
GIT_TRUE_FIELDS = {
    "local_state_roots_must_be_ignored",
    "audit_reports_may_be_committed",
    "exported_packs_may_be_committed_after_review",
    "private_cache_must_not_be_committed",
    "secrets_must_not_be_committed",
}
GIT_FALSE_FIELDS = {
    "private_state_tracked_by_git",
}
PRIVACY_TRUE_FIELDS = {
    "no_private_data_publication",
    "no_credentials",
    "no_account_sessions",
    "no_raw_browser_profiles",
    "no_telemetry_streams",
    "opt_in_export_only",
    "review_required_before_public_export",
    "reset_delete_available",
}
EXPORT_TRUE_FIELDS = {
    "public_export_requires_review",
}
EXPORT_FALSE_FIELDS = {
    "automatic_public_export_allowed",
    "automatic_master_index_import_allowed",
    "automatic_evidence_acceptance_allowed",
}
ROOT_CREATION_FALSE_FIELDS = {
    "state_root_created",
    "state_files_created",
}
CLAIM_PHRASES = {
    "rights clearance",
    "malware safe",
    "malware safety",
    "verified installability",
    "exhaustive global search",
    "production readiness",
}
PRIVATE_PATH_MARKERS = {
    "c:\\users\\",
    "/users/",
    "/home/",
}
SENSITIVE_KEY_NAMES = {
    "api_key",
    "apikey",
    "password",
    "token",
    "access_token",
    "auth_token",
    "credential_value",
    "credential_material",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_local_foundry_state(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []

    for path in (
        SCHEMA_PATH,
        STATE_POLICY_PATH,
        KIND_REGISTRY_PATH,
        PATH_POLICY_PATH,
        PRIVACY_POLICY_PATH,
        EXPORT_POLICY_PATH,
        RESET_POLICY_PATH,
        AUDIT_REPORT_PATH,
        *DOC_PATHS,
    ):
        if not (repo_root / path).is_file():
            errors.append(f"missing required file: {path}")

    if errors:
        return _report(errors)

    errors.extend(validate_schema(read_json(repo_root / SCHEMA_PATH), SCHEMA_PATH))
    errors.extend(validate_state_policy(read_json(repo_root / STATE_POLICY_PATH), STATE_POLICY_PATH))
    errors.extend(validate_kind_registry(read_json(repo_root / KIND_REGISTRY_PATH), KIND_REGISTRY_PATH))
    errors.extend(validate_path_policy(read_json(repo_root / PATH_POLICY_PATH), PATH_POLICY_PATH))
    errors.extend(validate_privacy_policy(read_json(repo_root / PRIVACY_POLICY_PATH), PRIVACY_POLICY_PATH))
    errors.extend(validate_export_policy(read_json(repo_root / EXPORT_POLICY_PATH), EXPORT_POLICY_PATH))
    errors.extend(validate_reset_policy(read_json(repo_root / RESET_POLICY_PATH), RESET_POLICY_PATH))
    errors.extend(validate_docs(repo_root))

    example_paths = sorted((repo_root / EXAMPLE_ROOT).glob("*.json"))
    if len(example_paths) != 5:
        errors.append(f"{EXAMPLE_ROOT} expected 5 examples, found {len(example_paths)}")

    seen_ids: set[str] = set()
    for path in example_paths:
        ref = path.relative_to(repo_root).as_posix()
        record = read_json(path)
        errors.extend(validate_local_foundry_state_record(record, ref, repo_root=repo_root))
        state_id = record.get("local_foundry_state_id")
        if state_id in seen_ids:
            errors.append(f"{ref}: duplicate local_foundry_state_id {state_id}")
        seen_ids.add(state_id)

    return _report(errors)


def validate_schema(schema: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if schema.get("title") != "EurekaLocalFoundryStateV0":
        errors.append(f"{path}: unexpected schema title")
    required = set(schema.get("required", []))
    missing = sorted(REQUIRED_TOP_LEVEL_FIELDS - required)
    if missing:
        errors.append(f"{path}: missing required schema fields {missing}")
    x_flags = {
        "x-local-foundry-runtime-implemented",
        "x-local-state-created",
        "x-network-access-enabled",
        "x-model-provider-calls-enabled",
    }
    for flag in sorted(x_flags):
        if schema.get(flag) is not False:
            errors.append(f"{path}: {flag} must be false")
    return errors


def validate_state_policy(policy: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "local_foundry_state_policy.v0":
        errors.append(f"{path}: unexpected schema_version")
    errors.extend(_require_values(path, "required_fields", policy, REQUIRED_TOP_LEVEL_FIELDS))
    errors.extend(_require_values(path, "allowed_statuses", policy, ALLOWED_STATUSES))
    errors.extend(_require_values(path, "allowed_scopes", policy, ALLOWED_SCOPES))
    errors.extend(_require_values(path, "allowed_state_kinds", policy, ALLOWED_STATE_KINDS))
    errors.extend(_require_values(path, "forbidden_state_kinds", policy, FORBIDDEN_STATE_KINDS))
    errors.extend(_require_values(path, "export_modes", policy, EXPORT_MODES))
    errors.extend(_require_values(path, "required_review_gates", policy, REVIEW_GATES))
    errors.extend(_require_values(path, "required_truth_boundary_false_booleans", policy, TRUTH_FALSE_FIELDS))
    errors.extend(_require_values(path, "required_product_boundary_false_booleans", policy, PRODUCT_BOUNDARY_FIELDS))
    errors.extend(_check_false_map(path, "product_boundary", policy.get("product_boundary", {}), PRODUCT_BOUNDARY_FIELDS))
    return errors


def validate_kind_registry(registry: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if registry.get("schema_version") != "local_foundry_state_kind_registry.v0":
        errors.append(f"{path}: unexpected schema_version")
    errors.extend(_require_values(path, "allowed_statuses", registry, ALLOWED_STATUSES))
    current_status_field = "current_allowed_statuses"
    if current_status_field not in registry:
        current_status_field = "current_example_allowed_statuses"
    errors.extend(_require_values(path, current_status_field, registry, CURRENT_ALLOWED_STATUSES))
    errors.extend(_require_values(path, "allowed_scopes", registry, ALLOWED_SCOPES))
    errors.extend(_require_values(path, "allowed_state_kinds", registry, ALLOWED_STATE_KINDS))
    errors.extend(_require_values(path, "forbidden_state_kinds", registry, FORBIDDEN_STATE_KINDS))
    errors.extend(_check_false_map(path, "product_boundary", registry.get("product_boundary", {}), PRODUCT_BOUNDARY_FIELDS))
    return errors


def validate_path_policy(policy: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "local_foundry_path_policy.v0":
        errors.append(f"{path}: unexpected schema_version")
    errors.extend(_require_values(path, "allowed_future_roots", policy, ALLOWED_FUTURE_ROOTS))
    errors.extend(_require_values(path, "forbidden_roots", policy, FORBIDDEN_ROOTS))
    if policy.get("root_creation_allowed_by_this_task") is not False:
        errors.append(f"{path}: root_creation_allowed_by_this_task must be false")
    errors.extend(_check_false_map(path, "product_boundary", policy.get("product_boundary", {}), PRODUCT_BOUNDARY_FIELDS))
    return errors


def validate_privacy_policy(policy: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "local_foundry_privacy_policy.v0":
        errors.append(f"{path}: unexpected schema_version")
    errors.extend(_require_values(path, "data_classification_values", policy, ALLOWED_DATA_CLASSIFICATIONS))
    errors.extend(_require_values(path, "current_example_allowed_classifications", policy, CURRENT_EXAMPLE_CLASSIFICATIONS))
    rules = policy.get("privacy_rules", {})
    errors.extend(_check_true_map(path, "privacy_rules", rules, PRIVACY_TRUE_FIELDS))
    errors.extend(_check_false_map(path, "product_boundary", policy.get("product_boundary", {}), PRODUCT_BOUNDARY_FIELDS))
    return errors


def validate_export_policy(policy: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "local_foundry_export_policy.v0":
        errors.append(f"{path}: unexpected schema_version")
    errors.extend(_require_values(path, "export_modes", policy, EXPORT_MODES))
    rules = policy.get("export_rules", {})
    errors.extend(_check_true_map(path, "export_rules", rules, EXPORT_TRUE_FIELDS))
    errors.extend(_check_false_map(path, "export_rules", rules, EXPORT_FALSE_FIELDS))
    errors.extend(_check_false_map(path, "product_boundary", policy.get("product_boundary", {}), PRODUCT_BOUNDARY_FIELDS))
    return errors


def validate_reset_policy(policy: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "local_foundry_reset_policy.v0":
        errors.append(f"{path}: unexpected schema_version")
    reset = policy.get("reset_delete_policy", {})
    for key in ("reset_allowed", "delete_allowed"):
        if reset.get(key) is not True:
            errors.append(f"{path}: reset_delete_policy.{key} must be true")
    for key in ("audit_record_policy", "private_state_deletion_policy", "export_preservation_policy"):
        if not reset.get(key):
            errors.append(f"{path}: reset_delete_policy.{key} is required")
    errors.extend(_check_false_map(path, "product_boundary", policy.get("product_boundary", {}), PRODUCT_BOUNDARY_FIELDS))
    return errors


def validate_docs(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    for doc in DOC_PATHS:
        text = (repo_root / doc).read_text(encoding="utf-8").lower()
        for phrase in ("local foundry state", "review", "master-index"):
            if phrase not in text:
                errors.append(f"{doc}: missing phrase {phrase!r}")
    return errors


def validate_local_foundry_state_record(
    record: Mapping[str, Any],
    path: str,
    *,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    errors: list[str] = []

    missing = sorted(REQUIRED_TOP_LEVEL_FIELDS - set(record))
    if missing:
        errors.append(f"{path}: missing required fields {missing}")

    if record.get("schema_version") != "local_foundry_state.v0":
        errors.append(f"{path}: schema_version must be local_foundry_state.v0")

    status = record.get("state_status")
    if status not in ALLOWED_STATUSES:
        errors.append(f"{path}: state_status {status!r} is not allowed")
    if status not in CURRENT_ALLOWED_STATUSES:
        errors.append(f"{path}: current example state_status {status!r} is not allowed")

    scope = record.get("state_scope")
    if scope not in ALLOWED_SCOPES:
        errors.append(f"{path}: state_scope {scope!r} is not allowed")

    state_kinds = set(record.get("state_kinds", []))
    unknown_kinds = sorted(state_kinds - ALLOWED_STATE_KINDS)
    forbidden_kinds = sorted(state_kinds & FORBIDDEN_STATE_KINDS)
    if unknown_kinds:
        errors.append(f"{path}: unknown state_kinds {unknown_kinds}")
    if forbidden_kinds:
        errors.append(f"{path}: forbidden state_kinds {forbidden_kinds}")

    root_policy = record.get("state_root_policy", {})
    errors.extend(_check_false_map(path, "state_root_policy", root_policy, ROOT_CREATION_FALSE_FIELDS))
    if root_policy.get("root_status") != "policy_reference_only":
        errors.append(f"{path}: state_root_policy.root_status must be policy_reference_only")

    for key in ("allowed_paths",):
        for value in record.get(key, []):
            errors.extend(_validate_allowed_future_path(path, f"{key}", value))
    for value in root_policy.get("future_root_refs", []):
        errors.extend(_validate_allowed_future_path(path, "state_root_policy.future_root_refs", value))

    for value in record.get("allowed_paths", []):
        if _path_matches_forbidden_root(value):
            errors.append(f"{path}: allowed_paths references forbidden root {value!r}")

    for value in root_policy.get("future_root_refs", []):
        if _path_matches_forbidden_root(value):
            errors.append(f"{path}: future_root_refs references forbidden root {value!r}")

    data_class = record.get("data_classification", {}).get("current_classification")
    if data_class not in ALLOWED_DATA_CLASSIFICATIONS:
        errors.append(f"{path}: data_classification.current_classification {data_class!r} is unknown")
    if data_class not in CURRENT_EXAMPLE_CLASSIFICATIONS:
        errors.append(f"{path}: current example data classification {data_class!r} is not allowed")
    if record.get("data_classification", {}).get("secret_or_prohibited_allowed") is not False:
        errors.append(f"{path}: data_classification.secret_or_prohibited_allowed must be false")

    errors.extend(_check_false_map(path, "source_access_posture", record.get("source_access_posture", {}), SOURCE_POSTURE_FALSE_FIELDS))
    errors.extend(_check_false_map(path, "network_posture", record.get("network_posture", {}), NETWORK_POSTURE_FALSE_FIELDS))
    errors.extend(_check_true_map(path, "git_tracking_policy", record.get("git_tracking_policy", {}), GIT_TRUE_FIELDS))
    errors.extend(_check_false_map(path, "git_tracking_policy", record.get("git_tracking_policy", {}), GIT_FALSE_FIELDS))
    errors.extend(_check_true_map(path, "privacy_policy", record.get("privacy_policy", {}), PRIVACY_TRUE_FIELDS))

    export_policy = record.get("export_policy", {})
    if export_policy.get("export_mode") not in EXPORT_MODES:
        errors.append(f"{path}: export_policy.export_mode {export_policy.get('export_mode')!r} is unknown")
    errors.extend(_check_true_map(path, "export_policy", export_policy, EXPORT_TRUE_FIELDS))
    errors.extend(_check_false_map(path, "export_policy", export_policy, EXPORT_FALSE_FIELDS))

    reset_policy = record.get("reset_delete_policy", {})
    for key in ("reset_allowed", "delete_allowed"):
        if reset_policy.get(key) is not True:
            errors.append(f"{path}: reset_delete_policy.{key} must be true")
    if reset_policy.get("actual_state_created") is not False:
        errors.append(f"{path}: reset_delete_policy.actual_state_created must be false")

    errors.extend(_check_true_map(path, "review_gates", record.get("review_gates", {}), REVIEW_GATES))
    errors.extend(_check_false_map(path, "truth_boundary", record.get("truth_boundary", {}), TRUTH_FALSE_FIELDS))
    errors.extend(_check_false_map(path, "product_boundary", record.get("product_boundary", {}), PRODUCT_BOUNDARY_FIELDS))
    errors.extend(_scan_record_for_sensitive_or_claims(record, path))

    return errors


def _require_values(path: str, field: str, data: Mapping[str, Any], expected: Iterable[str]) -> list[str]:
    actual = set(data.get(field, []))
    missing = sorted(set(expected) - actual)
    if missing:
        return [f"{path}: {field} missing {missing}"]
    return []


def _check_false_map(path: str, field: str, data: Any, keys: Iterable[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, Mapping):
        return [f"{path}: {field} must be an object"]
    for key in sorted(keys):
        if data.get(key) is not False:
            errors.append(f"{path}: {field}.{key} must be false")
    return errors


def _check_true_map(path: str, field: str, data: Any, keys: Iterable[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, Mapping):
        return [f"{path}: {field} must be an object"]
    for key in sorted(keys):
        if data.get(key) is not True:
            errors.append(f"{path}: {field}.{key} must be true")
    return errors


def _validate_allowed_future_path(path: str, field: str, value: Any) -> list[str]:
    if not isinstance(value, str):
        return [f"{path}: {field} value must be a string"]
    normalized = value.replace("\\", "/")
    if _looks_like_private_user_path(normalized):
        return [f"{path}: {field} references private/local user path {value!r}"]
    if _path_matches_forbidden_root(normalized):
        return [f"{path}: {field} references forbidden root {value!r}"]
    if not _path_matches_allowed_future_root(normalized):
        return [f"{path}: {field} references path outside allowed future roots {value!r}"]
    return []


def _path_matches_allowed_future_root(value: str) -> bool:
    if any(value.startswith(root) for root in (".aide.local/eureka/", ".local/eureka/", ".cache/eureka/", ".tmp/eureka/")):
        return True
    if value.startswith("control/audits/") and ("/generated/" in value or "/reports/" in value):
        return True
    return False


def _path_matches_forbidden_root(value: str) -> bool:
    normalized = value.replace("\\", "/")
    if normalized == ".git" or normalized.startswith(".git/"):
        return True
    for root in FORBIDDEN_ROOTS:
        if "*" in root:
            prefix = root.split("*", 1)[0]
            if normalized.startswith(prefix):
                return True
            continue
        if normalized == root.rstrip("/") or normalized.startswith(root):
            return True
    return False


def _looks_like_private_user_path(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in PRIVATE_PATH_MARKERS)


def _scan_record_for_sensitive_or_claims(record: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    for key_path, key, value in _walk(record):
        key_lower = key.lower()
        if key_lower in SENSITIVE_KEY_NAMES:
            errors.append(f"{path}: sensitive key {key_path}")
        if isinstance(value, str):
            text = value.lower()
            if _looks_like_private_user_path(text):
                errors.append(f"{path}: private/local user path in {key_path}")
            for phrase in sorted(CLAIM_PHRASES):
                if phrase in text:
                    errors.append(f"{path}: forbidden claim phrase {phrase!r} in {key_path}")
    return errors


def _walk(value: Any, prefix: str = "$") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}"
            yield child_prefix, str(key), child
            yield from _walk(child, child_prefix)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_prefix = f"{prefix}[{index}]"
            yield child_prefix, str(index), child
            yield from _walk(child, child_prefix)


def _report(errors: Sequence[str]) -> dict[str, Any]:
    sorted_errors = sorted(errors)
    return {
        "status": "invalid" if sorted_errors else "valid",
        "errors": sorted_errors,
        "checked": {
            "schema": SCHEMA_PATH,
            "policies": sorted(
                [
                    STATE_POLICY_PATH,
                    KIND_REGISTRY_PATH,
                    PATH_POLICY_PATH,
                    PRIVACY_POLICY_PATH,
                    EXPORT_POLICY_PATH,
                    RESET_POLICY_PATH,
                ]
            ),
            "examples": EXAMPLE_ROOT,
        },
    }


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description="Validate Local Foundry State governance artifacts.")
    parser.add_argument("--json", action="store_true", help="Print a JSON report.")
    args = parser.parse_args(argv)

    report = validate_local_foundry_state(REPO_ROOT)
    if args.json:
        stdout.write(json.dumps(report, indent=2, sort_keys=True))
        stdout.write("\n")
    elif report["status"] == "valid":
        stdout.write("Local Foundry State validation: PASS\n")
    else:
        stdout.write("Local Foundry State validation: FAIL\n")
        for error in report["errors"]:
            stdout.write(f"- {error}\n")
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
