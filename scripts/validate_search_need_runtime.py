#!/usr/bin/env python3
"""Validate Track B SearchNeed runtime artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_foundry import search_need as runtime  # noqa: E402


RUNTIME_POLICY_PATH = "control/inventory/observations/search_need_runtime_policy.json"
STATUS_POLICY_PATH = "control/inventory/observations/search_need_status_policy.json"
INTENT_POLICY_PATH = "control/inventory/observations/search_need_intent_policy.json"
OUTPUT_POLICY_PATH = "control/inventory/observations/search_need_output_policy.json"
REVIEW_POLICY_PATH = "control/inventory/observations/search_need_review_policy.json"
AUDIT_REPORT_PATH = "control/audits/track-b-09-search-need-runtime-v0/track_b_09_report.json"
SAMPLE_REPORT_PATH = "control/audits/track-b-09-search-need-runtime-v0/generated/sample_search_need_report.json"
SAMPLE_SUMMARY_PATH = "control/audits/track-b-09-search-need-runtime-v0/generated/sample_search_need_summary.md"
EXAMPLE_ROOT = "examples/search_needs"
DOC_PATHS = (
    "docs/reference/SEARCH_NEED_RUNTIME.md",
    "docs/architecture/SEARCH_NEED_MODEL.md",
    "docs/operations/SEARCH_NEED_REVIEW.md",
)
REQUIRED_EXAMPLES = {
    "minimal_search_need_v0.json",
    "software_version_search_need_v0.json",
    "driver_search_need_v0.json",
    "article_member_search_need_v0.json",
    "policy_blocked_search_need_v0.json",
    "not_evaluable_search_need_v0.json",
}
POLICY_FALSE_FIELDS = {
    "implemented_public_telemetry",
    "changed_public_search_behavior",
    "created_local_private_state",
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
    "enabled_model_provider_calls",
    "mutated_master_index",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
}
FORBIDDEN_STRING_CLAIMS = {
    "whole web was searched",
    "archive universe was searched",
    "requested object does not exist globally",
    "object does not exist",
    "globally absent",
    "global absence proof",
    "telemetry enabled",
    "hosted query capture enabled",
    "public search behavior changed",
    "source sync enabled",
    "download enabled",
    "upload enabled",
    "account enabled",
    "master-index mutation allowed",
    "rights clearance confirmed",
    "malware safe",
    "verified installability",
    "production readiness",
}


def validate_search_need_runtime(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []

    required_files = [
        RUNTIME_POLICY_PATH,
        STATUS_POLICY_PATH,
        INTENT_POLICY_PATH,
        OUTPUT_POLICY_PATH,
        REVIEW_POLICY_PATH,
        AUDIT_REPORT_PATH,
        SAMPLE_REPORT_PATH,
        SAMPLE_SUMMARY_PATH,
        "runtime/local_foundry/search_need.py",
        "scripts/record_search_need.py",
        *DOC_PATHS,
    ]
    for path in required_files:
        if not (repo_root / path).is_file():
            errors.append(f"missing required file: {path}")

    if errors:
        return _report(errors)

    runtime_policy = _read_json(repo_root / RUNTIME_POLICY_PATH)
    status_policy = _read_json(repo_root / STATUS_POLICY_PATH)
    intent_policy = _read_json(repo_root / INTENT_POLICY_PATH)
    output_policy = _read_json(repo_root / OUTPUT_POLICY_PATH)
    review_policy = _read_json(repo_root / REVIEW_POLICY_PATH)
    audit_report = _read_json(repo_root / AUDIT_REPORT_PATH)
    sample_report = _read_json(repo_root / SAMPLE_REPORT_PATH)

    errors.extend(validate_runtime_policy(runtime_policy, RUNTIME_POLICY_PATH))
    errors.extend(validate_status_policy(status_policy, STATUS_POLICY_PATH))
    errors.extend(validate_intent_policy(intent_policy, INTENT_POLICY_PATH))
    errors.extend(validate_output_policy(output_policy, OUTPUT_POLICY_PATH))
    errors.extend(validate_review_policy(review_policy, REVIEW_POLICY_PATH))
    errors.extend(validate_audit_report(audit_report, AUDIT_REPORT_PATH))
    errors.extend(validate_docs(repo_root))

    example_paths = sorted((repo_root / EXAMPLE_ROOT).glob("*.json"))
    found = {path.name for path in example_paths}
    missing_examples = sorted(REQUIRED_EXAMPLES - found)
    if missing_examples:
        errors.append(f"{EXAMPLE_ROOT}: missing examples {missing_examples}")
    for path in example_paths:
        ref = path.relative_to(repo_root).as_posix()
        payload = _read_json(path)
        record = runtime.build_search_need_from_search_miss(payload)
        errors.extend(f"{ref}: {error}" for error in runtime.validate_search_need(record))
        errors.extend(_scan_for_forbidden_claims(payload, ref))

    errors.extend(validate_sample_report(sample_report, SAMPLE_REPORT_PATH))
    errors.extend(validate_script_check(repo_root))
    errors.extend(validate_forbidden_output_root_rejected(repo_root))

    overclaim = runtime.build_search_need_from_search_miss(
        {
            "query_text": "legacy package",
            "query_source": "explicit_test_fixture",
            "result_count": 0,
            "result_quality": "empty",
            "failure_modes": ["empty_result"],
            "notes": ["whole web was searched"],
        }
    )
    if not runtime.detect_exhaustive_absence_overclaim(overclaim):
        errors.append("synthetic exhaustive absence overclaim was not detected")

    risky = runtime.build_search_need_from_search_miss(
        {
            "query_text": "https://example.invalid live_probe force rank source",
            "query_source": "explicit_test_fixture",
            "result_count": 0,
            "result_quality": "empty",
            "first_useful_result_rank": None,
            "failure_modes": ["empty_result"],
        }
    )
    risk_flags = set(risky["poisoning_guard_posture"]["risk_flags"])
    for expected in ("url_injection", "unsupported_live_probe_request", "result_rank_manipulation_attempt"):
        if expected not in risk_flags:
            errors.append(f"synthetic poisoning guard did not flag {expected}")

    return _report(errors)


def validate_runtime_policy(policy: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "search_need_runtime_policy.v0":
        errors.append(f"{path}: unexpected schema_version")
    errors.extend(_require_values(path, "allowed_input_types", policy, runtime.ALLOWED_INPUT_TYPES))
    errors.extend(_require_values(path, "allowed_statuses", policy, runtime.ALLOWED_STATUSES))
    errors.extend(_require_values(path, "current_allowed_statuses", policy, runtime.CURRENT_ALLOWED_STATUSES))
    errors.extend(_require_values(path, "allowed_need_intents", policy, runtime.ALLOWED_NEED_INTENTS))
    errors.extend(_require_values(path, "allowed_output_types", policy, runtime.ALLOWED_OUTPUT_TYPES))
    errors.extend(_require_values(path, "forbidden_output_types", policy, runtime.FORBIDDEN_OUTPUT_TYPES))
    if policy.get("review_required_before_downstream_use") is not True:
        errors.append(f"{path}: review_required_before_downstream_use must be true")
    truth = policy.get("truth_boundary", {})
    for key in ("search_need_is_public_truth", "search_need_is_accepted_evidence", "search_need_can_mutate_master_index", "search_need_is_exhaustive_global_absence"):
        if truth.get(key) is not False:
            errors.append(f"{path}: truth_boundary.{key} must be false")
    if truth.get("human_review_required_for_downstream_use") is not True:
        errors.append(f"{path}: truth_boundary.human_review_required_for_downstream_use must be true")
    errors.extend(_check_false_map(path, policy.get("product_boundary", {}), POLICY_FALSE_FIELDS, "product_boundary"))
    return errors


def validate_status_policy(policy: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "search_need_status_policy.v0":
        errors.append(f"{path}: unexpected schema_version")
    errors.extend(_require_values(path, "allowed_statuses", policy, runtime.ALLOWED_STATUSES))
    if "statuses_requiring_review" not in policy:
        errors.append(f"{path}: missing statuses_requiring_review")
    if "no_exhaustive_absence_rules" not in policy:
        errors.append(f"{path}: missing no_exhaustive_absence_rules")
    return errors


def validate_intent_policy(policy: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "search_need_intent_policy.v0":
        errors.append(f"{path}: unexpected schema_version")
    errors.extend(_require_values(path, "allowed_need_intents", policy, runtime.ALLOWED_NEED_INTENTS))
    for intent in ("find_software", "find_exact_version", "find_driver", "find_article_inside_scan", "policy_review"):
        if intent not in policy.get("intent_meanings", {}):
            errors.append(f"{path}: missing intent meaning for {intent}")
    return errors


def validate_output_policy(policy: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "search_need_output_policy.v0":
        errors.append(f"{path}: unexpected schema_version")
    errors.extend(_require_values(path, "allowed_output_types", policy, runtime.ALLOWED_OUTPUT_TYPES))
    errors.extend(_require_values(path, "forbidden_output_types", policy, runtime.FORBIDDEN_OUTPUT_TYPES))
    rules = policy.get("output_rules", {})
    if rules.get("review_required_before_downstream_use") is not True:
        errors.append(f"{path}: output_rules.review_required_before_downstream_use must be true")
    for key in (
        "automatic_public_use_allowed",
        "automatic_master_index_mutation_allowed",
        "automatic_evidence_acceptance_allowed",
        "automatic_workunit_seed_allowed",
        "automatic_source_lead_allowed",
        "automatic_candidate_review_seed_allowed",
    ):
        if rules.get(key) is not False:
            errors.append(f"{path}: output_rules.{key} must be false")
    errors.extend(_check_false_map(path, policy.get("product_boundary", {}), POLICY_FALSE_FIELDS, "product_boundary"))
    return errors


def validate_review_policy(policy: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "search_need_review_policy.v0":
        errors.append(f"{path}: unexpected schema_version")
    for key in (
        "review_required_before_workunit_seed",
        "review_required_before_source_lead",
        "review_required_before_candidate_review_seed",
        "review_required_before_public_surface",
        "review_required_before_master_index",
    ):
        if policy.get(key) is not True:
            errors.append(f"{path}: {key} must be true")
    for key in ("automatic_public_use_allowed", "automatic_master_index_mutation_allowed"):
        if policy.get(key) is not False:
            errors.append(f"{path}: {key} must be false")
    return errors


def validate_audit_report(report: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != "track_b_09_report.v0":
        errors.append(f"{path}: unexpected schema_version")
    scope = report.get("runtime_scope", {})
    for key in ("explicit_input_only", "local_only", "writes_no_files_by_default"):
        if scope.get(key) is not True:
            errors.append(f"{path}: runtime_scope.{key} must be true")
    for key in ("public_telemetry_enabled", "raw_public_query_logging_enabled"):
        if scope.get(key) is not False:
            errors.append(f"{path}: runtime_scope.{key} must be false")
    truth = report.get("truth_boundary", {})
    for key in ("search_need_is_public_truth", "search_need_is_accepted_evidence", "search_need_can_mutate_master_index", "search_need_is_exhaustive_global_absence"):
        if truth.get(key) is not False:
            errors.append(f"{path}: truth_boundary.{key} must be false")
    errors.extend(_check_false_map(path, report.get("product_boundary", {}), POLICY_FALSE_FIELDS, "product_boundary"))
    return errors


def validate_sample_report(report: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != runtime.REPORT_SCHEMA_VERSION:
        errors.append(f"{path}: unexpected schema_version")
    if report.get("status") != "pass":
        errors.append(f"{path}: status must be pass")
    record = report.get("record")
    if not isinstance(record, Mapping):
        errors.append(f"{path}: record must be an object")
    else:
        errors.extend(f"{path}: {error}" for error in runtime.validate_search_need(record))
    errors.extend(_check_false_map(path, report.get("product_boundary", {}), POLICY_FALSE_FIELDS, "product_boundary"))
    return errors


def validate_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for doc in DOC_PATHS:
        text = (repo_root / doc).read_text(encoding="utf-8").casefold()
        for phrase in ("searchneed", "telemetry", "poisoning", "master-index"):
            if phrase not in text:
                errors.append(f"{doc}: missing phrase {phrase}")
    return errors


def validate_script_check(repo_root: Path) -> list[str]:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/record_search_need.py",
            "--input",
            "examples/search_misses/empty_result_search_miss_v0.json",
            "--check",
            "--json",
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        return [f"record_search_need --check failed: {completed.stderr.strip()}"]
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return [f"record_search_need --check did not emit JSON: {exc}"]
    if payload.get("status") != "pass":
        return ["record_search_need --check returned non-pass report"]
    return []


def validate_forbidden_output_root_rejected(repo_root: Path) -> list[str]:
    forbidden = repo_root / "runtime" / "__search_need_forbidden_report.json"
    if forbidden.exists():
        return [f"forbidden test path unexpectedly exists before validation: {forbidden}"]
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/record_search_need.py",
            "--input",
            "examples/search_misses/empty_result_search_miss_v0.json",
            "--output",
            str(forbidden),
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
    )
    if completed.returncode == 0:
        return ["record_search_need allowed forbidden runtime output path"]
    if forbidden.exists():
        return ["record_search_need created forbidden runtime output path"]
    return []


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_values(path: str, field: str, data: Mapping[str, Any], expected: Iterable[str]) -> list[str]:
    actual = set(data.get(field, []))
    missing = sorted(set(expected) - actual)
    return [f"{path}: {field} missing {missing}"] if missing else []


def _check_false_map(path: str, data: Any, fields: Iterable[str], label: str) -> list[str]:
    if not isinstance(data, Mapping):
        return [f"{path}: {label} must be an object"]
    return [f"{path}: {label}.{field} must be false" for field in sorted(fields) if data.get(field) is not False]


def _scan_for_forbidden_claims(value: Any, path: str) -> list[str]:
    errors: list[str] = []
    for key_path, text in _walk_strings(value):
        lowered = text.casefold()
        for phrase in sorted(FORBIDDEN_STRING_CLAIMS):
            if phrase in lowered:
                errors.append(f"{path}: forbidden claim phrase {phrase!r} in {key_path}")
    return errors


def _walk_strings(value: Any, prefix: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield prefix, value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk_strings(child, f"{prefix}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_strings(child, f"{prefix}[{index}]")


def _report(errors: Sequence[str]) -> dict[str, Any]:
    sorted_errors = sorted(errors)
    return {
        "status": "invalid" if sorted_errors else "valid",
        "errors": sorted_errors,
        "checked": {
            "policies": sorted([RUNTIME_POLICY_PATH, STATUS_POLICY_PATH, INTENT_POLICY_PATH, OUTPUT_POLICY_PATH, REVIEW_POLICY_PATH]),
            "examples": EXAMPLE_ROOT,
            "sample_report": SAMPLE_REPORT_PATH,
        },
    }


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(argv)

    report = validate_search_need_runtime(REPO_ROOT)
    if args.json:
        stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    elif report["status"] == "valid":
        stdout.write("SearchNeed runtime validation: PASS\n")
    else:
        stdout.write("SearchNeed runtime validation: FAIL\n")
        for error in report["errors"]:
            stdout.write(f"- {error}\n")
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
