#!/usr/bin/env python3
"""Validate Public Query Observation Runtime Planning v0 artifacts."""

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "public-query-observation-runtime-planning-v0"
REPORT_PATH = AUDIT_DIR / "public_query_observation_runtime_planning_report.json"
INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "query_intelligence" / "public_query_observation_runtime_plan.json"
DOC_PATH = REPO_ROOT / "docs" / "operations" / "PUBLIC_QUERY_OBSERVATION_RUNTIME_PLAN.md"
REQUIRED_FILES = {
    "README.md",
    "PLANNING_SUMMARY.md",
    "READINESS_DECISION.md",
    "HOSTED_DEPLOYMENT_GATE_REVIEW.md",
    "QUERY_OBSERVATION_CONTRACT_REVIEW.md",
    "PRIVACY_AND_POISONING_GUARD_REVIEW.md",
    "RUNTIME_BOUNDARY.md",
    "STORAGE_AND_RETENTION_PLAN.md",
    "OBSERVATION_EVENT_FLOW.md",
    "SAFE_FIELD_MODEL.md",
    "REDACTION_AND_REJECTION_MODEL.md",
    "AGGREGATION_ELIGIBILITY_MODEL.md",
    "RESULT_CACHE_MISS_LEDGER_SEARCH_NEED_RELATIONSHIP.md",
    "DEMAND_DASHBOARD_RELATIONSHIP.md",
    "PUBLIC_SEARCH_INTEGRATION_PLAN.md",
    "ABUSE_RATE_LIMIT_AND_FAILURE_MODEL.md",
    "SECURITY_PRIVACY_RIGHTS_OPS_REVIEW.md",
    "IMPLEMENTATION_PHASES.md",
    "ACCEPTANCE_CRITERIA.md",
    "DO_NOT_IMPLEMENT_YET.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "public_query_observation_runtime_planning_report.json",
}
VALID_READINESS = {
    "ready_for_runtime_implementation_after_operator_approval",
    "ready_for_local_prototype_only",
    "blocked_hosted_deployment_unverified",
    "blocked_public_search_safety_failed",
    "blocked_privacy_policy_incomplete",
    "blocked_query_guard_missing",
    "blocked_storage_policy_incomplete",
    "blocked_retention_policy_incomplete",
    "blocked_other",
}
REPORT_FALSE_FIELDS = {
    "runtime_query_observation_implemented",
    "persistent_observation_store_implemented",
    "hosted_runtime_enabled",
    "telemetry_implemented",
    "raw_query_retention_enabled",
    "ip_tracking_enabled",
    "account_tracking_enabled",
    "user_profile_tracking_enabled",
    "public_aggregate_enabled",
    "public_search_runtime_mutated",
    "master_index_mutated",
    "public_index_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "live_source_called",
    "external_calls_performed",
}
INVENTORY_FALSE_FIELDS = {
    "runtime_query_observation_implemented",
    "persistent_observation_store_implemented",
    "hosted_runtime_enabled",
    "telemetry_implemented",
    "raw_query_retention_enabled",
    "ip_tracking_enabled",
    "account_tracking_enabled",
    "user_profile_tracking_enabled",
    "public_aggregate_enabled",
    "master_index_mutation_allowed",
    "public_index_mutation_allowed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
}
INVENTORY_TRUE_FIELDS = {
    "query_guard_required",
    "privacy_filter_required",
    "poisoning_filter_required",
    "hosted_deployment_required",
    "rate_limit_required",
    "retention_policy_required",
    "operator_approval_required",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_false(data: Mapping[str, Any], fields: set[str], prefix: str, errors: list[str]) -> None:
    for field in sorted(fields):
        if data.get(field) is not False:
            errors.append(f"{prefix}.{field} must be false")


def validate() -> list[str]:
    errors: list[str] = []
    if not AUDIT_DIR.exists():
        errors.append(f"missing audit directory: {AUDIT_DIR.relative_to(REPO_ROOT)}")
    else:
        missing = sorted(name for name in REQUIRED_FILES if not (AUDIT_DIR / name).exists())
        if missing:
            errors.append(f"audit pack missing files: {', '.join(missing)}")
    for path in (REPORT_PATH, INVENTORY_PATH, DOC_PATH):
        if not path.exists():
            errors.append(f"missing required artifact: {path.relative_to(REPO_ROOT)}")
    report: Mapping[str, Any] = {}
    inventory: Mapping[str, Any] = {}
    if REPORT_PATH.exists():
        loaded = load_json(REPORT_PATH)
        if not isinstance(loaded, Mapping):
            errors.append("report JSON must be an object")
        else:
            report = loaded
            if report.get("readiness_decision") not in VALID_READINESS:
                errors.append("report.readiness_decision is invalid")
            check_false(report, REPORT_FALSE_FIELDS, "report", errors)
            if report.get("hosted_deployment_gate", {}).get("decision") != "runtime_blocked":
                errors.append("hosted deployment gate must keep runtime_blocked")
            if not report.get("safe_field_model"):
                errors.append("report.safe_field_model must be present")
            if not report.get("forbidden_field_model"):
                errors.append("report.forbidden_field_model must be present")
            acceptance_text = " ".join(str(item).lower() for item in report.get("acceptance_criteria", []))
            for phrase in ("hosted", "rate-limit", "privacy/poisoning", "retention", "operator approval"):
                if phrase not in acceptance_text:
                    errors.append(f"acceptance criteria missing {phrase}")
    if INVENTORY_PATH.exists():
        loaded = load_json(INVENTORY_PATH)
        if not isinstance(loaded, Mapping):
            errors.append("inventory JSON must be an object")
        else:
            inventory = loaded
            if inventory.get("status") != "planning_only":
                errors.append("inventory.status must be planning_only")
            check_false(inventory, INVENTORY_FALSE_FIELDS, "inventory", errors)
            for field in sorted(INVENTORY_TRUE_FIELDS):
                if inventory.get(field) is not True:
                    errors.append(f"inventory.{field} must be true")
    if AUDIT_DIR.exists():
        safe_text = (AUDIT_DIR / "SAFE_FIELD_MODEL.md").read_text(encoding="utf-8").lower()
        for phrase in ("normalized_query_fingerprint", "ip address", "account id", "private path", "secret/token/api key"):
            if phrase not in safe_text:
                errors.append(f"safe field model missing {phrase}")
        acceptance = (AUDIT_DIR / "ACCEPTANCE_CRITERIA.md").read_text(encoding="utf-8").lower()
        for phrase in ("hosted backend verified", "rate-limit evidence", "privacy/poisoning guard", "retention/deletion", "operator approval"):
            if phrase not in acceptance:
                errors.append(f"acceptance criteria doc missing {phrase}")
        do_not = (AUDIT_DIR / "DO_NOT_IMPLEMENT_YET.md").read_text(encoding="utf-8").lower()
        for phrase in ("no runtime observation writes", "no telemetry", "no raw query logging", "no index mutation"):
            if phrase not in do_not:
                errors.append(f"do-not-implement doc missing {phrase}")
    if DOC_PATH.exists():
        text = DOC_PATH.read_text(encoding="utf-8").lower()
        for phrase in ("planning", "no raw query", "no telemetry", "hosted deployment gate", "disabled-by-default", "no ip/account tracking"):
            if phrase not in text:
                errors.append(f"operations doc missing {phrase}")
    return errors


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    errors = validate()
    status = "invalid" if errors else "valid"
    if args.json:
        payload = {
            "status": status,
            "report_id": "public_query_observation_runtime_planning_v0",
            "readiness_decision": None,
            "audit_dir": str(AUDIT_DIR.relative_to(REPO_ROOT)),
            "errors": errors,
        }
        if REPORT_PATH.exists():
            try:
                payload["readiness_decision"] = load_json(REPORT_PATH).get("readiness_decision")
            except Exception:
                payload["readiness_decision"] = None
        print(json.dumps(payload, indent=2), file=stdout)
    else:
        print(f"status: {status}", file=stdout)
        for error in errors:
            print(f"ERROR: {error}", file=stdout)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
