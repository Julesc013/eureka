#!/usr/bin/env python3
"""Validate R0-03 contract taxonomy authority records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]

TASK = "R0-03"
REQUIRED_FAMILIES = {
    "repo_layout_contracts",
    "source_registry_contracts",
    "source_record_contracts",
    "source_cache_contracts",
    "evidence_ledger_contracts",
    "candidate_index_contracts",
    "review_queue_contracts",
    "reviewed_index_contracts",
    "pack_contracts",
    "contribution_contracts",
    "archive_product_contracts",
    "runtime_contracts",
    "control_policy_schemas",
    "control_inventory_schemas",
    "generated_artifact_contracts",
    "testing_contracts",
    "IA_metadata_pilot_contracts",
    "Workbench_future_view_models",
    "Search_Interaction_future_packets",
}
REQUIRED_DUPLICATE_RISKS = {
    "control_schemas_policies_packs_vs_contracts_packs",
    "contracts_source_registry_vs_contracts_sources",
    "contracts_source_cache_vs_contracts_stores",
    "contracts_runtime_vs_runtime_helpers",
    "contracts_archive_vs_archive_root",
    "control_inventory_schemas_vs_contracts_repo",
}
REQUIRED_BACKLOG = {
    "migrate_or_reclassify_control_schemas_packs",
    "clarify_contracts_source_registry_vs_sources",
    "clarify_source_cache_vs_stores_contracts",
    "clarify_contracts_runtime_scope",
    "clarify_contracts_archive_vs_archive_root",
    "add_workbench_view_model_contract_location",
    "add_search_interaction_packet_contract_location",
    "add_generated_artifact_contract_exception_registry",
}
REQUIRED_JSON = {
    "control/inventory/contract_taxonomy_input_state.json": "contract_taxonomy_input_state.v0",
    "control/inventory/contract_taxonomy_root_inventory.json": "contract_taxonomy_root_inventory.v0",
    "control/inventory/contract_taxonomy_authority_matrix.json": "contract_taxonomy_authority_matrix.v0",
    "control/inventory/contract_taxonomy_duplicate_authority_report.json": "contract_taxonomy_duplicate_authority_report.v0",
    "control/inventory/contract_taxonomy_control_schemas_decision.json": "contract_taxonomy_control_schemas_decision.v0",
    "control/inventory/contract_taxonomy_migration_backlog.json": "contract_taxonomy_migration_backlog.v0",
    "control/inventory/contract_taxonomy_validator_matrix.json": "contract_taxonomy_validator_matrix.v0",
    "control/inventory/contract_taxonomy_result.json": "contract_taxonomy_result.v0",
    "control/inventory/contract_taxonomy_next_task_decision.json": "contract_taxonomy_next_task_decision.v0",
    "control/audits/repo-layout-contract-taxonomy-cleanup-v0/contract_taxonomy_report.json": "contract_taxonomy_report.v0",
}
REQUIRED_MARKDOWN = (
    "docs/architecture/CONTRACT_TAXONOMY.md",
    "docs/operations/CONTRACT_TAXONOMY_CLEANUP_PLAN.md",
    "control/audits/repo-layout-contract-taxonomy-cleanup-v0/README.md",
    "control/audits/repo-layout-contract-taxonomy-cleanup-v0/root_inventory.md",
    "control/audits/repo-layout-contract-taxonomy-cleanup-v0/authority_matrix.md",
    "control/audits/repo-layout-contract-taxonomy-cleanup-v0/duplicate_authority_report.md",
    "control/audits/repo-layout-contract-taxonomy-cleanup-v0/control_schemas_decision.md",
    "control/audits/repo-layout-contract-taxonomy-cleanup-v0/migration_backlog.md",
    "control/audits/repo-layout-contract-taxonomy-cleanup-v0/validation.md",
    "control/audits/repo-layout-contract-taxonomy-cleanup-v0/generated/sample_summary.md",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = validate_repo(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("Contract taxonomy validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in REQUIRED_JSON.items()}
    validate_markdown(root, errors)
    validate_input_state(payloads["control/inventory/contract_taxonomy_input_state.json"], errors)
    validate_root_inventory(payloads["control/inventory/contract_taxonomy_root_inventory.json"], errors)
    validate_authority_matrix(payloads["control/inventory/contract_taxonomy_authority_matrix.json"], root, errors)
    validate_duplicate_report(payloads["control/inventory/contract_taxonomy_duplicate_authority_report.json"], errors)
    validate_control_schemas_decision(payloads["control/inventory/contract_taxonomy_control_schemas_decision.json"], errors)
    validate_backlog(payloads["control/inventory/contract_taxonomy_migration_backlog.json"], errors)
    validate_result(payloads["control/inventory/contract_taxonomy_result.json"], errors)
    validate_next_task(payloads["control/inventory/contract_taxonomy_next_task_decision.json"], errors)
    validate_report(payloads["control/audits/repo-layout-contract-taxonomy-cleanup-v0/contract_taxonomy_report.json"], errors)

    return {
        "schema_version": "contract_taxonomy_validation.v0",
        "task": TASK,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "network_calls_made": False,
        "model_provider_calls_made": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def load_json(path: Path, schema_version: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {repo_rel(path)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"malformed JSON file {repo_rel(path)}: {exc}")
        return {}
    if payload.get("schema_version") != schema_version:
        errors.append(f"{repo_rel(path)} schema_version must be {schema_version}")
    return payload


def validate_markdown(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_MARKDOWN:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing markdown file: {rel}")
        elif not path.read_text(encoding="utf-8").strip():
            errors.append(f"empty markdown file: {rel}")


def validate_input_state(payload: Mapping[str, Any], errors: list[str]) -> None:
    require_false(payload, "production_readiness_claimed", errors)
    require_false(payload, "public_launch_readiness_claimed", errors)
    require_true(payload, "origin_main_equals_origin_dev", errors)
    require_true(payload, "repo_layout_canon_found", errors)
    require_true(payload, "ia_pilot_closeout_found", errors)
    require_true(payload, "known_debt_includes_control_schemas", errors)


def validate_root_inventory(payload: Mapping[str, Any], errors: list[str]) -> None:
    roots = {str(item.get("path")): item for item in payload.get("roots", []) if isinstance(item, Mapping)}
    for path in (
        "contracts",
        "contracts/repo",
        "contracts/testing",
        "contracts/schema/control",
        "control/policies",
        "control/inventory",
        "examples",
        "runtime",
        "scripts",
    ):
        if path not in roots:
            errors.append(f"root inventory missing {path}")

    if roots.get("contracts/schema/control", {}).get("authority_class") != "CONTROL_SCHEMA":
        errors.append("contracts/schema/control must be classified as CONTROL_SCHEMA")
    if roots.get("examples", {}).get("authority_class") not in {"FIXTURE_SCHEMA", "EXAMPLE_PAYLOAD"}:
        errors.append("examples must be classified as fixture/example only")
    if roots.get("runtime", {}).get("authority_class") != "NOT_CONTRACT_AUTHORITY":
        errors.append("runtime must not be classified as contract authority")
    if roots.get("contracts/repo", {}).get("authority_class") != "PRODUCT_INTERNAL_CONTRACT":
        errors.append("contracts/repo files must be classified")
    testing = roots.get("contracts/testing", {})
    if testing.get("authority_class") != "PRODUCT_INTERNAL_CONTRACT":
        errors.append("contracts/testing must be classified as PRODUCT_INTERNAL_CONTRACT")
    if testing.get("authority_class") in {"EXAMPLE_PAYLOAD", "FIXTURE_SCHEMA"}:
        errors.append("contracts/testing must not be classified as example or fixture authority")
    if testing.get("authority_class") == "NOT_CONTRACT_AUTHORITY":
        errors.append("contracts/testing must not be classified as runtime or generated implementation state")


def validate_authority_matrix(payload: Mapping[str, Any], root: Path, errors: list[str]) -> None:
    families = {str(item.get("family_id")): item for item in payload.get("families", []) if isinstance(item, Mapping)}
    missing = REQUIRED_FAMILIES - set(families)
    if missing:
        errors.append(f"authority matrix missing families: {', '.join(sorted(missing))}")

    for family_id, item in families.items():
        authority = str(item.get("authority_class", ""))
        canonical = str(item.get("canonical_authority_path", ""))
        if authority in {"PRODUCT_PUBLIC_CONTRACT", "PRODUCT_INTERNAL_CONTRACT"}:
            if canonical.startswith("examples/"):
                errors.append(f"{family_id} assigns product authority to examples")
            if canonical.startswith("runtime/"):
                errors.append(f"{family_id} assigns product authority to runtime")
            if canonical.startswith("contracts/schema/control/"):
                errors.append(f"{family_id} assigns product authority to contracts/schema/control")
        if item.get("duplicate_authority_risk") is True and not item.get("migration_required"):
            errors.append(f"{family_id} records duplicate authority without migration_required")

    testing = families.get("testing_contracts", {})
    if testing:
        if testing.get("authority_class") != "PRODUCT_INTERNAL_CONTRACT":
            errors.append("testing_contracts must be PRODUCT_INTERNAL_CONTRACT")
        if testing.get("canonical_authority_path") != "contracts/testing/":
            errors.append("testing_contracts must use contracts/testing/ as canonical authority")
        if "contracts/testing/**" not in set(testing.get("current_paths", [])):
            errors.append("testing_contracts must include contracts/testing/**")
        if testing.get("duplicate_authority_risk") not in {False, "low"}:
            errors.append("testing_contracts duplicate_authority_risk must be false or low")
        if testing.get("migration_required") is not False:
            errors.append("testing_contracts migration_required must be false")
        if not testing.get("validator_required"):
            errors.append("testing_contracts validator_required must be set")
        secondary = str(testing.get("allowed_secondary_role", ""))
        for required in ("control/inventory", "tests", "scripts"):
            if required not in secondary:
                errors.append(f"testing_contracts allowed_secondary_role must mention {required}")
        if testing.get("authority_class") in {"EXAMPLE_PAYLOAD", "FIXTURE_SCHEMA"}:
            errors.append("testing_contracts must not be example payload authority")
        if str(testing.get("canonical_authority_path", "")).startswith("runtime/"):
            errors.append("testing_contracts must not be runtime implementation authority")

    workbench = families.get("Workbench_future_view_models", {})
    if workbench.get("canonical_authority_path") != "contracts/view/pages/workbench/":
        errors.append("Workbench future view models must reserve contracts/view/pages/workbench/")
    search = families.get("Search_Interaction_future_packets", {})
    if search.get("canonical_authority_path") != "contracts/search/interaction/":
        errors.append("Search Interaction future packets must reserve contracts/search/interaction/")
    validate_testing_contracts_on_disk(root, families, errors)


def validate_testing_contracts_on_disk(
    root: Path, families: Mapping[str, Mapping[str, Any]], errors: list[str]
) -> None:
    testing_root = root / "contracts/testing"
    selector_contract = testing_root / "test_selection_result.v0.json"
    test_lane_router_present = (root / "scripts/eureka_test_select.py").is_file() or (
        root / "control/inventory/test_lane_router_result.json"
    ).is_file()

    if testing_root.exists() and "testing_contracts" not in families:
        errors.append("contracts/testing exists but testing_contracts is missing from authority matrix")
    if test_lane_router_present and not testing_root.is_dir():
        errors.append("test lane router requires contracts/testing")
    if test_lane_router_present and not selector_contract.is_file():
        errors.append("test lane router requires contracts/testing/test_selection_result.v0.json")
    if selector_contract.is_file():
        try:
            payload = json.loads(selector_contract.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"contracts/testing/test_selection_result.v0.json must be valid JSON: {exc}")
        else:
            if payload.get("schema_version") != "test_selection_result_schema.v0":
                errors.append("test_selection_result contract schema_version must be test_selection_result_schema.v0")
            properties = payload.get("properties", {})
            if not isinstance(properties, Mapping) or properties.get("schema_version", {}).get("const") != "test_selection_result.v0":
                errors.append("test_selection_result contract must recognize test_selection_result.v0 packets")


def validate_duplicate_report(payload: Mapping[str, Any], errors: list[str]) -> None:
    risks = {str(item.get("risk_id")): item for item in payload.get("duplicate_risks", []) if isinstance(item, Mapping)}
    missing = REQUIRED_DUPLICATE_RISKS - set(risks)
    if missing:
        errors.append(f"duplicate authority report missing risks: {', '.join(sorted(missing))}")
    for risk_id, item in risks.items():
        if not item.get("canonical_authority"):
            errors.append(f"{risk_id} missing canonical_authority")
        if not item.get("secondary_role"):
            errors.append(f"{risk_id} missing secondary_role")
        if item.get("blocks_workbench_foundation") not in {True, False}:
            errors.append(f"{risk_id} must make Workbench blocking state explicit")


def validate_control_schemas_decision(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("decision") != "retain_as_control_schema_authority_with_migration_backlog":
        errors.append("contracts/schema/control decision must retain as control schema authority with migration backlog")
    require_true(payload, "control_schemas_allowed_now", errors)
    require_false(payload, "product_contracts_allowed_under_control_schemas", errors)
    require_true(payload, "migration_required", errors)
    if payload.get("control_schemas_scope") != "control/governance schemas only":
        errors.append("contracts/schema/control scope must be control/governance schemas only")


def validate_backlog(payload: Mapping[str, Any], errors: list[str]) -> None:
    backlog = {str(item.get("backlog_id")): item for item in payload.get("backlog", []) if isinstance(item, Mapping)}
    missing = REQUIRED_BACKLOG - set(backlog)
    if missing:
        errors.append(f"migration backlog missing items: {', '.join(sorted(missing))}")
    for backlog_id, item in backlog.items():
        for key in ("current_paths", "target_authority", "risk", "prerequisite", "recommended_task"):
            if not item.get(key):
                errors.append(f"{backlog_id} missing {key}")
        if item.get("blocks_workbench_foundation") not in {True, False}:
            errors.append(f"{backlog_id} must make Workbench blocking state explicit")
        if item.get("blocks_search_interaction") not in {True, False}:
            errors.append(f"{backlog_id} must make Search Interaction blocking state explicit")


def validate_result(payload: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "root_inventory_added",
        "authority_matrix_added",
        "duplicate_authority_report_added",
        "control_schemas_decision_added",
        "migration_backlog_added",
        "contract_taxonomy_docs_added",
        "validator_added",
        "tests_added",
        "product_contracts_assigned_to_contracts_root",
        "control_schemas_scope_limited_to_control",
        "examples_classified_not_authority",
        "runtime_classified_not_contract_authority",
        "workbench_contract_location_reserved",
        "search_interaction_contract_location_reserved",
        "testing_contract_location_classified",
        "test_selection_result_contract_recognized",
    ):
        require_true(payload, key, errors)
    for key in ("large_file_moves_performed", "files_deleted", "runtime_behavior_changed"):
        require_false(payload, key, errors)
    if payload.get("hard_blockers_remaining") != 0:
        errors.append("hard blockers remaining must be zero")
    if payload.get("warnings_remaining") != 0:
        errors.append("warnings remaining must be zero after explicit classification")
    if not str(payload.get("recommended_next_task", "")).startswith("WORKBENCH-FOUNDATION-00"):
        errors.append("recommended next task must be WORKBENCH-FOUNDATION-00")


def validate_next_task(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("decision") != "WORKBENCH-FOUNDATION-00":
        errors.append("next task decision must point to WORKBENCH-FOUNDATION-00")
    require_false(payload, "production_readiness_claimed", errors)
    require_false(payload, "public_launch_readiness_claimed", errors)


def validate_report(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("status") != "pass":
        errors.append("audit report status must be pass")
    for key in (
        "large_file_moves_performed",
        "files_deleted",
        "runtime_behavior_changed",
        "source_probe_executed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        require_false(payload, key, errors)
    authority = payload.get("authority", {})
    if isinstance(authority, Mapping):
        if authority.get("examples_are_authority") is not False:
            errors.append("audit report must state examples are not authority")
        if authority.get("runtime_is_contract_authority") is not False:
            errors.append("audit report must state runtime is not contract authority")


def require_true(payload: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if payload.get(key) is not True:
        errors.append(f"{key} must be true")


def require_false(payload: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if payload.get(key) is not False:
        errors.append(f"{key} must be false")


def repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
