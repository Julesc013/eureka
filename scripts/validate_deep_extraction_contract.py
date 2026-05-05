from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CONTRACTS = [
    "contracts/extraction/deep_extraction_request.v0.json",
    "contracts/extraction/extraction_result_summary.v0.json",
    "contracts/extraction/extraction_policy.v0.json",
    "contracts/extraction/extraction_member.v0.json",
]
AUDIT_REQUIRED = [
    "README.md",
    "CONTRACT_SUMMARY.md",
    "DEEP_EXTRACTION_REQUEST_SCHEMA.md",
    "EXTRACTION_RESULT_SUMMARY_SCHEMA.md",
    "EXTRACTION_POLICY_SCHEMA.md",
    "EXTRACTION_TIER_TAXONOMY.md",
    "CONTAINER_AND_MEMBER_MODEL.md",
    "MANIFEST_AND_METADATA_EXTRACTION_MODEL.md",
    "SELECTIVE_TEXT_EXTRACTION_MODEL.md",
    "OCR_AND_TRANSCRIPTION_HOOK_MODEL.md",
    "PACKAGE_ARCHIVE_ISO_WARC_WACZ_SOURCE_BUNDLE_MODEL.md",
    "NESTED_RECURSION_AND_DEPTH_LIMIT_MODEL.md",
    "SANDBOX_AND_RESOURCE_LIMIT_MODEL.md",
    "PRIVACY_PATH_AND_SECRET_POLICY.md",
    "EXECUTABLE_PAYLOAD_RISK_POLICY.md",
    "RIGHTS_RISK_AND_PROVENANCE_POLICY.md",
    "SYNTHETIC_RECORD_GENERATION_BOUNDARY.md",
    "SOURCE_CACHE_EVIDENCE_CANDIDATE_RELATIONSHIP.md",
    "PUBLIC_SEARCH_OBJECT_PAGE_RESULT_EXPLANATION_RELATIONSHIP.md",
    "NO_RUNTIME_AND_NO_MUTATION_POLICY.md",
    "EXAMPLE_DEEP_EXTRACTION_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "deep_extraction_contract_report.json",
]
EXAMPLES = [
    "minimal_archive_member_listing_v0",
    "minimal_iso_manifest_summary_v0",
    "minimal_warc_wacz_capture_listing_v0",
    "minimal_package_metadata_summary_v0",
    "minimal_scanned_volume_ocr_hook_v0",
    "minimal_nested_container_limit_v0",
    "minimal_executable_payload_risk_v0",
]
REPORT_HARD_FALSE = [
    "runtime_extraction_implemented",
    "extraction_executed",
    "files_opened",
    "archive_unpacked",
    "payload_executed",
    "installer_executed",
    "package_manager_invoked",
    "emulator_vm_launched",
    "OCR_performed",
    "transcription_performed",
    "live_source_called",
    "external_calls_performed",
    "URL_fetched",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "accepted_as_truth",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "telemetry_enabled",
]
INVENTORY_FALSE = [
    "runtime_extraction_implemented",
    "extraction_queue_implemented",
    "extraction_store_implemented",
    "sandbox_runtime_implemented",
    "OCR_runtime_implemented",
    "transcription_runtime_implemented",
    "recursive_extraction_enabled",
    "arbitrary_local_path_enabled",
    "arbitrary_url_fetch_enabled",
    "payload_execution_enabled",
    "installer_execution_enabled",
    "package_manager_invocation_enabled",
    "emulator_vm_launch_enabled",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "public_index_mutation_allowed",
    "master_index_mutation_allowed",
]
INVENTORY_TRUE = [
    "privacy_path_secret_policy_required",
    "executable_payload_policy_required",
    "sandbox_required_before_runtime",
    "resource_limits_required_before_runtime",
    "operator_approval_required",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_validator(args: list[str]) -> None:
    result = subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        raise AssertionError(f"{' '.join(args)} failed: {result.stdout} {result.stderr}")


def validate() -> list[str]:
    checked: list[str] = []
    for rel in CONTRACTS:
        path = ROOT / rel
        if not path.exists():
            raise AssertionError(f"missing contract {rel}")
        load(path)
        checked.append(rel)
    inventory = ROOT / "control/inventory/extraction/deep_extraction_policy.json"
    if not inventory.exists():
        raise AssertionError("missing extraction inventory")
    inventory_data = load(inventory)
    if inventory_data.get("status") != "contract_only":
        raise AssertionError("inventory status must be contract_only")
    for key in INVENTORY_FALSE:
        if inventory_data.get(key) is not False:
            raise AssertionError(f"inventory {key} must be false")
    for key in INVENTORY_TRUE:
        if inventory_data.get(key) is not True:
            raise AssertionError(f"inventory {key} must be true")
    checked.append(str(inventory.relative_to(ROOT)))
    audit = ROOT / "control/audits/deep-extraction-contract-v0"
    for name in AUDIT_REQUIRED:
        path = audit / name
        if not path.exists():
            raise AssertionError(f"missing audit file {name}")
        checked.append(str(path.relative_to(ROOT)))
    report = load(audit / "deep_extraction_contract_report.json")
    for key in REPORT_HARD_FALSE:
        if report.get(key) is not False:
            raise AssertionError(f"report {key} must be false")
    for root_name in EXAMPLES:
        root = ROOT / "examples/extraction" / root_name
        for name in ("DEEP_EXTRACTION_REQUEST.json", "EXTRACTION_RESULT_SUMMARY.json", "EXTRACTION_POLICY.json", "README.md", "CHECKSUMS.SHA256"):
            path = root / name
            if not path.exists():
                raise AssertionError(f"missing example file {path}")
        checked.append(str(root.relative_to(ROOT)))
    run_validator(["scripts/validate_deep_extraction_request.py", "--all-examples"])
    run_validator(["scripts/validate_extraction_result_summary.py", "--all-examples"])
    docs = [
        ROOT / "docs/reference/DEEP_EXTRACTION_CONTRACT.md",
        audit / "EXTRACTION_TIER_TAXONOMY.md",
        audit / "CONTAINER_AND_MEMBER_MODEL.md",
        audit / "MANIFEST_AND_METADATA_EXTRACTION_MODEL.md",
        audit / "SELECTIVE_TEXT_EXTRACTION_MODEL.md",
        audit / "OCR_AND_TRANSCRIPTION_HOOK_MODEL.md",
        audit / "SANDBOX_AND_RESOURCE_LIMIT_MODEL.md",
        audit / "PRIVACY_PATH_AND_SECRET_POLICY.md",
        audit / "EXECUTABLE_PAYLOAD_RISK_POLICY.md",
        audit / "SYNTHETIC_RECORD_GENERATION_BOUNDARY.md",
        audit / "NO_RUNTIME_AND_NO_MUTATION_POLICY.md",
    ]
    required_phrases = [
        "contract-only",
        "no extraction runtime",
        "no runtime",
        "no mutation",
        "no OCR",
        "no transcription",
        "no execution",
        "source cache",
        "evidence ledger",
        "candidate",
    ]
    combined_text = "\n".join(path.read_text(encoding="utf-8").lower() for path in docs)
    for phrase in required_phrases:
        if phrase.lower() not in combined_text:
            raise AssertionError(f"deep extraction docs: missing phrase {phrase}")
    for path in docs:
        checked.append(str(path.relative_to(ROOT)))
    return checked


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Deep Extraction Contract v0.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    checked: list[str] = []
    try:
        checked = validate()
    except Exception as exc:
        errors.append(str(exc))
    if args.json:
        print(json.dumps({"ok": not errors, "checked": checked, "error_count": len(errors), "errors": errors}, indent=2, sort_keys=True))
    elif errors:
        for error in errors:
            print(error, file=sys.stderr)
    else:
        print(f"deep extraction contract validation passed: {len(checked)} item(s)")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
