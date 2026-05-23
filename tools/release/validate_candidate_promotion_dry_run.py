#!/usr/bin/env python3
"""Validate the candidate promotion dry-run milestone."""

from __future__ import annotations

from copy import deepcopy
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.foundry import candidate_promotion_dry_run as promotion
from scripts import run_candidate_promotion_dry_run


POLICY_FILES = [
    "control/inventory/review/candidate_promotion_dry_run_policy.json",
    "control/inventory/review/candidate_promotion_readiness_policy.json",
    "control/inventory/review/candidate_promotion_blocker_policy.json",
    "control/inventory/review/candidate_promotion_output_policy.json",
    "control/inventory/review/candidate_promotion_path_policy.json",
    "control/inventory/review/candidate_promotion_truth_policy.json",
]

DOC_FILES = [
    "docs/reference/CANDIDATE_PROMOTION_DRY_RUN.md",
    "docs/architecture/CANDIDATE_PROMOTION_DRY_RUN_MODEL.md",
    "docs/operations/CANDIDATE_PROMOTION_DRY_RUN_REVIEW.md",
]

EXAMPLE_FILES = [
    "examples/review/candidate_promotion_dry_runs/minimal_promotion_dry_run_v0.json",
    "examples/review/candidate_promotion_dry_runs/ready_for_promotion_dry_run_v0.json",
    "examples/review/candidate_promotion_dry_runs/missing_evidence_promotion_dry_run_v0.json",
    "examples/review/candidate_promotion_dry_runs/conflict_blocked_promotion_dry_run_v0.json",
    "examples/review/candidate_promotion_dry_runs/duplicate_blocked_promotion_dry_run_v0.json",
    "examples/review/candidate_promotion_dry_runs/policy_blocked_promotion_dry_run_v0.json",
    "examples/review/candidate_promotion_dry_runs/rights_risk_blocked_promotion_dry_run_v0.json",
]

AUDIT_FILES = [
    "control/audits/track-b-19-candidate-promotion-dry-run-v0/README.md",
    "control/audits/track-b-19-candidate-promotion-dry-run-v0/track_b_19_report.json",
    "control/audits/track-b-19-candidate-promotion-dry-run-v0/validation.md",
    "control/audits/track-b-19-candidate-promotion-dry-run-v0/generated/sample_candidate_promotion_dry_run.json",
    "control/audits/track-b-19-candidate-promotion-dry-run-v0/generated/sample_candidate_promotion_summary.md",
]

SCRIPT_FILES = [
    "scripts/run_candidate_promotion_dry_run.py",
    "scripts/validate_candidate_promotion_dry_run.py",
]

RUNTIME_FILE = "runtime/local/foundry/candidate_promotion_dry_run.py"
SAMPLE_RECORD = "control/audits/track-b-19-candidate-promotion-dry-run-v0/generated/sample_candidate_promotion_dry_run.json"

