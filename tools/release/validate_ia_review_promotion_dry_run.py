#!/usr/bin/env python3
"""Validate IA-06 review queue and promotion dry-run integration."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.source_observation.internet_archive_promotion import (  # noqa: E402
    build_ia_promotion_previews,
    load_ia_promotion_dry_run_policy,
    validate_ia_promotion_preview,
)
from runtime.source_observation.internet_archive_review import (  # noqa: E402
    apply_ia_review_decision,
    build_ia_review_items_from_candidates,
    load_default_ia_candidate_records,
    load_ia_review_policy,
    validate_ia_review_decision,
    validate_ia_review_item,
)
from scripts.validate_ia_candidate_index_integration import validate_ia_candidate_index_integration  # noqa: E402
from scripts.validate_ia_evidence_ledger_integration import validate_ia_evidence_ledger_integration  # noqa: E402
from scripts.validate_ia_fixture_replay import validate_ia_fixture_replay  # noqa: E402
from scripts.validate_ia_live_metadata_probe import validate_ia_live_metadata_probe  # noqa: E402
from scripts.validate_ia_metadata_policy import validate_ia_metadata_policy  # noqa: E402
from scripts.validate_ia_source_cache_write import validate_ia_source_cache_write  # noqa: E402


REQUIRED_FILES = (
    "control/policies/ia_review_policy.json",
    "control/policies/ia_promotion_dry_run_policy.json",
    "control/inventory/ia_review_item_schema.json",
    "control/inventory/ia_review_decision_schema.json",
    "control/inventory/ia_promotion_preview_schema.json",
    "examples/review_queue/internet_archive_metadata/expected_review_items.json",
    "examples/review_queue/internet_archive_metadata/expected_review_decisions.json",
    "examples/review_queue/internet_archive_metadata/expected_promotion_preview.json",
    "examples/review_queue/internet_archive_metadata/expected_review_boundary_report.json",
    "runtime/source_observation/internet_archive_review.py",
    "runtime/source_observation/internet_archive_promotion.py",
    "scripts/eureka_ia_review_queue.py",
    "scripts/eureka_ia_promotion_dry_run.py",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    _ = argv
    result = validate_ia_review_promotion_dry_run(REPO_ROOT)
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate_ia_review_promotion_dry_run(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    policy_result = validate_ia_metadata_policy(repo_root)
    fixture_result = validate_ia_fixture_replay(repo_root)
    live_result = validate_ia_live_metadata_probe(repo_root)
    source_cache_result = validate_ia_source_cache_write(repo_root)
    evidence_result = validate_ia_evidence_ledger_integration(repo_root)
    candidate_result = validate_ia_candidate_index_integration(repo_root)
    if policy_result.get("status") != "pass":
        errors.append("ia_00_policy_validator_failed")
    if fixture_result.get("status") != "pass":
        errors.append("ia_01_fixture_replay_validator_failed")
    if live_result.get("status") != "pass":
        errors.append("ia_02_live_probe_validator_failed")
    if source_cache_result.get("status") != "pass":
        errors.append("ia_03_source_cache_validator_failed")
    if evidence_result.get("status") != "pass":
        errors.append("ia_04_evidence_validator_failed")
    if candidate_result.get("status") != "pass":
        errors.append("ia_05_candidate_validator_failed")
    if not _ia05_passed(repo_root):
        errors.append("ia_05_pass_result_not_found")
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).exists():
            errors.append(f"missing_file:{rel_path}")

    review_policy = _load_json(repo_root / "control/policies/ia_review_policy.json", errors)
    promotion_policy = _load_json(repo_root / "control/policies/ia_promotion_dry_run_policy.json", errors)
    _validate_review_policy(review_policy, errors)
    _validate_promotion_policy(promotion_policy, errors)

    candidates = load_default_ia_candidate_records()
    review_items = build_ia_review_items_from_candidates(candidates, review_policy) if candidates else []
    if not review_items:
        errors.append("review_items_missing")
    decisions = [apply_ia_review_decision(item, "approve_for_reviewed_index_dry_run", review_policy) for item in review_items]
    previews = build_ia_promotion_previews(decisions, promotion_policy)
    if not previews:
        errors.append("promotion_previews_missing")
    for item in review_items:
        errors.extend(validate_ia_review_item(item, review_policy))
    for decision in decisions:
        errors.extend(validate_ia_review_decision(decision, review_policy))
    for preview in previews:
        errors.extend(validate_ia_promotion_preview(preview, promotion_policy))

    dry_run = _run(
        [
            sys.executable,
            "scripts/eureka_ia_review_queue.py",
            "--instance",
            str(Path(tempfile.gettempdir()) / "eureka-ia06-dry-run"),
            "--from-candidate-index",
            "--decision",
            "approve_for_reviewed_index_dry_run",
            "--dry-run",
            "--json",
        ],
        repo_root,
    )
    if dry_run.returncode != 0:
        errors.append("review_queue_dry_run_failed")
        warnings.append(dry_run.stderr.strip())
    else:
        _validate_review_cli_report(dry_run.stdout, expected_write=False, errors=errors)

    apply_result = _run_temp_apply(repo_root)
    if apply_result.get("status") != "pass":
        errors.append("temp_instance_review_apply_failed")
        warnings.extend(apply_result.get("warnings", []))

    _validate_no_forbidden_git_state(repo_root, errors, warnings)
    _validate_no_raw_response_commit(repo_root, errors)
    return {
        "schema_version": "ia_review_promotion_dry_run_validation.v0",
        "task": "IA-06",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": [item for item in warnings if item],
        "ia_00_policy_validated": policy_result.get("status") == "pass",
        "ia_01_fixture_replay_validated": fixture_result.get("status") == "pass",
        "ia_02_live_probe_validated": live_result.get("status") == "pass",
        "ia_03_source_cache_validated": source_cache_result.get("status") == "pass",
        "ia_04_evidence_ledger_validated": evidence_result.get("status") == "pass",
        "ia_05_candidate_index_validated": candidate_result.get("status") == "pass",
        "dry_run_passed": dry_run.returncode == 0,
        "temp_instance_review_write_passed": apply_result.get("status") == "pass",
        "promotion_dry_run_passed": bool(apply_result.get("promotion_dry_run_passed", False)),
        "fixture_review_items_written_to_temp": bool(apply_result.get("fixture_review_items_written_to_temp", False)),
        "live_preview_review_items_written_to_temp": bool(apply_result.get("live_preview_review_items_written_to_temp", False)),
        "promotion_previews_created": bool(apply_result.get("promotion_previews_created", False)) or bool(previews),
        "all_promotion_previews_dry_run_only": bool(apply_result.get("all_promotion_previews_dry_run_only", False))
        or bool(apply_result.get("all_promotion_previews_preview_only", False))
        or all(
            preview.get("promotion_dry_run_only") is True or preview.get("preview_only") is True
            for preview in previews
        ),
        "accepted_truth_created": False,
        "operator_instance_mutated": False,
        "instance_state_committed": False,
        "raw_response_committed": False,
        "review_queue_mutated": bool(apply_result.get("review_queue_mutated", False)),
        "review_queue_write_scope": "temp_explicit_instance_only" if apply_result.get("status") == "pass" else "none",
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _run_temp_apply(repo_root: Path) -> dict[str, Any]:
    warnings: list[str] = []
    with tempfile.TemporaryDirectory(prefix="eureka-ia06-") as tmp:
        instance = Path(tmp) / "instance"
        review_output = Path(tmp) / "review_queue_result.json"
        review_boundary = Path(tmp) / "review_boundary_report.json"
        promotion_output = Path(tmp) / "promotion_dry_run_result.json"
        promotion_boundary = Path(tmp) / "promotion_boundary_report.json"
        commands = (
            [sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"],
            [sys.executable, "scripts/eureka_validate_instance.py", "--instance", str(instance), "--json"],
            [sys.executable, "scripts/eureka_set_operator_token.py", "--instance", str(instance), "--token", "local-dev-token", "--json"],
            [
                sys.executable,
                "scripts/eureka_ia_source_cache_write.py",
                "--instance",
                str(instance),
                "--operator-token",
                "local-dev-token",
                "--from-fixtures",
                "--from-live-preview",
                "control/inventory/ia_02_tls_continue_normalized_preview.json",
                "--apply",
                "--json",
            ],
            [
                sys.executable,
                "scripts/eureka_ia_evidence_ledger_write.py",
                "--instance",
                str(instance),
                "--operator-token",
                "local-dev-token",
                "--from-source-cache",
                "--apply",
                "--json",
            ],
            [
                sys.executable,
                "scripts/eureka_ia_candidate_index_write.py",
                "--instance",
                str(instance),
                "--operator-token",
                "local-dev-token",
                "--from-evidence-ledger",
                "--apply",
                "--json",
            ],
            [
                sys.executable,
                "scripts/eureka_ia_review_queue.py",
                "--instance",
                str(instance),
                "--operator-token",
                "local-dev-token",
                "--from-candidate-index",
                "--decision",
                "approve_for_reviewed_index_dry_run",
                "--apply",
                "--json",
                "--output",
                str(review_output),
                "--boundary-output",
                str(review_boundary),
            ],
            [
                sys.executable,
                "scripts/eureka_ia_promotion_dry_run.py",
                "--instance",
                str(instance),
                "--operator-token",
                "local-dev-token",
                "--from-review-decisions",
                "--from-review-report",
                str(review_output),
                "--json",
                "--output",
                str(promotion_output),
                "--boundary-output",
                str(promotion_boundary),
            ],
        )
        for command in commands:
            completed = _run(command, repo_root)
            if completed.returncode != 0:
                warnings.append(completed.stderr.strip() or completed.stdout.strip())
                return {"status": "fail", "warnings": warnings}
        try:
            review_report = json.loads(review_output.read_text(encoding="utf-8"))
            review_boundary_payload = json.loads(review_boundary.read_text(encoding="utf-8"))
            promotion_report = json.loads(promotion_output.read_text(encoding="utf-8"))
            promotion_boundary_payload = json.loads(promotion_boundary.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {"status": "fail", "warnings": [f"apply_json_decode_failed:{exc}"]}
        return {
            "status": "pass"
            if review_boundary_payload.get("passed") is True
            and promotion_boundary_payload.get("passed") is True
            and review_report.get("review_queue_mutated") is True
            else "fail",
            "warnings": warnings,
            "review_queue_mutated": bool(review_report.get("review_queue_mutated", False)),
            "fixture_review_items_written_to_temp": bool(review_report.get("fixture_review_items_written_to_temp", False)),
            "live_preview_review_items_written_to_temp": bool(review_report.get("live_preview_review_items_written_to_temp", False)),
            "promotion_dry_run_passed": promotion_boundary_payload.get("passed") is True,
            "promotion_previews_created": bool(promotion_report.get("promotion_previews_created", False)),
            "all_promotion_previews_dry_run_only": bool(promotion_report.get("all_promotion_previews_dry_run_only", False))
            or bool(promotion_report.get("all_promotion_previews_preview_only", False)),
        }


def _validate_review_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("schema_version") != "ia_review_policy.v0":
        errors.append("bad_ia_review_policy_schema")
    if policy.get("review_queue_writes_enabled_for_IA_06") is not True:
        errors.append("review_queue_writes_not_enabled_for_ia06")
    if policy.get("dry_run_default") is not True:
        errors.append("review_dry_run_default_not_true")
    if policy.get("explicit_apply_required") is not True:
        errors.append("review_explicit_apply_not_required")
    for key in (
        "accepted_truth_enabled",
        "reviewed_index_mutation_enabled",
        "master_index_mutation_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if policy.get(key) is not False:
            errors.append(f"review_policy_expected_false:{key}")


def _validate_promotion_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("schema_version") != "ia_promotion_dry_run_policy.v0":
        errors.append("bad_ia_promotion_policy_schema")
    if policy.get("promotion_dry_run_enabled") is not True:
        errors.append("promotion_dry_run_not_enabled")
    if policy.get("preview_only") is not True:
        errors.append("promotion_preview_only_not_true")
    for key in (
        "reviewed_index_write_enabled",
        "master_index_write_enabled",
        "accepted_truth_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if policy.get(key) is not False:
            errors.append(f"promotion_policy_expected_false:{key}")


def _validate_review_cli_report(stdout: str, *, expected_write: bool, errors: list[str]) -> None:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"review_cli_invalid_json:{exc}")
        return
    report = payload.get("review_report", {})
    boundary = payload.get("boundary_report", {})
    if bool(report.get("review_queue_mutated", False)) is not expected_write:
        errors.append("review_cli_write_flag_mismatch")
    if boundary.get("passed") is not True:
        errors.append("review_cli_boundary_failed")
    for key in (
        "operator_instance_mutated",
        "instance_state_committed",
        "raw_response_committed",
        "accepted_truth_created",
        "reviewed_index_mutated",
        "master_index_mutated",
        "download_performed",
        "upload_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
    ):
        if boundary.get(key) is not False:
            errors.append(f"review_boundary_forbidden_flag:{key}")


def _ia05_passed(repo_root: Path) -> bool:
    result_path = repo_root / "control/inventory/ia_05_result.json"
    if not result_path.exists():
        return False
    result = json.loads(result_path.read_text(encoding="utf-8"))
    return (
        result.get("status") == "pass"
        and result.get("candidate_index_mutated") is True
        and result.get("reviewed_index_mutated") is False
        and result.get("master_index_mutated") is False
    )


def _validate_no_raw_response_commit(repo_root: Path, errors: list[str]) -> None:
    for path in list((repo_root / "control/inventory").glob("ia_*live*preview*.json")) + list(
        (repo_root / "control/audits").glob("ia-*/generated/*.json")
    ):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        text = json.dumps(payload, sort_keys=True).lower()
        if "raw_response_body" in text or "response_body" in text:
            errors.append(f"raw_response_body_committed:{path.relative_to(repo_root).as_posix()}")


def _validate_no_forbidden_git_state(repo_root: Path, errors: list[str], warnings: list[str]) -> None:
    completed = _run(
        [
            "git",
            "status",
            "--short",
            "--",
            "eureka-instance",
            "instances",
            ".aide.local",
            "secrets",
            ".env",
            "site/dist/data/public_index",
            "runtime/connectors",
            "runtime/extraction",
            "runtime/search_quality",
            "native",
            "crates",
        ],
        repo_root,
    )
    if completed.returncode != 0:
        warnings.append("git_status_forbidden_paths_failed")
    elif completed.stdout.strip():
        errors.append("forbidden_path_modified:" + completed.stdout.strip().replace("\n", ";"))


def _load_json(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.exists():
        errors.append(f"missing_json:{path.relative_to(REPO_ROOT).as_posix()}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{path.relative_to(REPO_ROOT).as_posix()}:{exc}")
        return {}
    return payload if isinstance(payload, Mapping) else {}


def _run(command: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
