from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = ROOT / "control" / "audits" / "deep-extraction-runtime-planning-v0"
DEFAULT_REPORT = AUDIT_ROOT / "deep_extraction_runtime_planning_report.json"
DEFAULT_INVENTORY = ROOT / "control" / "inventory" / "extraction" / "deep_extraction_runtime_plan.json"

READINESS_VALUES = {
    "ready_for_local_dry_run_runtime_after_operator_approval",
    "ready_for_sandboxed_fixture_runtime_after_operator_approval",
    "ready_for_planning_only",
    "blocked_deep_extraction_contract_missing",
    "blocked_extraction_examples_missing",
    "blocked_sandbox_policy_missing",
    "blocked_resource_limit_policy_missing",
    "blocked_privacy_path_secret_policy_missing",
    "blocked_executable_payload_policy_missing",
    "blocked_OCR_transcription_boundary_missing",
    "blocked_pack_import_boundary_incomplete",
    "blocked_source_cache_evidence_boundary_incomplete",
    "blocked_candidate_index_boundary_incomplete",
    "blocked_public_search_page_boundary_incomplete",
    "blocked_other",
}

REQUIRED_AUDIT_FILES = [
    "README.md",
    "PLANNING_SUMMARY.md",
    "READINESS_DECISION.md",
    "EXTRACTION_CONTRACT_GATE_REVIEW.md",
    "SANDBOX_AND_RESOURCE_LIMIT_GATE_REVIEW.md",
    "PRIVACY_PATH_SECRET_GATE_REVIEW.md",
    "EXECUTABLE_PAYLOAD_AND_CONTENT_SAFETY_GATE_REVIEW.md",
    "OCR_TRANSCRIPTION_AND_TEXT_BOUNDARY_REVIEW.md",
    "PACK_IMPORT_AND_STAGING_BOUNDARY_REVIEW.md",
    "SOURCE_CACHE_EVIDENCE_CANDIDATE_BOUNDARY_REVIEW.md",
    "PUBLIC_SEARCH_AND_PAGE_BOUNDARY_REVIEW.md",
    "RUNTIME_BOUNDARY.md",
    "DEEP_EXTRACTION_RUNTIME_ARCHITECTURE_PLAN.md",
    "APPROVED_INPUT_MODEL.md",
    "EXTRACTION_PIPELINE_PLAN.md",
    "CONTAINER_TYPE_HANDLING_PLAN.md",
    "SANDBOX_RESOURCE_AND_TIMEOUT_PLAN.md",
    "OUTPUT_REPORT_AND_CANDIDATE_EFFECT_MODEL.md",
    "FAILURE_ROLLBACK_AND_AUDIT_MODEL.md",
    "SECURITY_AND_ABUSE_REVIEW.md",
    "IMPLEMENTATION_PHASES.md",
    "ACCEPTANCE_CRITERIA.md",
    "DO_NOT_IMPLEMENT_YET.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "deep_extraction_runtime_planning_report.json",
]

REQUIRED_REPORT_FIELDS = [
    "report_id",
    "created_by_slice",
    "repo_head",
    "branch",
    "worktree_status",
    "readiness_decision",
    "extraction_contract_gate_review",
    "sandbox_resource_limit_gate_review",
    "privacy_path_secret_gate_review",
    "executable_payload_content_safety_gate_review",
    "OCR_transcription_text_boundary_review",
    "pack_import_staging_boundary_review",
    "source_cache_evidence_candidate_boundary_review",
    "public_search_page_boundary_review",
    "runtime_boundary",
    "runtime_architecture_plan",
    "approved_input_model",
    "extraction_pipeline_plan",
    "container_type_handling_plan",
    "sandbox_resource_timeout_plan",
    "output_report_candidate_effect_model",
    "failure_rollback_audit_model",
    "security_abuse_review",
    "implementation_phases",
    "acceptance_criteria",
    "command_results",
    "remaining_blockers",
    "next_recommended_branch",
    "notes",
]

REPORT_TRUE = ["planning_only"]
REPORT_FALSE = [
    "runtime_extraction_implemented",
    "extraction_executed",
    "files_opened",
    "archive_unpacked",
    "arbitrary_local_path_enabled",
    "arbitrary_url_fetch_enabled",
    "URL_fetched",
    "live_source_called",
    "external_calls_performed",
    "payload_executed",
    "installer_executed",
    "script_execution_enabled",
    "package_manager_invoked",
    "emulator_vm_launched",
    "OCR_performed",
    "transcription_performed",
    "extraction_queue_implemented",
    "extraction_store_implemented",
    "sandbox_runtime_implemented",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "public_search_runtime_mutated",
    "page_runtime_mutated",
    "pack_import_runtime_mutated",
    "connector_runtime_executed",
    "telemetry_enabled",
    "accounts_enabled",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
]

INVENTORY_TRUE = [
    "sandbox_policy_required",
    "resource_limits_required",
    "executable_payload_policy_required",
    "privacy_path_secret_policy_required",
    "operator_approval_required",
]

INVENTORY_FALSE = [
    "runtime_extraction_implemented",
    "extraction_queue_implemented",
    "extraction_store_implemented",
    "sandbox_runtime_implemented",
    "arbitrary_local_path_enabled",
    "arbitrary_url_fetch_enabled",
    "network_enabled",
    "payload_execution_enabled",
    "installer_execution_enabled",
    "script_execution_enabled",
    "package_manager_invocation_enabled",
    "emulator_vm_launch_enabled",
    "OCR_runtime_enabled",
    "transcription_runtime_enabled",
    "recursive_extraction_enabled",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "master_index_mutation_allowed",
    "public_search_integration_enabled",
    "page_runtime_integration_enabled",
    "pack_import_integration_enabled",
    "connector_runtime_integration_enabled",
    "telemetry_enabled",
    "accounts_enabled",
]

