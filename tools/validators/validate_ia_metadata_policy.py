#!/usr/bin/env python3
"""Validate IA-00 metadata connector policy closure artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]

POLICY_FILES = {
    "connector": Path("control/policies/ia_metadata_connector_policy.json"),
    "source_access": Path("control/policies/ia_source_access_policy.json"),
    "user_agent": Path("control/policies/ia_user_agent_policy.json"),
    "rate_limit": Path("control/policies/ia_rate_limit_policy.json"),
    "kill_switch": Path("control/policies/ia_kill_switch_policy.json"),
    "non_claim": Path("control/policies/ia_non_claim_policy.json"),
}

INVENTORY_FILES = {
    "allowed_endpoints": Path("control/inventory/ia_metadata_allowed_endpoint_matrix.json"),
    "forbidden_actions": Path("control/inventory/ia_metadata_forbidden_action_matrix.json"),
    "policy_decision": Path("control/inventory/ia_metadata_policy_decision.json"),
    "runtime_gates": Path("control/inventory/ia_metadata_runtime_gate_matrix.json"),
    "fixture_requirements": Path("control/inventory/ia_metadata_fixture_requirements.json"),
    "live_probe_requirements": Path("control/inventory/ia_metadata_live_probe_requirements.json"),
    "source_cache_requirements": Path("control/inventory/ia_metadata_source_cache_requirements.json"),
    "evidence_requirements": Path("control/inventory/ia_metadata_evidence_requirements.json"),
    "result": Path("control/inventory/ia_00_result.json"),
    "next_task": Path("control/inventory/ia_00_next_task_decision.json"),
}

DOC_FILES = [
    Path("docs/architecture/IA_METADATA_CONNECTOR_MODEL.md"),
    Path("docs/operations/IA_METADATA_SOURCE_POLICY.md"),
    Path("docs/operations/IA_METADATA_NON_CLAIMS.md"),
    Path("docs/operations/IA_METADATA_PILOT_RUNBOOK.md"),
    Path("docs/reference/IA_METADATA_FIELD_MAPPING.md"),
    Path("docs/reference/IA_METADATA_POLICY_MATRIX.md"),
]

AUDIT_FILES = [
    Path("control/audits/ia-00-metadata-connector-approval-v0/README.md"),
    Path("control/audits/ia-00-metadata-connector-approval-v0/ia_00_report.json"),
    Path("control/audits/ia-00-metadata-connector-approval-v0/allowed_endpoint_matrix.md"),
    Path("control/audits/ia-00-metadata-connector-approval-v0/forbidden_action_matrix.md"),
    Path("control/audits/ia-00-metadata-connector-approval-v0/policy_decision.md"),
    Path("control/audits/ia-00-metadata-connector-approval-v0/fixture_requirements.md"),
    Path("control/audits/ia-00-metadata-connector-approval-v0/live_probe_requirements.md"),
    Path("control/audits/ia-00-metadata-connector-approval-v0/source_cache_evidence_review_handoff.md"),
    Path("control/audits/ia-00-metadata-connector-approval-v0/non_claims.md"),
    Path("control/audits/ia-00-metadata-connector-approval-v0/validation.md"),
]

REQUIRED_ALLOWED_ENDPOINTS = {
    "metadata_search_small",
    "item_metadata_read",
    "item_file_list_metadata_read",
}

REQUIRED_FORBIDDEN_ACTIONS = {
    "downloads",
    "uploads",
    "write_apis",
    "s3_apis",
    "authenticated_account_apis",
    "reviews_write_apis",
    "tasks_write_apis",
    "item_file_fetch",
    "broad_collection_crawl",
    "unbounded_paging",
    "public_query_fanout",
    "arbitrary_url_fetch",
    "wayback_content_replay",
    "page_scraping_outside_metadata_api_posture",
    "source_cache_write_in_IA_00",
    "evidence_ledger_write_in_IA_00",
    "candidate_index_mutation_in_IA_00",
    "reviewed_index_mutation_in_IA_00",
    "master_index_mutation",
    "production_deployment",
}

REQUIRED_GATES = {"IA-00", "IA-01", "IA-02", "IA-03", "IA-04", "IA-05", "IA-06", "IA-07"}

REQUIRED_FIXTURES = {
    "metadata_search_fixture",
    "exact_item_metadata_fixture",
    "file_list_metadata_fixture",
    "missing_item_fixture",
    "malformed_partial_fixture",
    "retry_after_429_fixture",
    "large_file_list_fixture",
    "no_download_proof",
}

REQUIRED_LIVE_REQUIREMENTS = {
    "operator_approval",
    "kill_switch",
    "user_agent_contact",
    "row_cap",
    "timeout",
    "retry_policy",
    "retry_after",
    "cache",
    "one_shot_small_probe",
    "no_public_fanout",
    "no_downloads",
}

REQUIRED_SOURCE_CACHE_REQUIREMENTS = {
    "source_observation_id",
    "observed_at",
    "request_policy_id",
    "response_hash",
    "raw_cache_policy",
    "normalized_summary",
    "ttl",
    "deletion_reset_command",
}

REQUIRED_EVIDENCE_REQUIREMENTS = {
    "title_claim_candidate",
    "mediatype_claim_candidate",
    "creator_date_description_claim_candidate_if_present",
    "file_list_claim_candidate",
    "checksum_file_metadata_claim_candidate",
    "source_locator_claim_candidate",
    "no_accepted_truth_without_review",
}

FORBIDDEN_DIRTY_PATHS = [
    "runtime/connectors",
    "runtime/extraction",
    "runtime/search/quality",
    "site/dist/data/public_index",
    "site/dist",
    "native",
    "crates",
    "eureka-instance",
    "instances",
    ".aide.local",
    "secrets",
    ".env",
]


def main(argv: Sequence[str] | None = None) -> int:
    _ = argv
    result = validate_ia_metadata_policy(REPO_ROOT)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


def validate_ia_metadata_policy(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    policies = {name: _load_json(repo_root / path, errors) for name, path in POLICY_FILES.items()}
    inventories = {name: _load_json(repo_root / path, errors) for name, path in INVENTORY_FILES.items()}

    for path in DOC_FILES + AUDIT_FILES:
        if not (repo_root / path).exists():
            errors.append(f"missing_file:{path.as_posix()}")

    _validate_connector_policy(policies.get("connector", {}), errors)
    _validate_source_access_policy(policies.get("source_access", {}), errors)
    _validate_user_agent_policy(policies.get("user_agent", {}), errors)
    _validate_rate_limit_policy(policies.get("rate_limit", {}), errors)
    _validate_kill_switch_policy(policies.get("kill_switch", {}), errors)
    _validate_non_claim_policy(policies.get("non_claim", {}), errors)

    _validate_allowed_endpoints(inventories.get("allowed_endpoints", {}), errors)
    _validate_forbidden_actions(inventories.get("forbidden_actions", {}), errors)
    _validate_runtime_gates(inventories.get("runtime_gates", {}), errors)
    _validate_requirements(inventories.get("fixture_requirements", {}), REQUIRED_FIXTURES, "fixture", errors)
    _validate_requirements(inventories.get("live_probe_requirements", {}), REQUIRED_LIVE_REQUIREMENTS, "live", errors)
    _validate_requirements(
        inventories.get("source_cache_requirements", {}),
        REQUIRED_SOURCE_CACHE_REQUIREMENTS,
        "source_cache",
        errors,
    )
    _validate_requirements(inventories.get("evidence_requirements", {}), REQUIRED_EVIDENCE_REQUIREMENTS, "evidence", errors)
    _validate_policy_decision(inventories.get("policy_decision", {}), errors)
    _validate_result(inventories.get("result", {}), errors)
    _validate_docs(repo_root, errors)
    _validate_no_forbidden_git_state(repo_root, errors, warnings)

    return {
        "schema_version": "ia_metadata_policy_validation.v0",
        "task": "IA-00",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "live_calls_enabled": False,
        "source_probe_execution_enabled": False,
        "downloads_enabled": False,
        "uploads_enabled": False,
        "public_search_fanout_enabled": False,
        "source_cache_writes_enabled": False,
        "evidence_ledger_writes_enabled": False,
        "candidate_index_mutation_enabled": False,
        "reviewed_index_mutation_enabled": False,
        "master_index_mutation_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _load_json(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.exists():
        errors.append(f"missing_file:{path.relative_to(REPO_ROOT).as_posix()}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{path.relative_to(REPO_ROOT).as_posix()}:{exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"json_not_object:{path.relative_to(REPO_ROOT).as_posix()}")
        return {}
    return payload


def _expect_false(payload: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if payload.get(key) is not False:
        errors.append(f"expected_false:{key}")


def _expect_true(payload: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if payload.get(key) is not True:
        errors.append(f"expected_true:{key}")


def _validate_connector_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("connector_status") != "policy_approved_runtime_disabled":
        errors.append("connector_status_not_runtime_disabled")
    for key in [
        "live_calls_enabled",
        "source_probe_execution_enabled",
        "downloads_enabled",
        "uploads_enabled",
        "write_apis_enabled",
        "account_auth_enabled",
        "public_search_fanout_enabled",
        "arbitrary_url_fetch_enabled",
        "wayback_content_replay_enabled",
        "source_cache_writes_enabled",
        "evidence_ledger_writes_enabled",
        "candidate_index_mutation_enabled",
        "reviewed_index_mutation_enabled",
        "master_index_mutation_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ]:
        _expect_false(policy, key, errors)
    for key in [
        "metadata_only_future_pilot",
        "fixture_replay_required_before_live_probe",
        "operator_approval_required_for_live_probe",
        "kill_switch_required",
        "user_agent_required",
        "contact_required",
        "retry_after_required",
        "cache_required",
        "review_required_before_truth",
    ]:
        _expect_true(policy, key, errors)


def _validate_source_access_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    for key in [
        "source_cache_writes_enabled_now",
        "evidence_ledger_writes_enabled_now",
        "candidate_index_mutation_enabled_now",
        "reviewed_index_mutation_enabled_now",
        "master_index_mutation_enabled_now",
        "live_calls_enabled_now",
        "public_user_query_sync_enabled",
        "telemetry_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ]:
        _expect_false(policy, key, errors)
    for key in [
        "metadata_is_source_observation_material_only",
        "fixture_replay_required_before_live_probe",
        "operator_approval_required_before_live_probe",
    ]:
        _expect_true(policy, key, errors)
    allowed = set(policy.get("allowed_future_access_classes", []))
    if not REQUIRED_ALLOWED_ENDPOINTS.issubset(allowed):
        errors.append("source_access_missing_allowed_metadata_classes")


def _validate_user_agent_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    for key in [
        "descriptive_project_user_agent_required",
        "contact_identifier_required",
        "generic_python_urllib_default_forbidden",
        "operator_must_configure_contact",
        "committed_contact_secret_forbidden",
    ]:
        _expect_true(policy, key, errors)
    for key in ["live_calls_enabled_now", "model_provider_used", "production_readiness_claimed", "public_launch_readiness_claimed"]:
        _expect_false(policy, key, errors)


def _validate_rate_limit_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if int(policy.get("first_probe_search_row_cap", 0)) > 10:
        errors.append("first_probe_search_row_cap_too_high")
    for key in [
        "timeout_seconds_required",
        "retry_budget_required",
        "backoff_required",
        "retry_after_honored",
        "cache_before_repeat_required",
        "large_file_list_cap_required",
        "unbounded_paging_forbidden",
        "public_fanout_forbidden",
    ]:
        _expect_true(policy, key, errors)
    for key in ["live_calls_enabled_now", "download_install_execute_enabled", "production_readiness_claimed", "public_launch_readiness_claimed"]:
        _expect_false(policy, key, errors)


def _validate_kill_switch_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    for key in [
        "kill_switch_required",
        "kill_switch_checked_before_every_future_live_call",
        "future_enable_requires_operator_approval",
        "future_disable_must_fail_closed",
        "source_cache_writes_stop_when_disabled",
        "evidence_writes_stop_when_disabled",
    ]:
        _expect_true(policy, key, errors)
    if policy.get("default_state") != "disabled":
        errors.append("kill_switch_default_not_disabled")
    for key in ["public_search_fanout_enabled", "live_calls_enabled_now", "production_readiness_claimed", "public_launch_readiness_claimed"]:
        _expect_false(policy, key, errors)


def _validate_non_claim_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    for key in [
        "metadata_is_not_truth",
        "source_observation_material_only",
        "review_required_before_truth",
        "no_rights_claims_from_metadata_alone",
        "no_safety_claims_from_metadata_alone",
        "no_compatibility_truth_from_metadata_alone",
        "no_availability_truth_from_metadata_alone",
        "no_source_trust_inference_without_review",
        "live_ia_json_to_public_truth_forbidden",
    ]:
        _expect_true(policy, key, errors)
    for key in ["production_readiness_claimed", "public_launch_readiness_claimed"]:
        _expect_false(policy, key, errors)


def _validate_allowed_endpoints(matrix: Mapping[str, Any], errors: list[str]) -> None:
    rows = matrix.get("rows", [])
    row_by_id = {row.get("endpoint_class"): row for row in rows if isinstance(row, dict)}
    if set(row_by_id) != REQUIRED_ALLOWED_ENDPOINTS:
        errors.append("allowed_endpoint_matrix_rows_mismatch")
    required_fields = {
        "endpoint_class",
        "future_status",
        "allowed_after",
        "purpose",
        "required_policy",
        "max_rows_or_scope",
        "cache_required",
        "review_required",
        "forbidden_side_effects",
    }
    for endpoint_id, row in row_by_id.items():
        missing = required_fields - set(row)
        if missing:
            errors.append(f"allowed_endpoint_missing_fields:{endpoint_id}:{','.join(sorted(missing))}")
        if row.get("future_status") != "future_allowed_after_IA_01_and_operator_approval":
            errors.append(f"allowed_endpoint_bad_status:{endpoint_id}")
        if row.get("cache_required") is not True or row.get("review_required") is not True:
            errors.append(f"allowed_endpoint_missing_cache_or_review:{endpoint_id}")
        if "downloads" not in row.get("forbidden_side_effects", []) and "file_fetch" not in row.get("forbidden_side_effects", []):
            errors.append(f"allowed_endpoint_does_not_forbid_download_path:{endpoint_id}")


def _validate_forbidden_actions(matrix: Mapping[str, Any], errors: list[str]) -> None:
    rows = matrix.get("rows", [])
    row_by_id = {row.get("action_id"): row for row in rows if isinstance(row, dict)}
    missing = REQUIRED_FORBIDDEN_ACTIONS - set(row_by_id)
    if missing:
        errors.append(f"forbidden_action_matrix_missing:{','.join(sorted(missing))}")
    for action_id, row in row_by_id.items():
        if row.get("status") != "forbidden":
            errors.append(f"forbidden_action_not_forbidden:{action_id}")
        for key in ["reason", "future_reconsideration_gate", "validator_assertion"]:
            if not row.get(key):
                errors.append(f"forbidden_action_missing_{key}:{action_id}")


def _validate_runtime_gates(matrix: Mapping[str, Any], errors: list[str]) -> None:
    rows = matrix.get("gates", [])
    gate_ids = {row.get("gate_id") for row in rows if isinstance(row, dict)}
    if gate_ids != REQUIRED_GATES:
        errors.append("runtime_gate_matrix_rows_mismatch")
    ia02 = next((row for row in rows if isinstance(row, dict) and row.get("gate_id") == "IA-02"), {})
    if "IA-01" not in str(ia02.get("enables", "")) and "IA-01" not in " ".join(ia02.get("required_validators", [])):
        errors.append("IA_02_does_not_reference_IA_01_gate")


def _validate_requirements(matrix: Mapping[str, Any], required: set[str], prefix: str, errors: list[str]) -> None:
    rows = matrix.get("requirements", [])
    ids = {row.get("requirement_id") for row in rows if isinstance(row, dict)}
    missing = required - ids
    if missing:
        errors.append(f"{prefix}_requirements_missing:{','.join(sorted(missing))}")
    for row in rows:
        if isinstance(row, dict) and row.get("required") is False:
            errors.append(f"{prefix}_requirement_not_required:{row.get('requirement_id')}")


def _validate_policy_decision(decision: Mapping[str, Any], errors: list[str]) -> None:
    if decision.get("decision") != "approve_metadata_only_local_pilot_policy_runtime_disabled":
        errors.append("policy_decision_not_approved_runtime_disabled")
    if decision.get("future_live_probe_allowed_after") != "IA-01":
        errors.append("policy_decision_live_probe_not_after_IA_01")
    for key in [
        "live_calls_enabled_now",
        "source_cache_writes_enabled_now",
        "evidence_writes_enabled_now",
        "candidate_index_mutation_enabled_now",
        "reviewed_index_mutation_enabled_now",
        "downloads_enabled",
        "uploads_enabled",
        "public_search_fanout_enabled",
    ]:
        _expect_false(decision, key, errors)
    _expect_true(decision, "operator_approval_required_for_IA_02", errors)


def _validate_result(result: Mapping[str, Any], errors: list[str]) -> None:
    if result.get("status") not in {"pass", "pass_with_warnings"}:
        errors.append("ia_00_result_status_not_passing")
    for key in [
        "live_source_call_performed",
        "source_probe_executed",
        "source_cache_write_performed",
        "evidence_ledger_write_performed",
        "candidate_index_mutated",
        "reviewed_index_mutated",
        "master_index_mutated",
        "download_performed",
        "upload_performed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ]:
        _expect_false(result, key, errors)


def _validate_docs(repo_root: Path, errors: list[str]) -> None:
    required_terms = {
        "docs/architecture/IA_METADATA_CONNECTOR_MODEL.md": [
            "policy closure",
            "runtime execution disabled",
            "source observation",
            "accepted Eureka truth without review",
        ],
        "docs/operations/IA_METADATA_SOURCE_POLICY.md": [
            "does not approve live calls",
            "downloads",
            "public query fanout",
            "No IA metadata field creates accepted truth by itself",
        ],
        "docs/operations/IA_METADATA_NON_CLAIMS.md": [
            "no production readiness",
            "Metadata Is Not Truth",
        ],
    }
    for rel_path, terms in required_terms.items():
        text = (repo_root / rel_path).read_text(encoding="utf-8") if (repo_root / rel_path).exists() else ""
        lowered = text.lower()
        for term in terms:
            if term.lower() not in lowered:
                errors.append(f"doc_missing_term:{rel_path}:{term}")


def _validate_no_forbidden_git_state(repo_root: Path, errors: list[str], warnings: list[str]) -> None:
    status = subprocess.run(
        ["git", "status", "--short", "--", *FORBIDDEN_DIRTY_PATHS],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if status.returncode != 0:
        warnings.append("git_status_forbidden_paths_failed")
    elif status.stdout.strip():
        errors.append("forbidden_path_modified:" + status.stdout.strip().replace("\n", ";"))

    tracked_instances = subprocess.run(
        ["git", "ls-files", "--", "eureka-instance", "instances"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if tracked_instances.returncode != 0:
        warnings.append("git_ls_files_instances_failed")
    elif tracked_instances.stdout.strip():
        errors.append("local_instance_state_tracked")


if __name__ == "__main__":
    raise SystemExit(main())
