#!/usr/bin/env python3
"""Validate Object Page Contract v0 governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_object_page import validate_all_examples  # noqa: E402


CONTRACT_PATH = REPO_ROOT / "contracts" / "pages" / "object_page.v0.json"
SECTION_CONTRACT_PATH = REPO_ROOT / "contracts" / "pages" / "object_page_section.v0.json"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "pages" / "object_page_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "object-page-contract-v0"
REPORT_PATH = AUDIT_DIR / "object_page_contract_report.json"
DOC_PATH = REPO_ROOT / "docs" / "reference" / "OBJECT_PAGE_CONTRACT.md"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "OBJECT_PAGE_SCHEMA.md",
    "OBJECT_IDENTITY_MODEL.md",
    "OBJECT_STATUS_AND_LANE_MODEL.md",
    "VERSION_STATE_RELEASE_MODEL.md",
    "REPRESENTATION_MODEL.md",
    "MEMBER_AND_CONTAINER_MODEL.md",
    "SOURCE_EVIDENCE_PROVENANCE_MODEL.md",
    "COMPATIBILITY_MODEL.md",
    "RIGHTS_RISK_ACTION_POSTURE_MODEL.md",
    "CONFLICT_AND_DUPLICATE_MODEL.md",
    "ABSENCE_NEAR_MISS_AND_GAP_MODEL.md",
    "RESULT_CARD_AND_SEARCH_PROJECTION.md",
    "API_PROJECTION.md",
    "STATIC_DEMO_PROJECTION.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "NO_DOWNLOAD_INSTALL_EXECUTION_POLICY.md",
    "NO_RUNTIME_AND_NO_MUTATION_POLICY.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_OBJECT_PAGE_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "object_page_contract_report.json",
}
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "object_page_id",
    "object_page_kind",
    "status",
    "created_by_tool",
    "object_identity",
    "object_status",
    "title",
    "summary",
    "versions_states_releases",
    "representations",
    "members",
    "sources",
    "evidence",
    "compatibility",
    "rights_risk_action_posture",
    "conflicts",
    "absence_near_misses_gaps",
    "result_card_projection",
    "api_projection",
    "static_projection",
    "privacy",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
HARD_FALSE_FIELDS = {
    "runtime_object_page_implemented",
    "persistent_object_page_store_implemented",
    "object_page_generated_from_live_source",
    "live_source_called",
    "external_calls_performed",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "candidate_promotion_performed",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "execution_enabled",
    "arbitrary_url_fetch_enabled",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "telemetry_exported",
}
POLICY_FALSE_FIELDS = {
    "runtime_object_pages_implemented",
    "persistent_object_page_store_implemented",
    "static_demo_available",
    "public_search_object_links_enabled_now",
    "live_source_calls_allowed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "candidate_promotion_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "master_index_mutation_allowed",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "execution_enabled",
    "arbitrary_url_fetch_enabled",
    "rights_clearance_claimed",
    "malware_safety_claimed",
}
REQUIRED_DOC_PHRASES = (
    "contract-only",
    "evidence-first",
    "not an app store",
    "not a downloader",
    "no runtime object pages",
    "no source cache mutation",
    "no evidence ledger mutation",
    "no candidate promotion",
    "no public index mutation",
    "no master index mutation",
    "no rights clearance",
    "no malware safety",
    "known absence",
    "result-card projection",
)


def validate_object_page_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    contract = _read_json_object(CONTRACT_PATH, errors, "contracts/pages/object_page.v0.json")
    if contract:
        _validate_contract(contract, errors)
    section = _read_json_object(SECTION_CONTRACT_PATH, errors, "contracts/pages/object_page_section.v0.json")
    if section:
        if section.get("x-runtime_object_page_implemented") is not False:
            errors.append("object_page_section.v0.json x-runtime_object_page_implemented must be false.")
    policy = _read_json_object(POLICY_PATH, errors, "control/inventory/pages/object_page_policy.json")
    if policy:
        _validate_policy(policy, errors)
    _validate_docs(errors)
    _validate_audit_pack(errors, warnings)
    examples = validate_all_examples(strict=True)
    if examples.get("status") != "valid":
        errors.append("object page examples failed validation.")
        errors.extend(examples.get("errors", []))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "object_page_contract_validator_v0",
        "contract_file": "contracts/pages/object_page.v0.json",
        "section_contract_file": "contracts/pages/object_page_section.v0.json",
        "policy_file": "control/inventory/pages/object_page_policy.json",
        "report_id": _report_id(),
        "example_count": examples.get("example_count", 0),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("object_page.v0.json x-status must be contract_only.")
    for key in (
        "x-runtime_object_page_implemented",
        "x-persistent_object_page_store_implemented",
        "x-live_source_calls_allowed",
        "x-downloads_enabled",
        "x-installs_enabled",
        "x-execution_enabled",
        "x-source_cache_mutation_allowed",
        "x-evidence_ledger_mutation_allowed",
        "x-candidate_index_mutation_allowed",
        "x-candidate_promotion_allowed",
        "x-master_index_mutation_allowed",
    ):
        if contract.get(key) is not False:
            errors.append(f"object_page.v0.json {key} must be false.")
    required = set(contract.get("required", []))
    missing = sorted((REQUIRED_CONTRACT_FIELDS | HARD_FALSE_FIELDS) - required)
    if missing:
        errors.append(f"object_page.v0.json missing required fields: {', '.join(missing)}")
    props = contract.get("properties")
    if not isinstance(props, Mapping):
        errors.append("object_page.v0.json properties must be an object.")
    else:
        for key in sorted(REQUIRED_CONTRACT_FIELDS | HARD_FALSE_FIELDS):
            if key not in props:
                errors.append(f"object_page.v0.json properties missing {key}.")
    defs = contract.get("$defs")
    if not isinstance(defs, Mapping):
        errors.append("object_page.v0.json $defs must be present.")
        return
    for key in (
        "object_identity",
        "object_status",
        "version_state_release",
        "representation",
        "member",
        "source",
        "evidence",
        "compatibility",
        "rights_risk_action_posture",
        "conflict",
        "absence_near_misses_gaps",
        "result_card_projection",
        "api_projection",
        "static_projection",
        "privacy",
    ):
        if key not in defs:
            errors.append(f"object_page.v0.json $defs missing {key}.")


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "contract_only":
        errors.append("object_page_policy.status must be contract_only.")
    for key in sorted(POLICY_FALSE_FIELDS):
        if policy.get(key) is not False:
            errors.append(f"object_page_policy.{key} must be false.")
    next_contracts = policy.get("next_contracts")
    for key in ("source_page_contract", "comparison_page_contract", "cross_source_identity_resolution_contract"):
        if not isinstance(next_contracts, list) or key not in next_contracts:
            errors.append(f"object_page_policy.next_contracts missing {key}.")


def _validate_docs(errors: list[str]) -> None:
    if not DOC_PATH.is_file():
        errors.append("docs/reference/OBJECT_PAGE_CONTRACT.md: missing.")
        return
    text = DOC_PATH.read_text(encoding="utf-8").casefold()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.casefold() not in text:
            errors.append(f"OBJECT_PAGE_CONTRACT.md missing phrase: {phrase}")


def _validate_audit_pack(errors: list[str], warnings: list[str]) -> None:
    if not AUDIT_DIR.is_dir():
        errors.append("control/audits/object-page-contract-v0: missing audit directory.")
        return
    present = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - present)
    if missing:
        errors.append(f"missing P79 audit files: {', '.join(missing)}")
    report = _read_json_object(REPORT_PATH, errors, "object_page_contract_report.json")
    if not report:
        return
    if report.get("report_id") != "object_page_contract_v0":
        errors.append("object_page_contract_report.json report_id must be object_page_contract_v0.")
    if report.get("contract_file") != "contracts/pages/object_page.v0.json":
        errors.append("object_page_contract_report.json contract_file must point to contracts/pages/object_page.v0.json.")
    guarantees = report.get("no_runtime_no_mutation_guarantees")
    if not isinstance(guarantees, Mapping):
        errors.append("report no_runtime_no_mutation_guarantees must be present.")
    else:
        for key in (
            "runtime_object_pages_implemented",
            "persistent_object_page_store_implemented",
            "object_page_generated_from_live_source",
            "live_source_called",
            "external_calls_performed",
            "source_cache_mutation_allowed",
            "evidence_ledger_mutation_allowed",
            "candidate_index_mutation_allowed",
            "candidate_promotion_allowed",
            "public_index_mutation_allowed",
            "local_index_mutation_allowed",
            "master_index_mutation_allowed",
            "downloads_enabled",
            "uploads_enabled",
            "installs_enabled",
            "execution_enabled",
            "arbitrary_url_fetch_enabled",
            "rights_clearance_claimed",
            "malware_safety_claimed",
            "telemetry_implemented",
        ):
            if guarantees.get(key) is not False:
                errors.append(f"report no_runtime_no_mutation_guarantees.{key} must be false.")
    runtime = report.get("runtime_status")
    if not isinstance(runtime, Mapping):
        errors.append("report runtime_status must be present.")
    else:
        for key in ("runtime_object_pages_implemented", "persistent_object_page_store_implemented", "telemetry_implemented"):
            if runtime.get(key) is not False:
                errors.append(f"report runtime_status.{key} must be false.")
    if report.get("next_recommended_branch") != "P80 Source Page Contract v0":
        errors.append("next_recommended_branch must be P80 Source Page Contract v0.")
    if not report.get("remaining_blockers"):
        errors.append("remaining_blockers must be recorded.")
    warnings.append("P79 is contract-only; runtime object pages remain deferred.")


def _read_json_object(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"{label}: missing.")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: invalid JSON at line {exc.lineno}: {exc.msg}.")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"{label}: top-level JSON must be an object.")
        return {}
    return payload


def _report_id() -> str | None:
    try:
        payload = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload.get("report_id") if isinstance(payload, Mapping) else None


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Object Page Contract validation",
        f"status: {report['status']}",
        f"contract_file: {report.get('contract_file')}",
        f"report_id: {report.get('report_id')}",
        f"example_count: {report.get('example_count')}",
    ]
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = validate_object_page_contract()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