ACCEPTANCE_PHRASES = [
    "sandbox policy",
    "resource limits",
    "privacy/path/secret",
    "executable payload",
    "OCR/transcription",
    "mutation boundary",
    "approved input",
    "operator approval",
]

DO_NOT_IMPLEMENT_PHRASES = [
    "no extraction runtime",
    "no archive unpacking",
    "no arbitrary local file reads",
    "no URL fetching",
    "no payload execution",
    "no OCR runtime",
    "no source cache writes",
    "no evidence ledger writes",
    "no public/local/master index mutation",
]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_file(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing file: {path.relative_to(ROOT)}")


def _validate_bool(data: dict[str, Any], key: str, expected: bool, errors: list[str], prefix: str) -> None:
    if data.get(key) is not expected:
        errors.append(f"{prefix}.{key} must be {str(expected).lower()}")


def _combined_text(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists()).lower()


def validate(report_path: Path, inventory_path: Path) -> list[str]:
    errors: list[str] = []

    if not AUDIT_ROOT.exists():
        errors.append(f"missing audit pack: {AUDIT_ROOT.relative_to(ROOT)}")
    for name in REQUIRED_AUDIT_FILES:
        _require_file(AUDIT_ROOT / name, errors)

    doc = ROOT / "docs" / "operations" / "DEEP_EXTRACTION_RUNTIME_PLAN.md"
    _require_file(doc, errors)
    _require_file(inventory_path, errors)
    _require_file(report_path, errors)

    report: dict[str, Any] = {}
    inventory: dict[str, Any] = {}
    if report_path.exists():
        try:
            report = _load_json(report_path)
        except Exception as exc:  # noqa: BLE001 - bounded validator output
            errors.append(f"report JSON parse failed: {exc}")
    if inventory_path.exists():
        try:
            inventory = _load_json(inventory_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"inventory JSON parse failed: {exc}")

    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"report missing field: {field}")

    decision = report.get("readiness_decision")
    if decision not in READINESS_VALUES:
        errors.append(f"invalid readiness_decision: {decision}")

    for key in REPORT_TRUE:
        _validate_bool(report, key, True, errors, "report")
    for key in REPORT_FALSE:
        _validate_bool(report, key, False, errors, "report")

    if inventory.get("status") != "planning_only":
        errors.append("inventory.status must be planning_only")
    for key in INVENTORY_TRUE:
        _validate_bool(inventory, key, True, errors, "inventory")
    for key in INVENTORY_FALSE:
        _validate_bool(inventory, key, False, errors, "inventory")

    acceptance = _combined_text([AUDIT_ROOT / "ACCEPTANCE_CRITERIA.md"])
    for phrase in ACCEPTANCE_PHRASES:
        if phrase.lower() not in acceptance:
            errors.append(f"acceptance criteria missing phrase: {phrase}")

    do_not = _combined_text([AUDIT_ROOT / "DO_NOT_IMPLEMENT_YET.md"])
    for phrase in DO_NOT_IMPLEMENT_PHRASES:
        if phrase.lower() not in do_not:
            errors.append(f"DO_NOT_IMPLEMENT_YET missing phrase: {phrase}")

    boundary_paths = [
        AUDIT_ROOT / "SANDBOX_AND_RESOURCE_LIMIT_GATE_REVIEW.md",
        AUDIT_ROOT / "PRIVACY_PATH_SECRET_GATE_REVIEW.md",
        AUDIT_ROOT / "EXECUTABLE_PAYLOAD_AND_CONTENT_SAFETY_GATE_REVIEW.md",
        AUDIT_ROOT / "OCR_TRANSCRIPTION_AND_TEXT_BOUNDARY_REVIEW.md",
        AUDIT_ROOT / "SOURCE_CACHE_EVIDENCE_CANDIDATE_BOUNDARY_REVIEW.md",
        AUDIT_ROOT / "PUBLIC_SEARCH_AND_PAGE_BOUNDARY_REVIEW.md",
        AUDIT_ROOT / "RUNTIME_BOUNDARY.md",
        doc,
    ]
    boundary_text = _combined_text(boundary_paths)
    for phrase in [
        "sandbox",
        "resource",
        "privacy",
        "executable",
        "ocr",
        "transcription",
        "no public search",
        "no page",
        "no mutation",
    ]:
        if phrase not in boundary_text:
            errors.append(f"boundary docs missing phrase: {phrase}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate P105 Deep Extraction Runtime Planning v0.")
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report_path = Path(args.report)
    inventory_path = Path(args.inventory)
    if not report_path.is_absolute():
        report_path = ROOT / report_path
    if not inventory_path.is_absolute():
        inventory_path = ROOT / inventory_path

    errors = validate(report_path, inventory_path)
    payload = {
        "created_by": "deep_extraction_runtime_plan_validator_v0",
        "errors": errors,
        "report": str(report_path.relative_to(ROOT)) if report_path.exists() and report_path.is_relative_to(ROOT) else str(report_path),
        "status": "valid" if not errors else "invalid",
    }
    if not errors and report_path.exists():
        payload["report_id"] = _load_json(report_path).get("report_id")
        payload["readiness_decision"] = _load_json(report_path).get("readiness_decision")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif errors:
        print("Deep Extraction Runtime Planning validation failed")
        for error in errors:
            print(f"- {error}")
    else:
        print("Deep Extraction Runtime Planning validation")
        print("status: valid")
        print(f"report: {payload['report']}")
        print(f"readiness_decision: {payload.get('readiness_decision')}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

