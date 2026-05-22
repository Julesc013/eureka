#!/usr/bin/env python3
"""Validate Workbench review/promotion-preview foundation."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]

POLICIES = {
    "control/policies/workbench_review_promote_policy.json",
    "control/policies/review_queue_operator_policy.json",
    "control/policies/promotion_preview_policy.json",
    "control/policies/reviewed_index_refresh_policy.json",
    "control/policies/workbench_review_promote_non_claim_policy.json",
}
MATRICES = {
    "control/inventory/workbench_review_promote_route_matrix.json",
    "control/inventory/workbench_review_promote_api_matrix.json",
    "control/inventory/workbench_review_promote_permission_matrix.json",
    "control/inventory/workbench_review_promote_state_matrix.json",
    "control/inventory/workbench_review_promote_event_matrix.json",
    "control/inventory/workbench_review_promote_candidate_matrix.json",
    "control/inventory/workbench_review_promote_decision_matrix.json",
    "control/inventory/workbench_review_promote_preview_matrix.json",
    "control/inventory/workbench_reviewed_index_refresh_matrix.json",
    "control/inventory/workbench_review_promote_boundary_report.json",
    "control/inventory/workbench_review_promote_smoke_result.json",
    "control/inventory/workbench_review_promote_validation_matrix.json",
    "control/inventory/workbench_review_promote_result.json",
    "control/inventory/workbench_review_promote_next_task_decision.json",
}
EXAMPLES = {
    "examples/workbench/review_promote/sample_candidate_input.json",
    "examples/workbench/review_promote/sample_review_item.json",
    "examples/workbench/review_promote/sample_review_decision.json",
    "examples/workbench/review_promote/sample_promotion_preview.json",
    "examples/workbench/review_promote/sample_reviewed_index_refresh_preview.json",
    "examples/workbench/review_promote/sample_reviewed_index_refresh_temp_result.json",
    "examples/workbench/review_promote/sample_boundary_report.json",
    "examples/workbench/review_promote/sample_public_blocked_projection.json",
    "examples/workbench/review_promote/sample_native_blocked_projection.json",
}
DOCS = {
    "docs/architecture/WORKBENCH_REVIEW_PROMOTE.md",
    "docs/architecture/REVIEW_TO_PROMOTION_PREVIEW_MODEL.md",
    "docs/architecture/REVIEWED_LOCAL_INDEX_REFRESH.md",
    "docs/operations/WORKBENCH_REVIEW_PROMOTE_RUNBOOK.md",
    "docs/operations/POST_WORKBENCH_REVIEW_PROMOTE_PLAN.md",
    "docs/reference/WORKBENCH_REVIEW_PROMOTE_ROUTES.md",
    "docs/reference/WORKBENCH_REVIEW_PROMOTE_API.md",
}
AUDIT_ROOT = Path("control/audits/workbench-review-promote-01-v0")
AUDIT_FILES = {
    "README.md",
    "workbench_review_promote_report.json",
    "route_matrix.md",
    "api_matrix.md",
    "permission_matrix.md",
    "state_matrix.md",
    "event_matrix.md",
    "candidate_matrix.md",
    "decision_matrix.md",
    "promotion_preview_matrix.md",
    "reviewed_index_refresh_matrix.md",
    "boundary_report.md",
    "smoke_result.md",
    "validation_matrix.md",
    "validation.md",
    "generated/sample_review_item.json",
    "generated/sample_review_decision.json",
    "generated/sample_promotion_preview.json",
    "generated/sample_reviewed_index_refresh_preview.json",
    "generated/sample_reviewed_index_refresh_temp_result.json",
    "generated/sample_boundary_report.json",
    "generated/sample_summary.md",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("Workbench review/promote validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    for rel in sorted(POLICIES | MATRICES | EXAMPLES | DOCS):
        require_file(root, rel, errors)
    for rel in sorted(AUDIT_FILES):
        require_file(root, (AUDIT_ROOT / rel).as_posix(), errors)
    payloads = {rel: load_json(root / rel, errors) for rel in sorted(POLICIES | MATRICES | EXAMPLES)}
    validate_policies(payloads, errors)
    validate_required_matrix_content(payloads, errors)
    validate_examples(payloads, errors)
    script_result = validate_script_commands(root, errors)
    result_payload = load_json(root / "control/inventory/workbench_review_promote_result.json", errors)
    boundary = load_json(root / "control/inventory/workbench_review_promote_boundary_report.json", errors)
    validate_result(result_payload, errors)
    validate_boundary(boundary, errors)
    status = "pass" if not errors else "fail"
    return {
        "schema_version": "workbench_review_promote_validation.v0",
        "task": "AIDE-BATCH-WORKBENCH-REVIEW-PROMOTE-01",
        "status": status,
        "errors": errors,
        "warnings": [],
        "script_checks": script_result,
        "policies_added": all((root / rel).is_file() for rel in POLICIES),
        "matrices_added": all((root / rel).is_file() for rel in MATRICES),
        "examples_added": all((root / rel).is_file() for rel in EXAMPLES),
        "docs_added": all((root / rel).is_file() for rel in DOCS),
        "operator_token_required": result_payload.get("operator_token_required") is True,
        "public_projection_blocked": result_payload.get("public_projection_blocked") is True,
        "native_read_only_projection_blocked": result_payload.get("native_read_only_projection_blocked") is True,
        "temp_reviewed_index_refresh_passed": result_payload.get("temp_reviewed_index_refresh_passed") is True,
        "temp_search_after_refresh_passed": result_payload.get("temp_search_after_refresh_passed") is True,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    combined: dict[str, Any] = {}
    for rel in POLICIES:
        combined.update(payloads.get(rel, {}))
    true_keys = (
        "review_requires_operator_token",
        "promotion_preview_is_not_promotion",
        "promotion_preview_requires_review_decision",
        "reviewed_index_refresh_allowed_only_temp_or_explicit_instance",
        "fake_evidence_forbidden",
        "fake_verified_records_forbidden",
    )
    false_keys = (
        "public_review_enabled",
        "native_review_enabled",
        "operator_instance_mutation_default",
        "master_index_mutation_enabled",
        "committed_data_public_index_mutation_enabled",
        "automatic_candidate_acceptance_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for key in true_keys:
        if combined.get(key) is not True:
            errors.append(f"policy must set {key}=true")
    for key in false_keys:
        if combined.get(key) is not False:
            errors.append(f"policy must set {key}=false")


def validate_required_matrix_content(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    route_text = json.dumps(payloads.get("control/inventory/workbench_review_promote_route_matrix.json", {}))
    for token in ("/review", "/promotion", "/api/v1/review", "/api/v1/promotion-preview", "/api/v1/reviewed-index/refresh-preview"):
        if token not in route_text:
            errors.append(f"route matrix missing {token}")
    event_text = json.dumps(payloads.get("control/inventory/workbench_review_promote_event_matrix.json", {}))
    for token in ("review.item_created", "review.decision_recorded", "promotion.preview_created", "reviewed_index.refresh_completed_temp"):
        if token not in event_text:
            errors.append(f"event matrix missing {token}")
    decision_text = json.dumps(payloads.get("control/inventory/workbench_review_promote_decision_matrix.json", {}))
    for token in ("accept_local_reviewed", "needs_more_evidence", "rights_risk", "defer"):
        if token not in decision_text:
            errors.append(f"decision matrix missing {token}")


def validate_examples(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    preview = payloads.get("examples/workbench/review_promote/sample_promotion_preview.json", {})
    if preview.get("promotion_preview_is_not_promotion") is not True:
        errors.append("sample promotion preview must be marked not promotion")
    temp = payloads.get("examples/workbench/review_promote/sample_reviewed_index_refresh_temp_result.json", {})
    if temp.get("temp_reviewed_index_refresh_passed") is not True or temp.get("temp_search_after_refresh_passed") is not True:
        errors.append("sample temp refresh result must pass refresh/search proof")
    for rel in ("examples/workbench/review_promote/sample_public_blocked_projection.json", "examples/workbench/review_promote/sample_native_blocked_projection.json"):
        payload = payloads.get(rel, {})
        if payload.get("review_decision", {}).get("allowed") is not False:
            errors.append(f"{rel} must block review decision")


def validate_script_commands(root: Path, errors: list[str]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    commands = {
        "help": ["python", "scripts/eureka_workbench_review_promote.py", "--help"],
        "dry_run": ["python", "scripts/eureka_workbench_review_promote.py", "--from-fixtures", "--decision", "accept_local_reviewed", "--dry-run", "--projection", "operator_workbench", "--json"],
        "public_blocked": ["python", "scripts/eureka_workbench_review_promote.py", "--from-fixtures", "--decision", "accept_local_reviewed", "--dry-run", "--projection", "public_web", "--json"],
        "native_blocked": ["python", "scripts/eureka_workbench_review_promote.py", "--from-fixtures", "--decision", "accept_local_reviewed", "--dry-run", "--projection", "native_desktop_read_only", "--json"],
        "temp_apply": ["python", "scripts/eureka_workbench_review_promote.py", "--from-fixtures", "--decision", "accept_local_reviewed", "--operator-token", "local-dev-token", "--use-temp-instance", "--apply-to-temp", "--projection", "operator_workbench", "--json"],
    }
    for label, command in commands.items():
        completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        checks[label] = completed.returncode == 0
        if completed.returncode != 0:
            errors.append(f"{label} command failed: {completed.stdout}{completed.stderr}")
            continue
        if label != "help":
            try:
                payload = json.loads(completed.stdout)
            except json.JSONDecodeError as exc:
                errors.append(f"{label} command did not emit JSON: {exc}")
                continue
            if label == "temp_apply" and payload.get("temp_reviewed_index_refresh_passed") is not True:
                errors.append("temp apply command did not pass temp refresh")
            if label == "public_blocked" and payload.get("public_projection_blocked") is not True:
                errors.append("public projection command was not blocked")
            if label == "native_blocked" and payload.get("native_read_only_projection_blocked") is not True:
                errors.append("native projection command was not blocked")
    return checks


def validate_result(payload: Mapping[str, Any], errors: list[str]) -> None:
    required_true = (
        "policies_added",
        "route_matrix_added",
        "api_matrix_added",
        "permission_matrix_added",
        "state_matrix_added",
        "event_matrix_added",
        "candidate_matrix_added",
        "decision_matrix_added",
        "promotion_preview_matrix_added",
        "reviewed_index_refresh_matrix_added",
        "runtime_review_flow_added",
        "workbench_projection_added",
        "cli_added",
        "examples_added",
        "docs_added",
        "validator_added",
        "tests_added",
        "review_item_created",
        "operator_token_required",
        "public_projection_blocked",
        "native_read_only_projection_blocked",
        "promotion_preview_created",
        "temp_reviewed_index_refresh_passed",
        "temp_search_after_refresh_passed",
    )
    required_false = (
        "automatic_candidate_acceptance_enabled",
        "fake_evidence_created",
        "fake_verified_records_created",
        "operator_instance_mutated",
        "master_index_mutated",
        "committed_data_public_index_mutated",
        "download_performed",
        "upload_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for key in required_true:
        if payload.get(key) is not True:
            errors.append(f"result must set {key}=true")
    for key in required_false:
        if payload.get(key) is not False:
            errors.append(f"result must set {key}=false")


def validate_boundary(payload: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "automatic_candidate_acceptance_enabled",
        "fake_evidence_created",
        "fake_verified_records_created",
        "operator_instance_mutated",
        "master_index_mutated",
        "committed_data_public_index_mutated",
        "download_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if payload.get(key) is not False:
            errors.append(f"boundary must set {key}=false")


def require_file(root: Path, rel: str, errors: list[str]) -> None:
    path = root / rel
    if not path.is_file():
        errors.append(f"missing file: {rel}")
    elif path.stat().st_size == 0:
        errors.append(f"empty file: {rel}")


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {path.relative_to(REPO_ROOT).as_posix() if path.is_absolute() else path.as_posix()}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON file must contain object: {path}")
        return {}
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
