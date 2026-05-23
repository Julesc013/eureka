#!/usr/bin/env python3
"""Validate IA-04 Internet Archive evidence-ledger integration."""

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

from runtime.source.observation.internet_archive_evidence import (  # noqa: E402
    build_ia_evidence_candidate_records,
    load_default_ia_source_cache_records,
    load_ia_evidence_policy,
    validate_ia_evidence_candidate,
)
from scripts.validate_ia_fixture_replay import validate_ia_fixture_replay  # noqa: E402
from scripts.validate_ia_live_metadata_probe import validate_ia_live_metadata_probe  # noqa: E402
from scripts.validate_ia_metadata_policy import validate_ia_metadata_policy  # noqa: E402
from scripts.validate_ia_source_cache_write import validate_ia_source_cache_write  # noqa: E402


REQUIRED_FILES = (
    "control/policies/ia_evidence_ledger_policy.json",
    "control/inventory/ia_evidence_record_schema.json",
    "examples/evidence/ledger/dry_run/internet_archive_metadata/expected_evidence_candidates.json",
    "examples/evidence/ledger/dry_run/internet_archive_metadata/expected_evidence_boundary_report.json",
    "runtime/source/observation/internet_archive_evidence.py",
    "scripts/eureka_ia_evidence_ledger_write.py",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    _ = argv
    result = validate_ia_evidence_ledger_integration(REPO_ROOT)
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate_ia_evidence_ledger_integration(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    policy_result = validate_ia_metadata_policy(repo_root)
    fixture_result = validate_ia_fixture_replay(repo_root)
    live_result = validate_ia_live_metadata_probe(repo_root)
    source_cache_result = validate_ia_source_cache_write(repo_root)
    if policy_result.get("status") != "pass":
        errors.append("ia_00_policy_validator_failed")
    if fixture_result.get("status") != "pass":
        errors.append("ia_01_fixture_replay_validator_failed")
    if live_result.get("status") != "pass":
        errors.append("ia_02_live_probe_validator_failed")
    if source_cache_result.get("status") != "pass":
        errors.append("ia_03_source_cache_validator_failed")
    if not _ia03_passed(repo_root):
        errors.append("ia_03_pass_result_not_found")
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).exists():
            errors.append(f"missing_file:{rel_path}")

    policy = _load_json(repo_root / "control/policies/ia_evidence_ledger_policy.json", errors)
    _validate_policy(policy, errors)
    records = load_default_ia_source_cache_records()
    if not records:
        errors.append("source_cache_records_missing")
    candidates = build_ia_evidence_candidate_records(records[:2], policy) if records else []
    if not candidates:
        errors.append("evidence_candidates_missing")
    for candidate in candidates:
        errors.extend(validate_ia_evidence_candidate(candidate, policy))
    if any(candidate.get("accepted_truth") is True for candidate in candidates):
        errors.append("accepted_truth_created")
    if not all(candidate.get("review_required") is True for candidate in candidates):
        errors.append("candidate_without_review_required")

    dry_run = _run(
        [
            sys.executable,
            "scripts/eureka_ia_evidence_ledger_write.py",
            "--instance",
            str(Path(tempfile.gettempdir()) / "eureka-ia04-dry-run"),
            "--operator-token",
            "local-dev-token",
            "--from-source-cache",
            "--dry-run",
            "--json",
        ],
        repo_root,
    )
    if dry_run.returncode != 0:
        errors.append("evidence_dry_run_failed")
        warnings.append(dry_run.stderr.strip())
    else:
        _validate_cli_report(dry_run.stdout, expected_write=False, errors=errors)

    apply_result = _run_temp_apply(repo_root)
    if apply_result.get("status") != "pass":
        errors.append("temp_instance_evidence_apply_failed")
        warnings.extend(apply_result.get("warnings", []))

    _validate_no_forbidden_git_state(repo_root, errors, warnings)
    _validate_no_raw_response_commit(repo_root, errors)
    return {
        "schema_version": "ia_evidence_ledger_integration_validation.v0",
        "task": "IA-04",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": [item for item in warnings if item],
        "ia_00_policy_validated": policy_result.get("status") == "pass",
        "ia_01_fixture_replay_validated": fixture_result.get("status") == "pass",
        "ia_02_live_probe_validated": live_result.get("status") == "pass",
        "ia_03_source_cache_validated": source_cache_result.get("status") == "pass",
        "dry_run_passed": dry_run.returncode == 0,
        "temp_instance_evidence_write_passed": apply_result.get("status") == "pass",
        "fixture_evidence_written_to_temp": bool(apply_result.get("fixture_evidence_written_to_temp", False)),
        "live_preview_evidence_written_to_temp": bool(apply_result.get("live_preview_evidence_written_to_temp", False)),
        "all_evidence_requires_review": bool(apply_result.get("all_evidence_requires_review", False)) or all(
            candidate.get("review_required") is True for candidate in candidates
        ),
        "accepted_truth_created": False,
        "operator_instance_mutated": False,
        "instance_state_committed": False,
        "raw_response_committed": False,
        "evidence_ledger_write_performed": bool(apply_result.get("evidence_ledger_write_performed", False)),
        "evidence_ledger_write_scope": "temp_explicit_instance_only" if apply_result.get("status") == "pass" else "none",
        "candidate_index_mutated": False,
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
    with tempfile.TemporaryDirectory(prefix="eureka-ia04-") as tmp:
        instance = Path(tmp) / "instance"
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
        )
        last_stdout = ""
        for command in commands:
            completed = _run(command, repo_root)
            if completed.returncode != 0:
                warnings.append(completed.stderr.strip() or completed.stdout.strip())
                return {"status": "fail", "warnings": warnings}
            last_stdout = completed.stdout
        try:
            payload = json.loads(last_stdout)
        except json.JSONDecodeError as exc:
            return {"status": "fail", "warnings": [f"apply_json_decode_failed:{exc}"]}
        report = payload.get("write_report", {})
        boundary = payload.get("boundary_report", {})
        return {
            "status": "pass" if boundary.get("passed") is True and report.get("evidence_ledger_write_performed") is True else "fail",
            "warnings": warnings,
            "fixture_evidence_written_to_temp": bool(report.get("fixture_evidence_written_to_temp", False)),
            "live_preview_evidence_written_to_temp": bool(report.get("live_preview_evidence_written_to_temp", False)),
            "all_evidence_requires_review": bool(report.get("all_evidence_requires_review", False)),
            "evidence_ledger_write_performed": bool(report.get("evidence_ledger_write_performed", False)),
        }


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("schema_version") != "ia_evidence_ledger_policy.v0":
        errors.append("bad_ia_evidence_policy_schema")
    if policy.get("evidence_ledger_writes_enabled_for_IA_04") is not True:
        errors.append("evidence_writes_not_enabled_for_ia04")
    if policy.get("dry_run_default") is not True:
        errors.append("dry_run_default_not_true")
    if policy.get("explicit_apply_required") is not True:
        errors.append("explicit_apply_not_required")
    if policy.get("review_required") is not True:
        errors.append("review_required_not_true")
    for key in (
        "accepted_truth_enabled",
        "candidate_index_mutation_enabled",
        "reviewed_index_mutation_enabled",
        "master_index_mutation_enabled",
        "download_install_execute_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if policy.get(key) is not False:
            errors.append(f"policy_expected_false:{key}")


def _validate_cli_report(stdout: str, *, expected_write: bool, errors: list[str]) -> None:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"evidence_cli_invalid_json:{exc}")
        return
    report = payload.get("write_report", {})
    boundary = payload.get("boundary_report", {})
    if bool(report.get("evidence_ledger_write_performed", False)) is not expected_write:
        errors.append("evidence_cli_write_flag_mismatch")
    if boundary.get("passed") is not True:
        errors.append("evidence_cli_boundary_failed")
    for key in (
        "operator_instance_mutated",
        "instance_state_committed",
        "raw_response_committed",
        "accepted_truth_created",
        "candidate_index_mutated",
        "reviewed_index_mutated",
        "master_index_mutated",
        "download_performed",
        "upload_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
    ):
        if boundary.get(key) is not False:
            errors.append(f"evidence_boundary_forbidden_flag:{key}")


def _ia03_passed(repo_root: Path) -> bool:
    result_path = repo_root / "control/inventory/ia_03_result.json"
    if not result_path.exists():
        return False
    result = json.loads(result_path.read_text(encoding="utf-8"))
    return (
        result.get("status") == "pass"
        and result.get("source_cache_write_performed") is True
        and result.get("evidence_ledger_write_performed") is False
        and result.get("candidate_index_mutated") is False
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
            "runtime/search/quality",
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