FORBIDDEN_TEXT_TOKENS = [
    "api_key",
    "secret",
    "credential",
    "cookie",
    "account session",
    "live source access enabled",
    "source sync enabled",
    "hosted moderation enabled",
    "accepted evidence truth",
    "accepted public truth",
    "public index mutation allowed",
    "master index mutation allowed",
    "rights are cleared",
    "malware safety established",
    "verified installability",
    "production ready",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_files(paths: Iterable[str], errors: list[str]) -> None:
    for raw_path in paths:
        if not (REPO_ROOT / raw_path).exists():
            errors.append(f"missing required file: {raw_path}")


def require_values(label: str, actual: Iterable[str], expected: Iterable[str], errors: list[str]) -> None:
    actual_set = set(actual)
    expected_set = set(expected)
    missing = sorted(expected_set - actual_set)
    extra = sorted(actual_set - expected_set)
    if missing:
        errors.append(f"{label} missing values: {missing}")
    if extra:
        errors.append(f"{label} has unexpected values: {extra}")


def expect_false(mapping: Mapping[str, Any], field: str, label: str, errors: list[str]) -> None:
    if mapping.get(field) is not False:
        errors.append(f"{label}.{field} must be false")


def expect_true(mapping: Mapping[str, Any], field: str, label: str, errors: list[str]) -> None:
    if mapping.get(field) is not True:
        errors.append(f"{label}.{field} must be true")


def scan_forbidden_text(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8").lower()
    for token in FORBIDDEN_TEXT_TOKENS:
        if token in text:
            errors.append(f"{path.relative_to(REPO_ROOT).as_posix()} contains forbidden text token: {token}")


def validate_policies(errors: list[str]) -> None:
    policies: dict[str, Any] = {}
    for raw_path in POLICY_FILES:
        path = REPO_ROOT / raw_path
        if path.exists():
            try:
                policies[raw_path] = load_json(path)
            except json.JSONDecodeError as exc:
                errors.append(f"{raw_path} is not valid JSON: {exc}")

    runtime_policy = policies.get(POLICY_FILES[0], {})
    readiness_policy = policies.get(POLICY_FILES[1], {})
    blocker_policy = policies.get(POLICY_FILES[2], {})
    output_policy = policies.get(POLICY_FILES[3], {})
    path_policy = policies.get(POLICY_FILES[4], {})
    truth_policy = policies.get(POLICY_FILES[5], {})

    require_values("runtime.allowed_statuses", runtime_policy.get("allowed_statuses", []), promotion.ALLOWED_STATUSES, errors)
    require_values("runtime.allowed_readiness_values", runtime_policy.get("allowed_readiness_values", []), promotion.READINESS_VALUES, errors)
    require_values("runtime.allowed_blocker_categories", runtime_policy.get("allowed_blocker_categories", []), promotion.BLOCKER_CATEGORIES, errors)
    require_values("runtime.allowed_output_types", runtime_policy.get("allowed_output_types", []), promotion.ALLOWED_OUTPUT_TYPES, errors)
    require_values("runtime.forbidden_output_types", runtime_policy.get("forbidden_output_types", []), promotion.FORBIDDEN_OUTPUT_TYPES, errors)
    expect_true(runtime_policy, "promotion_dry_run_only", "runtime_policy", errors)

    require_values("readiness.allowed_readiness_values", readiness_policy.get("allowed_readiness_values", []), promotion.READINESS_VALUES, errors)
    for field in [
        "ready_value_is_public_truth",
        "ready_value_accepts_candidate",
        "ready_value_accepts_evidence",
        "ready_value_allows_public_index_mutation",
        "ready_value_allows_master_index_mutation",
    ]:
        expect_false(readiness_policy, field, "readiness_policy", errors)

    require_values("blocker.allowed_blocker_categories", blocker_policy.get("allowed_blocker_categories", []), promotion.BLOCKER_CATEGORIES, errors)
    for field in ["automatic_resolution_allowed", "automatic_merge_allowed", "automatic_delete_allowed"]:
        expect_false(blocker_policy, field, "blocker_policy", errors)

    require_values("output.allowed_output_types", output_policy.get("allowed_output_types", []), promotion.ALLOWED_OUTPUT_TYPES, errors)
    require_values("output.forbidden_output_types", output_policy.get("forbidden_output_types", []), promotion.FORBIDDEN_OUTPUT_TYPES, errors)
    expect_false(output_policy, "writes_public_index", "output_policy", errors)
    expect_false(output_policy, "writes_master_index", "output_policy", errors)

    allowed_roots = path_policy.get("allowed_output_roots", [])
    forbidden_roots = path_policy.get("forbidden_output_roots", [])
    if "control/audits/**/generated/" not in allowed_roots:
        errors.append("path policy must allow control/audits/**/generated/")
    for root in ["site/dist/", "runtime/", "contracts/", "public_index/", ".aide.local/", ".local/eureka/", ".cache/eureka/"]:
        if root not in forbidden_roots:
            errors.append(f"path policy must forbid {root}")

    truth = truth_policy.get("truth_boundary", {})
    for field in promotion.TRUTH_BOUNDARY_FALSE_FIELDS:
        expect_false(truth, field, "truth_policy.truth_boundary", errors)
    for field in promotion.TRUTH_BOUNDARY_TRUE_FIELDS:
        expect_true(truth, field, "truth_policy.truth_boundary", errors)
    for field in [
        "automatic_candidate_acceptance_allowed",
        "automatic_evidence_acceptance_allowed",
        "automatic_public_record_creation_allowed",
        "automatic_public_index_mutation_allowed",
        "automatic_master_index_mutation_allowed",
        "automatic_rights_clearance_allowed",
        "automatic_malware_safety_allowed",
        "automatic_installability_verification_allowed",
    ]:
        expect_false(truth_policy, field, "truth_policy", errors)


def validate_examples(errors: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    ids: set[str] = set()
    for raw_path in EXAMPLE_FILES:
        path = REPO_ROOT / raw_path
        if not path.exists():
            continue
        try:
            payload = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{raw_path} is not valid JSON: {exc}")
            continue
        scan_forbidden_text(path, errors)
        record = promotion.build_candidate_promotion_dry_run(payload)
        validation_errors = promotion.validate_candidate_promotion_dry_run(record)
        if validation_errors:
            errors.append(f"{raw_path} failed validation: {validation_errors}")
        record_id = str(record.get("promotion_dry_run_id", ""))
        if record_id in ids:
            errors.append(f"duplicate promotion_dry_run_id in examples: {record_id}")
        ids.add(record_id)
        records.append(record)
    return records


def run_command(args: list[str], errors: list[str]) -> None:
    completed = subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        errors.append("command failed: " + " ".join(args) + "\nstdout:\n" + completed.stdout + "\nstderr:\n" + completed.stderr)
        return
    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"command did not emit JSON: {' '.join(args)}: {exc}")
        return
    if parsed.get("status") not in {"pass", "PASS"}:
        errors.append(f"command did not report pass: {' '.join(args)}")


def validate_script_commands(errors: list[str]) -> None:
    run_command(
        [
            sys.executable,
            "scripts/run_candidate_promotion_dry_run.py",
            "--candidate",
            "examples/index/candidates/search_need_candidate_v0.json",
            "--review",
            "examples/review/queue_entries/candidate_needs_review_v0.json",
            "--check",
            "--json",
        ],
        errors,
    )


def validate_output_roots(errors: list[str]) -> None:
    allowed_audit = REPO_ROOT / "control/audits/track-b-19-candidate-promotion-dry-run-v0/generated/sample_candidate_promotion_dry_run.json"
    if not run_candidate_promotion_dry_run.output_path_allowed(allowed_audit):
        errors.append("audit generated output path should be allowed")
    with tempfile.TemporaryDirectory() as tmp:
        if not run_candidate_promotion_dry_run.output_path_allowed(Path(tmp) / "promotion.json"):
            errors.append("explicit temp output path should be allowed")
    for raw_path in [
        "site/dist/promotion.json",
        "runtime/promotion.json",
        "contracts/index/master/promotion.json",
        "control/inventory/publication/promotion.json",
        "public_index/promotion.json",
        "master_index/promotion.json",
        ".aide.local/eureka/promotion.json",
    ]:
        if run_candidate_promotion_dry_run.output_path_allowed(REPO_ROOT / raw_path):
            errors.append(f"forbidden output path allowed: {raw_path}")


def validate_boundary_guards(records: list[dict[str, Any]], errors: list[str]) -> None:
    if not records:
        return
    base = deepcopy(records[0])
    for field in promotion.TRUTH_BOUNDARY_FALSE_FIELDS:
        mutated = deepcopy(base)
        mutated.setdefault("truth_boundary", {})[field] = True
        validation_errors = promotion.validate_candidate_promotion_dry_run(mutated)
        if not validation_errors:
            errors.append(f"truth-boundary mutation was accepted: {field}")
    for field in promotion.PRODUCT_BOUNDARY_FALSE_FIELDS:
        mutated = deepcopy(base)
        mutated.setdefault("product_boundary", {})[field] = True
        validation_errors = promotion.validate_candidate_promotion_dry_run(mutated)
        if not validation_errors:
            errors.append(f"product-boundary mutation was accepted: {field}")
            break
    duplicate = deepcopy(base)
    duplicate["blockers"] = [
        {
            "blocker_id": "promotion_blocker.duplicate_uncertain.v0",
            "blocker_category": "duplicate_uncertain",
            "blocker_summary": "Duplicate marker.",
            "evidence_or_review_refs": [],
            "automatic_resolution_allowed": False,
            "automatic_merge_allowed": True,
            "automatic_delete_allowed": False,
        }
    ]
    if not promotion.validate_candidate_promotion_dry_run(duplicate):
        errors.append("automatic duplicate merge was accepted")


def validate_generated_samples(errors: list[str]) -> None:
    sample = REPO_ROOT / SAMPLE_RECORD
    if sample.exists():
        try:
            record = promotion.build_candidate_promotion_dry_run(load_json(sample))
        except json.JSONDecodeError as exc:
            errors.append(f"{SAMPLE_RECORD} is not valid JSON: {exc}")
            return
        validation_errors = promotion.validate_candidate_promotion_dry_run(record)
        if validation_errors:
            errors.append(f"{SAMPLE_RECORD} failed validation: {validation_errors}")


def validate_candidate_promotion_dry_run(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    if repo_root != REPO_ROOT:
        raise ValueError("validate_candidate_promotion_dry_run expects the repository root")
    errors: list[str] = []
    require_files([RUNTIME_FILE], errors)
    require_files(SCRIPT_FILES, errors)
    require_files(POLICY_FILES, errors)
    require_files(DOC_FILES, errors)
    require_files(EXAMPLE_FILES, errors)
    require_files(AUDIT_FILES, errors)
    validate_policies(errors)
    records = validate_examples(errors)
    validate_script_commands(errors)
    validate_output_roots(errors)
    validate_boundary_guards(records, errors)
    validate_generated_samples(errors)
    return {
        "schema_version": "candidate_promotion_dry_run_validation.v0",
        "status": "pass" if not errors else "fail",
        "checked_files": {
            "runtime": [RUNTIME_FILE],
            "scripts": sorted(SCRIPT_FILES),
            "policies": sorted(POLICY_FILES),
            "docs": sorted(DOC_FILES),
            "examples": sorted(EXAMPLE_FILES),
            "audit": sorted(AUDIT_FILES),
        },
        "example_count": len(records),
        "error_count": len(errors),
        "errors": sorted(errors),
    }


def main() -> int:
    report = validate_candidate_promotion_dry_run()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
