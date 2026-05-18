#!/usr/bin/env python3
"""Validate IA-03 Internet Archive source-cache write path."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.source_observation.internet_archive_source_cache import (  # noqa: E402
    build_ia_source_cache_record,
    load_fixture_normalized_records,
    load_ia_source_cache_policy,
    load_live_preview_records,
    validate_ia_source_cache_record,
)
from scripts.validate_ia_fixture_replay import validate_ia_fixture_replay  # noqa: E402
from scripts.validate_ia_live_metadata_probe import validate_ia_live_metadata_probe  # noqa: E402
from scripts.validate_ia_metadata_policy import validate_ia_metadata_policy  # noqa: E402


REQUIRED_FILES = (
    "control/policies/ia_source_cache_policy.json",
    "control/inventory/ia_source_cache_record_schema.json",
    "examples/source_cache/internet_archive_metadata/expected_source_cache_records.json",
    "examples/source_cache/internet_archive_metadata/expected_source_cache_boundary_report.json",
    "runtime/source_observation/internet_archive_source_cache.py",
    "scripts/eureka_ia_source_cache_write.py",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    _ = argv
    result = validate_ia_source_cache_write(REPO_ROOT)
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate_ia_source_cache_write(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    policy_result = validate_ia_metadata_policy(repo_root)
    fixture_result = validate_ia_fixture_replay(repo_root)
    live_result = validate_ia_live_metadata_probe(repo_root)
    if policy_result.get("status") != "pass":
        errors.append("ia_00_policy_validator_failed")
    if fixture_result.get("status") != "pass":
        errors.append("ia_01_fixture_replay_validator_failed")
    if live_result.get("status") != "pass":
        errors.append("ia_02_live_probe_validator_failed")
    if not _ia02_successful(repo_root):
        errors.append("ia_02_successful_live_probe_not_found")
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).exists():
            errors.append(f"missing_file:{rel_path}")

    policy = _load_json(repo_root / "control/policies/ia_source_cache_policy.json", errors)
    _validate_policy(policy, errors)
    fixture_records = load_fixture_normalized_records(repo_root / "examples/internet_archive_metadata")
    live_preview_records = load_live_preview_records(repo_root / "control/inventory/ia_02_tls_continue_normalized_preview.json")
    if not fixture_records:
        errors.append("fixture_records_missing")
    if not live_preview_records:
        errors.append("live_preview_records_missing")
    for source in fixture_records[:1] + live_preview_records[:1]:
        record = build_ia_source_cache_record(source, policy, live_probe_id="validator")
        errors.extend(validate_ia_source_cache_record(record, policy))

    dry_run = _run(
        [
            sys.executable,
            "scripts/eureka_ia_source_cache_write.py",
            "--instance",
            str(Path(tempfile.gettempdir()) / "eureka-ia03-dry-run"),
            "--operator-token",
            "local-dev-token",
            "--from-fixtures",
            "--dry-run",
            "--json",
        ],
        repo_root,
    )
    if dry_run.returncode != 0:
        errors.append("source_cache_dry_run_failed")
        warnings.append(dry_run.stderr.strip())
    else:
        _validate_cli_report(dry_run.stdout, expected_write=False, errors=errors)

    apply_result = _run_temp_apply(repo_root)
    if apply_result.get("status") != "pass":
        errors.append("temp_instance_apply_write_failed")
        warnings.extend(apply_result.get("warnings", []))

    _validate_no_forbidden_git_state(repo_root, errors, warnings)
    _validate_no_raw_response_commit(repo_root, errors)
    return {
        "schema_version": "ia_source_cache_write_validation.v0",
        "task": "IA-03",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": [item for item in warnings if item],
        "ia_00_policy_validated": policy_result.get("status") == "pass",
        "ia_01_fixture_replay_validated": fixture_result.get("status") == "pass",
        "ia_02_live_probe_validated": live_result.get("status") == "pass",
        "dry_run_passed": dry_run.returncode == 0,
        "temp_instance_write_passed": apply_result.get("status") == "pass",
        "fixture_records_written_to_temp": bool(apply_result.get("fixture_records_written_to_temp", False)),
        "live_preview_records_written_to_temp": bool(apply_result.get("live_preview_records_written_to_temp", False)),
        "operator_instance_mutated": False,
        "instance_state_committed": False,
        "raw_response_committed": False,
        "source_cache_write_performed": bool(apply_result.get("source_cache_write_performed", False)),
        "source_cache_write_scope": "temp_explicit_instance_only" if apply_result.get("status") == "pass" else "none",
        "evidence_ledger_write_performed": False,
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
    with tempfile.TemporaryDirectory(prefix="eureka-ia03-") as tmp:
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
            "status": "pass" if boundary.get("passed") is True and report.get("source_cache_write_performed") is True else "fail",
            "warnings": warnings,
            "fixture_records_written_to_temp": bool(report.get("fixture_records_written_to_temp", False)),
            "live_preview_records_written_to_temp": bool(report.get("live_preview_records_written_to_temp", False)),
            "source_cache_write_performed": bool(report.get("source_cache_write_performed", False)),
        }


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("schema_version") != "ia_source_cache_policy.v0":
        errors.append("bad_ia_source_cache_policy_schema")
    if policy.get("source_cache_writes_enabled_for_IA_03") is not True:
        errors.append("source_cache_writes_not_enabled_for_ia03")
    if policy.get("dry_run_default") is not True:
        errors.append("dry_run_default_not_true")
    if policy.get("explicit_apply_required") is not True:
        errors.append("explicit_apply_not_required")
    for key in (
        "evidence_ledger_writes_enabled",
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
        errors.append(f"source_cache_cli_invalid_json:{exc}")
        return
    report = payload.get("write_report", {})
    boundary = payload.get("boundary_report", {})
    if bool(report.get("source_cache_write_performed", False)) is not expected_write:
        errors.append("source_cache_cli_write_flag_mismatch")
    if boundary.get("passed") is not True:
        errors.append("source_cache_cli_boundary_failed")
    for key in (
        "raw_response_committed",
        "evidence_ledger_write_performed",
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
            errors.append(f"source_cache_boundary_forbidden_flag:{key}")


def _ia02_successful(repo_root: Path) -> bool:
    result_path = repo_root / "control/inventory/ia_02_result.json"
    if not result_path.exists():
        return False
    result = json.loads(result_path.read_text(encoding="utf-8"))
    return result.get("live_probe_succeeded") is True and result.get("raw_response_committed") is False


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
            "data/public_index",
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
