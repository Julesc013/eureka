#!/usr/bin/env python3
"""Validate the local review queue runtime milestone."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_foundry import review_queue
from scripts import record_review_queue


POLICY_FILES = [
    "control/inventory/review/local_review_queue_runtime_policy.json",
    "control/inventory/review/local_review_queue_entry_status_policy.json",
    "control/inventory/review/local_review_queue_subject_policy.json",
    "control/inventory/review/local_review_queue_decision_policy.json",
    "control/inventory/review/local_review_queue_output_policy.json",
    "control/inventory/review/local_review_queue_path_policy.json",
    "control/inventory/review/local_review_queue_truth_policy.json",
]

DOC_FILES = [
    "docs/reference/LOCAL_REVIEW_QUEUE_RUNTIME.md",
    "docs/architecture/LOCAL_REVIEW_QUEUE_MODEL.md",
    "docs/operations/LOCAL_REVIEW_QUEUE_REVIEW.md",
]

EXAMPLE_FILES = [
    "examples/review_queue_entries/minimal_review_queue_entry_v0.json",
    "examples/review_queue_entries/candidate_needs_review_v0.json",
    "examples/review_queue_entries/evidence_candidate_needs_review_v0.json",
    "examples/review_queue_entries/source_cache_record_needs_review_v0.json",
    "examples/review_queue_entries/source_cache_bridge_needs_review_v0.json",
    "examples/review_queue_entries/workunit_result_review_v0.json",
    "examples/review_queue_entries/duplicate_review_entry_v0.json",
    "examples/review_queue_entries/reject_review_entry_v0.json",
    "examples/review_queue_entries/request_more_evidence_review_entry_v0.json",
    "examples/review_queue_entries/policy_blocked_review_entry_v0.json",
]

AUDIT_FILES = [
    "control/audits/track-b-18-local-review-queue-runtime-v0/README.md",
    "control/audits/track-b-18-local-review-queue-runtime-v0/track_b_18_report.json",
    "control/audits/track-b-18-local-review-queue-runtime-v0/validation.md",
    "control/audits/track-b-18-local-review-queue-runtime-v0/generated/sample_review_queue_entry.json",
    "control/audits/track-b-18-local-review-queue-runtime-v0/generated/sample_review_queue_summary.md",
]

SCRIPT_FILES = [
    "scripts/record_review_queue.py",
    "scripts/summarize_review_queue.py",
    "scripts/validate_local_review_queue_runtime.py",
]

RUNTIME_FILE = "runtime/local_foundry/review_queue.py"

SAMPLE_ENTRY = (
    "control/audits/track-b-18-local-review-queue-runtime-v0/"
    "generated/sample_review_queue_entry.json"
)

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
    "master index mutation allowed",
    "rights are cleared",
    "malware safety established",
    "verified installability",
    "production ready",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def require_files(paths: Iterable[str], errors: list[str]) -> None:
    for raw_path in paths:
        path = REPO_ROOT / raw_path
        if not path.exists():
            errors.append(f"missing required file: {raw_path}")


def require_values(
    label: str,
    actual: Iterable[str],
    expected: Iterable[str],
    errors: list[str],
) -> None:
    actual_set = set(actual)
    expected_set = set(expected)
    missing = sorted(expected_set - actual_set)
    extra = sorted(actual_set - expected_set)
    if missing:
        errors.append(f"{label} missing values: {missing}")
    if extra:
        errors.append(f"{label} has unexpected values: {extra}")


def expect_bool_false(mapping: Mapping[str, Any], field: str, label: str, errors: list[str]) -> None:
    if mapping.get(field) is not False:
        errors.append(f"{label}.{field} must be false")


def expect_bool_true(mapping: Mapping[str, Any], field: str, label: str, errors: list[str]) -> None:
    if mapping.get(field) is not True:
        errors.append(f"{label}.{field} must be true")


def scan_forbidden_text(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    for token in FORBIDDEN_TEXT_TOKENS:
        if token in lowered:
            errors.append(f"{rel(path)} contains forbidden text token: {token}")


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
    status_policy = policies.get(POLICY_FILES[1], {})
    subject_policy = policies.get(POLICY_FILES[2], {})
    decision_policy = policies.get(POLICY_FILES[3], {})
    output_policy = policies.get(POLICY_FILES[4], {})
    path_policy = policies.get(POLICY_FILES[5], {})
    truth_policy = policies.get(POLICY_FILES[6], {})

    require_values(
        "runtime_policy.allowed_statuses",
        runtime_policy.get("allowed_statuses", []),
        review_queue.ALLOWED_STATUSES,
        errors,
    )
    require_values(
        "runtime_policy.allowed_subject_types",
        runtime_policy.get("allowed_subject_types", []),
        review_queue.ALLOWED_SUBJECT_TYPES,
        errors,
    )
    require_values(
        "runtime_policy.allowed_decisions",
        runtime_policy.get("allowed_decisions", []),
        review_queue.ALLOWED_DECISIONS,
        errors,
    )
    require_values(
        "runtime_policy.allowed_output_types",
        runtime_policy.get("allowed_output_types", []),
        review_queue.ALLOWED_OUTPUT_TYPES,
        errors,
    )
    require_values(
        "runtime_policy.forbidden_output_types",
        runtime_policy.get("forbidden_output_types", []),
        review_queue.FORBIDDEN_OUTPUT_TYPES,
        errors,
    )

    for field in [
        "review_required_before_downstream_use",
        "public_review_disabled_current",
        "hosted_moderation_disabled_current",
        "evidence_acceptance_disabled_current",
        "candidate_acceptance_disabled_current",
        "public_index_use_disabled_current",
        "master_index_mutation_disabled_current",
    ]:
        expect_bool_true(runtime_policy, field, "runtime_policy", errors)

    product_boundary = runtime_policy.get("product_boundary", {})
    for field in review_queue.PRODUCT_BOUNDARY_FALSE_FIELDS:
        expect_bool_false(product_boundary, field, "runtime_policy.product_boundary", errors)

    require_values(
        "status_policy.allowed_statuses",
        status_policy.get("allowed_statuses", []),
        review_queue.ALLOWED_STATUSES,
        errors,
    )
    require_values(
        "status_policy.current_allowed_statuses",
        status_policy.get("current_allowed_statuses", []),
        review_queue.CURRENT_ALLOWED_STATUSES,
        errors,
    )
    if "accepted_public_future" not in status_policy.get("statuses_forbidden_current", []):
        errors.append("accepted_public_future must be forbidden current status")

    require_values(
        "subject_policy.allowed_subject_types",
        subject_policy.get("allowed_subject_types", []),
        review_queue.ALLOWED_SUBJECT_TYPES,
        errors,
    )
    require_values(
        "decision_policy.allowed_decisions",
        decision_policy.get("allowed_decisions", []),
        review_queue.ALLOWED_DECISIONS,
        errors,
    )
    require_values(
        "decision_policy.current_allowed_decisions",
        decision_policy.get("current_allowed_decisions", []),
        review_queue.CURRENT_ALLOWED_DECISIONS,
        errors,
    )
    if "accept_public_future" not in decision_policy.get("decisions_forbidden_current", []):
        errors.append("accept_public_future must be forbidden current decision")

    require_values(
        "output_policy.allowed_output_types",
        output_policy.get("allowed_output_types", []),
        review_queue.ALLOWED_OUTPUT_TYPES,
        errors,
    )
    require_values(
        "output_policy.forbidden_output_types",
        output_policy.get("forbidden_output_types", []),
        review_queue.FORBIDDEN_OUTPUT_TYPES,
        errors,
    )

    allowed_roots = path_policy.get("allowed_output_roots", [])
    forbidden_roots = path_policy.get("forbidden_output_roots", [])
    if "control/audits/**/generated/" not in allowed_roots:
        errors.append("path policy must allow control/audits/**/generated/")
    for root in ["site/dist/", "runtime/", ".aide.local/", ".local/eureka/", ".cache/eureka/"]:
        if root not in forbidden_roots:
            errors.append(f"path policy must forbid {root}")

    for field in [
        "automatic_evidence_acceptance_allowed",
        "automatic_candidate_acceptance_allowed",
        "automatic_public_index_use_allowed",
        "automatic_master_index_mutation_allowed",
        "automatic_rights_clearance_allowed",
        "automatic_malware_safety_allowed",
        "automatic_installability_verification_allowed",
    ]:
        expect_bool_false(truth_policy, field, "truth_policy", errors)


def validate_examples(errors: list[str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    ids: set[str] = set()
    for raw_path in EXAMPLE_FILES:
        path = REPO_ROOT / raw_path
        if not path.exists():
            continue
        try:
            entry = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{raw_path} is not valid JSON: {exc}")
            continue
        scan_forbidden_text(path, errors)
        built = review_queue.build_review_queue_entry(entry)
        validation_errors = review_queue.validate_review_queue_entry(built)
        if validation_errors:
            errors.append(f"{raw_path} failed validation: {validation_errors}")
        entry_id = built.get("review_entry_id")
        if entry_id in ids:
            errors.append(f"duplicate review_entry_id in examples: {entry_id}")
        ids.add(str(entry_id))
        entries.append(built)
    return entries


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
        errors.append(
            "command failed: "
            + " ".join(args)
            + "\nstdout:\n"
            + completed.stdout
            + "\nstderr:\n"
            + completed.stderr
        )
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
            "scripts/record_review_queue.py",
            "--input",
            "examples/review_queue_entries/candidate_needs_review_v0.json",
            "--check",
            "--json",
        ],
        errors,
    )
    run_command(
        [
            sys.executable,
            "scripts/summarize_review_queue.py",
            "--input",
            "examples/review_queue_entries",
            "--check",
            "--json",
        ],
        errors,
    )


def validate_output_roots(errors: list[str]) -> None:
    allowed_audit = REPO_ROOT / (
        "control/audits/track-b-18-local-review-queue-runtime-v0/"
        "generated/sample_review_queue_entry.json"
    )
    if not record_review_queue.output_path_allowed(allowed_audit):
        errors.append("audit generated output path should be allowed")

    with tempfile.TemporaryDirectory() as tmp:
        if not record_review_queue.output_path_allowed(Path(tmp) / "review.json"):
            errors.append("explicit temp output path should be allowed")

    for raw_path in [
        "site/dist/review.json",
        "runtime/review.json",
        "contracts/master_index/review.json",
        "control/inventory/publication/review.json",
        ".aide.local/eureka/review.json",
    ]:
        if record_review_queue.output_path_allowed(REPO_ROOT / raw_path):
            errors.append(f"forbidden output path allowed: {raw_path}")


def validate_boundary_guards(entries: list[dict[str, Any]], errors: list[str]) -> None:
    if not entries:
        return
    base = deepcopy(entries[1] if len(entries) > 1 else entries[0])

    for field in [
        "review_entry_is_public_truth",
        "review_entry_accepts_evidence",
        "review_entry_accepts_candidate",
        "review_entry_mutates_master_index",
        "review_entry_allows_public_index_mutation",
        "review_entry_can_claim_rights_clearance",
        "review_entry_can_claim_malware_safety",
        "review_entry_can_claim_verified_installability",
        "review_entry_can_claim_exhaustive_global_search",
    ]:
        mutated = deepcopy(base)
        mutated.setdefault("truth_boundary", {})[field] = True
        validation_errors = review_queue.validate_review_queue_entry(mutated)
        if not validation_errors:
            errors.append(f"truth-boundary mutation was accepted: {field}")

    for field in review_queue.PRODUCT_BOUNDARY_FALSE_FIELDS:
        mutated = deepcopy(base)
        mutated.setdefault("product_boundary", {})[field] = True
        validation_errors = review_queue.validate_review_queue_entry(mutated)
        if not validation_errors:
            errors.append(f"product-boundary mutation was accepted: {field}")
            break

    missing = deepcopy(base)
    missing["review_entry_status"] = "request_more_evidence"
    missing["review_decision"] = "request_more_evidence"
    missing["missing_evidence"] = []
    validation_errors = review_queue.validate_review_queue_entry(missing)
    if not validation_errors:
        errors.append("request_more_evidence without missing_evidence was accepted")

    duplicate = deepcopy(base)
    duplicate["review_entry_status"] = "duplicate_possible"
    duplicate["review_decision"] = "mark_duplicate_possible"
    duplicate["duplicate_summary"] = {"duplicate_possible": True, "automatic_merge_allowed": True}
    validation_errors = review_queue.validate_review_queue_entry(duplicate)
    if not validation_errors:
        errors.append("automatic duplicate merge was accepted")

    conflict = deepcopy(base)
    conflict["review_entry_status"] = "conflict_detected"
    conflict["review_decision"] = "preserve_conflict"
    conflict["conflict_summary"] = {
        "conflict_detected": True,
        "automatic_conflict_resolution_allowed": True,
    }
    validation_errors = review_queue.validate_review_queue_entry(conflict)
    if not validation_errors:
        errors.append("automatic conflict resolution was accepted")


def validate_generated_samples(errors: list[str]) -> None:
    sample = REPO_ROOT / SAMPLE_ENTRY
    if sample.exists():
        try:
            entry = load_json(sample)
        except json.JSONDecodeError as exc:
            errors.append(f"{SAMPLE_ENTRY} is not valid JSON: {exc}")
            return
        validation_errors = review_queue.validate_review_queue_entry(entry)
        if validation_errors:
            errors.append(f"{SAMPLE_ENTRY} failed validation: {validation_errors}")


def validate_local_review_queue_runtime(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    if repo_root != REPO_ROOT:
        raise ValueError("validate_local_review_queue_runtime expects the repository root")
    errors: list[str] = []
    require_files([RUNTIME_FILE], errors)
    require_files(SCRIPT_FILES, errors)
    require_files(POLICY_FILES, errors)
    require_files(DOC_FILES, errors)
    require_files(EXAMPLE_FILES, errors)
    require_files(AUDIT_FILES, errors)

    validate_policies(errors)
    entries = validate_examples(errors)
    validate_script_commands(errors)
    validate_output_roots(errors)
    validate_boundary_guards(entries, errors)
    validate_generated_samples(errors)

    return {
        "schema_version": "local_review_queue_runtime_validation.v0",
        "status": "pass" if not errors else "fail",
        "checked_files": {
            "runtime": [RUNTIME_FILE],
            "scripts": sorted(SCRIPT_FILES),
            "policies": sorted(POLICY_FILES),
            "docs": sorted(DOC_FILES),
            "examples": sorted(EXAMPLE_FILES),
            "audit": sorted(AUDIT_FILES),
        },
        "example_count": len(entries),
        "error_count": len(errors),
        "errors": sorted(errors),
    }


def main() -> int:
    report = validate_local_review_queue_runtime()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
