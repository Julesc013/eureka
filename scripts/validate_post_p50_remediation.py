#!/usr/bin/env python3
"""Validate the Post-P50 Remediation Pack v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = ROOT / "control" / "audits" / "post-p50-remediation-v0"
REPORT_PATH = AUDIT_ROOT / "post_p50_remediation_report.json"
P50_REPORT = ROOT / "control" / "audits" / "post-p49-platform-audit-v0" / "post_p49_platform_audit_report.json"

REQUIRED_FILES = [
    "README.md",
    "REMEDIATION_SUMMARY.md",
    "P50_FINDINGS_REVIEW.md",
    "FIXED_ITEMS.md",
    "UNFIXED_OR_OPERATOR_GATED_ITEMS.md",
    "GOVERNANCE_DOCS_STATUS.md",
    "PACK_VALIDATOR_CLI_REMEDIATION.md",
    "GITHUB_PAGES_REMEDIATION_STATUS.md",
    "COMMAND_MATRIX_REMEDIATION.md",
    "TEST_REGISTRY_REMEDIATION.md",
    "GENERATED_ARTIFACT_RECHECK.md",
    "SECURITY_PRIVACY_RIGHTS_REMEDIATION.md",
    "CARGO_AND_RUST_STATUS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_BRANCH_RECOMMENDATION.md",
    "COMMAND_RESULTS.md",
    "post_p50_remediation_report.json",
]

REQUIRED_KEYS = [
    "report_id",
    "created_by_slice",
    "repo_head_before",
    "repo_head_after",
    "branch",
    "worktree_status",
    "p50_audit_ref",
    "p50_findings_reviewed",
    "remediation_items",
    "governance_docs_status",
    "pack_validator_cli_status",
    "github_pages_status",
    "command_matrix_status",
    "generated_artifact_status",
    "cargo_status",
    "security_privacy_rights_status",
    "command_results",
    "remaining_blockers",
    "human_operated_work",
    "approval_gated_work",
    "operator_gated_work",
    "recommended_next_branch",
    "next_milestones",
    "do_not_do_next",
    "notes",
]

REQUIRED_ITEM_IDS = {
    "p51-root-contributing",
    "p51-root-security",
    "p51-root-code-of-conduct",
    "p51-license-selection",
    "p51-pack-validator-cli-drift",
    "p51-github-pages-evidence",
    "p51-command-matrix-drift",
    "p51-test-registry-drift",
    "p51-generated-artifact-recheck",
    "p51-cargo-unavailable",
    "p51-security-privacy-rights-ops-gap",
}

ALLOWED_STATUSES = {
    "fixed",
    "partially_fixed",
    "operator_gated",
    "human_pending",
    "deferred",
    "blocked",
}

FORBIDDEN_POSITIVE_CLAIMS = [
    "production ready: true",
    "production_ready\": true",
    "github pages deployment succeeded",
    "deployment_verified\": true",
    "deployment_success_claim\": true",
    "hosted backend is implemented",
    "hosted public search is available",
    "hosted search is live",
    "live probes enabled",
    "live probe runtime is implemented",
    "ai runtime is implemented",
    "model calls are enabled",
    "pack import runtime is implemented",
    "staging runtime is implemented",
]


def _load_report(errors: list[str]) -> dict[str, Any]:
    if not REPORT_PATH.exists():
        errors.append("post_p50_remediation_report.json missing")
        return {}
    try:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"post_p50_remediation_report.json did not parse: {exc.msg}")
        return {}
    if not isinstance(report, dict):
        errors.append("post_p50_remediation_report.json must contain an object")
        return {}
    return report


def _audit_text() -> str:
    if not AUDIT_ROOT.exists():
        return ""
    parts: list[str] = []
    for path in AUDIT_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt"}:
            parts.append(path.read_text(encoding="utf-8").lower())
    return "\n".join(parts)


def validate() -> dict[str, Any]:
    errors: list[str] = []

    if not AUDIT_ROOT.exists():
        errors.append(f"audit pack missing: {AUDIT_ROOT.relative_to(ROOT)}")
    else:
        for name in REQUIRED_FILES:
            if not (AUDIT_ROOT / name).exists():
                errors.append(f"required audit file missing: {name}")

    if not P50_REPORT.exists():
        errors.append("P50 audit reference is missing")

    report = _load_report(errors)
    if report:
        for key in REQUIRED_KEYS:
            if key not in report:
                errors.append(f"report missing top-level key: {key}")

        p50_ref = report.get("p50_audit_ref")
        if p50_ref != "control/audits/post-p49-platform-audit-v0/post_p49_platform_audit_report.json":
            errors.append("p50_audit_ref must point at the P50 JSON report")

        items = report.get("remediation_items")
        if not isinstance(items, list) or not items:
            errors.append("remediation_items must be a non-empty list")
            items = []
        found_ids = set()
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"remediation_items[{index}] must be an object")
                continue
            item_id = item.get("item_id")
            if isinstance(item_id, str):
                found_ids.add(item_id)
            else:
                errors.append(f"remediation_items[{index}].item_id must be a string")
            for key in ["fixed", "remaining_status"]:
                if item.get(key) not in ALLOWED_STATUSES:
                    errors.append(f"{item_id or index}.{key} has invalid status: {item.get(key)!r}")
        missing = sorted(REQUIRED_ITEM_IDS - found_ids)
        if missing:
            errors.append("missing remediation item IDs: " + ", ".join(missing))

        governance = report.get("governance_docs_status", {})
        if not isinstance(governance, dict):
            errors.append("governance_docs_status must be an object")
        else:
            for key in ["contributing", "security", "code_of_conduct", "license"]:
                if key not in governance:
                    errors.append(f"governance_docs_status missing {key}")
            if governance.get("license") != "not_selected_no_root_license_added":
                errors.append("license status must record no selected root license")

        if (ROOT / "LICENSE").exists():
            errors.append("root LICENSE exists even though the report records license selection pending")
        for root_doc in ["CONTRIBUTING.md", "SECURITY.md", "CODE_OF_CONDUCT.md"]:
            if not (ROOT / root_doc).exists():
                errors.append(f"root governance document missing: {root_doc}")

        pack_cli = report.get("pack_validator_cli_status", {})
        if not isinstance(pack_cli, dict) or pack_cli.get("individual_all_examples") != "fixed":
            errors.append("pack_validator_cli_status must record individual_all_examples fixed")
        if isinstance(pack_cli, dict) and pack_cli.get("mutation_behavior_added") is not False:
            errors.append("pack_validator_cli_status must record no mutation behavior added")

        pages = report.get("github_pages_status", {})
        if not isinstance(pages, dict):
            errors.append("github_pages_status must be an object")
        else:
            if pages.get("deployment_verified") is not False:
                errors.append("github_pages_status must record deployment_verified false")
            if pages.get("deployment_success_claim") is not False:
                errors.append("github_pages_status must not claim deployment success")

        cargo = report.get("cargo_status", {})
        if not isinstance(cargo, dict) or cargo.get("cargo_available") is not False:
            errors.append("cargo_status must record cargo_available false in this environment")
        if isinstance(cargo, dict) and cargo.get("rust_runtime_wiring") is not False:
            errors.append("cargo_status must record rust_runtime_wiring false")

        for list_key in [
            "command_results",
            "remaining_blockers",
            "human_operated_work",
            "approval_gated_work",
            "operator_gated_work",
            "next_milestones",
            "do_not_do_next",
        ]:
            if not isinstance(report.get(list_key), list) or not report.get(list_key):
                errors.append(f"{list_key} must be a non-empty list")

        if not isinstance(report.get("recommended_next_branch"), str) or not report.get("recommended_next_branch"):
            errors.append("recommended_next_branch must be a non-empty string")

    text = _audit_text()
    for phrase in FORBIDDEN_POSITIVE_CLAIMS:
        if phrase in text:
            errors.append(f"forbidden product/deployment claim found: {phrase}")

    return {
        "check_id": "post_p50_remediation_v0",
        "audit_root": str(AUDIT_ROOT.relative_to(ROOT)),
        "required_file_count": len(REQUIRED_FILES),
        "required_item_count": len(REQUIRED_ITEM_IDS),
        "allowed_statuses": sorted(ALLOWED_STATUSES),
        "errors": errors,
        "status": "passed" if not errors else "failed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable validation result.")
    args = parser.parse_args()

    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["status"] == "passed":
        print(
            "post-p50 remediation validation passed: "
            f"{result['required_file_count']} required files checked"
        )
    else:
        print("post-p50 remediation validation failed:")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
